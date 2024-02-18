import os.path

import torch
from torch.utils.data import DataLoader
from collections import OrderedDict
import torch.optim as optim
import torch.nn as nn
from .detection_utils import *
from .utils import *


class TorchChecks:
    def __init__(self, **kwargs):
        validate_kwargs(
            kwargs,
            {
                "model",
                "model_name",
                "model_type",
                "category",
                "message",
                "progress_bar",
                "image_size",
                "batch_size",
                "classes",
                "tmp_path",
            },
        )
        self.message = kwargs["message"]
        self.model = kwargs["model"]
        self.model_name = kwargs["model_name"]
        self.model_type = kwargs["model_type"]
        self.category = kwargs["category"]
        self.progress_bar = kwargs["progress_bar"]
        self.image_size = kwargs["image_size"]
        self.batch_size = kwargs["batch_size"]
        self.classes = kwargs["classes"]
        self.tmp_path = kwargs["tmp_path"]
        self.average_weights_file_path = None
        self.criterion = None
        self.loss = None

    def is_model_supported(self):
        """
        Check if model contains:
            - forward function
        """
        model = self.model
        self.progress_bar.update(1)
        if not hasattr(model, "forward"):
            self.message = "\nModel file not provided as per docs: forward function not found in  Model"
            raise Exception("forward func missing")

    def collate_fn(self, batch):
        """
        Custom collate function for handling varying sizes of tensors and different numbers of objects
        in images during data loading.

        Args:
            batch (list): A batch of data.

        Returns:
            Tuple: Collated batch of data.
        """
        return tuple(zip(*batch))

    def small_training_loop(self, weight_filename, custom_loss=False):
        try:
            # Define the number of fake images and other properties
            # Create fake image data
            train_dataset = dummy_dataset_pytorch(
                image_size=self.image_size,
                num_classes=self.classes,
                category=self.category,
                model_type=self.model_type,
                tmp_path=self.tmp_path,
            )

            train_loader = DataLoader(
                train_dataset, batch_size=self.batch_size, shuffle=True
            )

            # train_loader, classes = mock_torch_data(self.tmp_path)
            if self.criterion is not None:
                self.get_loss_function(custom_loss)

            if self.category == CLASSIFICATION:
                self.classification_training(train_loader)
            elif self.model_type == YOLO:
                self.yolo_training(train_loader)
            elif self.model_type == RCNN:
                self.rcnn_training(train_loader)
            else:
                # Raise an exception for unsupported models
                raise Exception("Unsupported model")

            # dump weights from trained model will be used in averaging check
            get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_path,
                    weights_file_name=TRAINED_WEIGHTS_FILENAME,
                    framework=PYTORCH_FRAMEWORK,
                    preweights=False,
                )
            if self.progress_bar is not None:
                self.progress_bar.update(1)
        except Exception as e:  # pragma: no cover
            self.message = f"\nModel not support training on image classification dataset as there is error {e} "
            raise

    def resize_weight_arrays(self, weights_list_tuple):
        # Find the maximum shape among all weight arrays in the tuple
        max_shape = np.array(max(w.shape for w in weights_list_tuple))

        # Broadcast each weight array to the maximum shape
        resized_weights_list = []
        for w in weights_list_tuple:
            if w.shape == ():
                # Convert 0-dimensional array to 1-dimensional array
                broadcasted_w = np.broadcast_to(w, (1,))
            else:
                broadcasted_w = np.broadcast_to(w, max_shape)
            resized_weights_list.append(broadcasted_w)

        return resized_weights_list

    def average_weights(self):
        weights = []
        new_weights = []
        no_images_array = [100, 100]
        weights_file_path_1 = os.path.join(
            self.tmp_path, f"{PRETRAINED_WEIGHTS_FILENAME}.pkl"
        )
        weights_file_path_2 = os.path.join(
            self.tmp_path, f"{TRAINED_WEIGHTS_FILENAME}.pkl"
        )
        self.average_weights_file_path = os.path.join(
            self.tmp_path, f"{AVERAGED_WEIGHTS_PATH}.pkl"
        )
        try:
            with open(weights_file_path_1, "rb") as pkl_file, open(
                weights_file_path_2, "rb"
            ) as pkl_file2:
                weights.append(pickle.load(pkl_file))
                weights.append(pickle.load(pkl_file2))
        except Exception as e:
            raise
        try:
            new_weights = [
                np.array(
                    [
                        np.average(np.array(w), weights=no_images_array, axis=0)
                        for w in zip(*self.resize_weight_arrays(weights_list_tuple))
                    ]
                )
                for weights_list_tuple in zip(*weights)
            ]
            del weights
            del no_images_array
        except Exception as e:
            raise
        try:
            with open(self.average_weights_file_path, "wb") as f:
                pickle.dump(new_weights, f)
            del new_weights
            self.progress_bar.update(1)
        except Exception as e:
            raise e

    def load_averaged_weights(self):
        try:
            with open(self.average_weights_file_path, "rb") as f:
                parameters = pickle.load(f)
            params_dict = zip(self.model.state_dict().keys(), parameters)
            state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
            self.model.load_state_dict(state_dict, strict=True)
            self.progress_bar.update(1)
            del params_dict
            del state_dict
            del parameters
        except Exception as e:
            raise

    def get_loss_function(self, custom_loss=False):
        if self.category == CLASSIFICATION:
            self.criterion = nn.CrossEntropyLoss()
        if custom_loss or self.category == DETECTION:
            try:
                import sys

                sys.path.append(self.tmp_path)
                if os.path.exists(os.path.join(self.tmp_path, "loss.py")):
                    from loss import Custom_loss

                    self.criterion = Custom_loss
                    self.loss = self.criterion
                else:
                    raise Exception(
                        "loss.py file missing in the zip.\n Please refer docs for more information."
                    )
            except Exception as e:
                raise e
        self.progress_bar.update(1)

    def yolo_training(self, train_loader):
        total_correct = 0
        total_samples = 0
        for epoch in range(1):  # loop over the dataset multiple times
            running_loss = 0.0
            for i, data in enumerate(train_loader, 0):
                # get the inputs; data is a list of [inputs, labels]
                inputs, labels = data
                labels = torch.tensor(labels, dtype=torch.long)

                # forward + backward + optimize
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                all_correct_pred_boxes, all_true_boxes, all_pred_boxes = get_bboxes(
                    loader=train_loader,
                    model=self.model,
                    iou_threshold=0.4,
                    threshold=0.4,
                    C=self.classes,
                )
                total_correct += len(
                    all_correct_pred_boxes
                )  # Accumulate correct predictions
                total_samples += len(
                    all_pred_boxes
                )  # Accumulate total number of samples

    def classification_training(self, train_loader):
        optimizer = optim.SGD(self.model.parameters(), lr=0.001, momentum=0.9)
        for epoch in range(1):  # loop over the dataset multiple times
            running_loss = 0.0
            for i, data in enumerate(train_loader, 0):
                # get the inputs; data is a list of [inputs, labels]
                inputs, labels = data
                labels = torch.tensor(labels, dtype=torch.long)
                # zero the parameter gradients
                optimizer.zero_grad()

                # forward + backward + optimize
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                # print statistics
                running_loss += loss.item()

    def rcnn_training(self, train_loader):
        for epoch in range(1):  # loop over the dataset multiple times
            running_loss = 0.0
            for i, data in enumerate(train_loader, 0):
                # get the inputs; data is a list of [inputs, labels]
                images, targets = data
                targets = torch.tensor(targets, dtype=torch.long)

                loss_dict = self.model(
                    images, targets
                )  # Get model predictions and compute loss
                losses = sum(
                    loss for loss in loss_dict.values()
                )  # Aggregate the losses

    def model_func_checks(self):
        # check if model is eligible
        try:
            self.is_model_supported()
            self.get_loss_function()
            self.small_training_loop(TRAINED_WEIGHTS_FILENAME)
            if os.path.exists(
                os.path.join(self.tmp_path, f"{PRETRAINED_WEIGHTS_FILENAME}.pth")
            ):
                get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_path,
                    weights_file_name=PRETRAINED_WEIGHTS_FILENAME,
                    framework=PYTORCH_FRAMEWORK,
                    preweights=True,
                )
                self.progress_bar.update(1)
            else:
                get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_path,
                    weights_file_name=PRETRAINED_WEIGHTS_FILENAME,
                    framework=PYTORCH_FRAMEWORK,
                    preweights=False,
                )
                self.progress_bar.update(1)
            self.average_weights()
            self.load_averaged_weights()
            self.message = "all check passed"
            eligible = True
        except Exception as e:  # pragma: no cover
            self.message = f"\nModel checks failed with error:\n {e}"
            eligible = False
        if not eligible:
            return eligible, self.message, None, self.progress_bar  # pragma: no cover
        return eligible, self.message, self.model_name, self.progress_bar
