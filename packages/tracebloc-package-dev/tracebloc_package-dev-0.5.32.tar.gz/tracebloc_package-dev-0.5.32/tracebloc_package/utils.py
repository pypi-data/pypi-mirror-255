import tensorflow_datasets as tfds
import tensorflow as tf
import torch
import torchvision
import torchvision.transforms as transforms
import numpy as np
from tensorflow_datasets.testing import mock_data
import torchvision.datasets as datasets
from torch.utils.data import Dataset, DataLoader
from PIL import Image, ImageDraw
from importlib.machinery import SourceFileLoader
import base64
import os
import ast
import pickle
import pickletools
import random

MODEL_PARAMS_LIMIT = 300000000
TENSORFLOW_FRAMEWORK = "tensorflow"
PYTORCH_FRAMEWORK = "pytorch"
CLASSIFICATION = "classification"
DETECTION = "detection"
YOLO = "yolo"
RCNN = "rcnn"
CONSTANT = "constant"
STANDARD = "standard"
ADAPTIVE = "adaptive"
CUSTOM = "custom"
TYPE = "type"
FUNCTION = "function"
VALUE = "value"
PRETRAINED_WEIGHTS_FILENAME = "pretrained_weights"
TRAINED_WEIGHTS_FILENAME = "trained_weights"
AVERAGED_WEIGHTS_PATH = "averaged"
SUCCESS = "success"
TORCH_HUB_PATTERN = "torch.hub"


class FakeObjectDetectionDataset(Dataset):
    def __init__(self, num_samples, num_classes=None, image_shape=(256, 256)):
        self.num_samples = num_samples
        self.num_classes = num_classes if num_classes else random.randint(1, 10)
        self.classes = [self._generate_class_name() for _ in range(self.num_classes)]
        self.image_shape = image_shape
        self.data = self._generate_fake_data()

    def _generate_class_name(self):
        # Generate a random class name
        return "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(5))

    def _generate_fake_data(self):
        data = []
        for _ in range(self.num_samples):
            image = torch.rand((3, *self.image_shape))  # Fake image data
            num_objects = random.randint(1, 5)
            labels = [
                random.randint(0, self.num_classes - 1) for _ in range(num_objects)
            ]
            boxes = [
                (random.random(), random.random(), random.random(), random.random())
                for _ in range(num_objects)
            ]
            target = {"boxes": boxes, "labels": labels}
            data.append((image, target))
        return data

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return self.data[idx]

    def __iter__(self):
        return iter(self.data)

    def get_classes(self):
        return self.classes


def check_MyModel(filename, path):
    try:
        # check if file contains the MyModel function
        model = SourceFileLoader(filename, f"{path}").load_module()
        model.MyModel(input_shape=(500, 500, 3), classes=10)
        return True, model

    except AttributeError:
        return (
            False,
            "Model file not provided as per docs: No function with name MyModel",
        )
    except TypeError:
        return (
            False,
            "Model file not provided as per docs: MyModel function receives no arguments",
        )
    except ValueError:
        return False, "Layers shape is not compatible with model input shape"


def is_model_supported(model_obj):
    tensorflow_supported_apis = (tf.keras.models.Sequential, tf.keras.Model)
    supported = isinstance(model_obj, tensorflow_supported_apis)
    if supported:
        # check if it of subclassing
        try:
            # Note that the `input_shape` property is only available for Functional and Sequential models.
            input_shape = model_obj.input_shape
            return True
        except AttributeError:
            return False


# function to check if layers used in tensorflow are supported
def layer_instance_check(model):
    model_layers = model.layers
    for layer in model_layers:
        if not isinstance(layer, tf.keras.layers.Layer):
            return False, []
    return True, model_layers


def is_valid_method(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        return False
    return True


def get_base64_encoded_code(code):
    if not is_valid_method(code):
        raise ValueError("Input is not a valid Python method")
    code_bytes = code.encode("utf-8")
    return base64.b64encode(code_bytes).decode("utf-8")


def getImagesCount(images_count):
    count = 0
    for key in images_count.keys():
        count += images_count[key]
    return count


def get_model_info(model):
    # For Sequential model
    if isinstance(model, tf.keras.Sequential):
        # Get the input shape
        try:
            model_input_shape = model.input_shape[1:]
        except:
            raise ValueError(
                "Unable to determine input shape for the Sequential model."
            )

        # Get the number of output classes
        try:
            model_output_classes = model.layers[-1].units
        except:
            raise ValueError(
                "Unable to determine number of output classes for the Sequential model."
            )

    # For Functional model
    elif isinstance(model, tf.keras.Model):
        # Get the input shape
        try:
            model_input_shape = model.layers[0].input_shape[0][1:]
        except:
            raise ValueError(
                "Unable to determine input shape for the Functional model."
            )

        # Get the number of output classes
        try:
            output_shape = model.output_shape
            if len(output_shape) == 2:
                model_output_classes = output_shape[1]
            else:
                raise ValueError
        except:
            raise ValueError(
                "Unable to determine number of output classes for the Functional model."
            )

    else:
        raise ValueError("Model is neither Sequential nor Functional.")

    return model_input_shape, model_output_classes


def dummy_dataset_tensorflow(
    input_shape, num_classes, batch_size=8, num_examples=1000, category=CLASSIFICATION
):
    if category == CLASSIFICATION:
        # Create random images
        images = np.random.randint(0, 256, size=(num_examples,) + input_shape).astype(
            np.uint8
        )
        # Create random labels
        labels = np.random.randint(0, num_classes, size=(num_examples,))
        # One-hot encode the labels
        labels = tf.keras.utils.to_categorical(labels, num_classes=num_classes)

        # Convert to TensorFlow datasets
        ds = tf.data.Dataset.from_tensor_slices((images, labels))

        return ds.batch(batch_size)
    else:
        return None


def dummy_dataset_pytorch(
    image_size,
    num_classes=2,
    num_images=100,
    num_channels=3,
    category=CLASSIFICATION,
    model_type="",
    tmp_path="",
):
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
        ]
    )

    if category == CLASSIFICATION:
        image_shape = (num_channels, image_size, image_size)
        train_dataset = datasets.FakeData(
            size=num_images,
            image_size=image_shape,
            num_classes=num_classes,
            transform=transform,
        )
        return train_dataset

    elif category == DETECTION:
        image_shape = (448, 448)

        fake_dataset = FakeObjectDetectionDataset(
            num_classes=num_classes, num_samples=10
        )
        classes = fake_dataset.get_classes()
        if model_type == YOLO:
            train_dataset = create_yolo_dataset(
                dataset=fake_dataset, classes=classes, image_shape=image_shape, S=7, B=2
            )
            return train_dataset

        else:
            train_dataset = create_fasterrcnn_dataset(
                dataset=fake_dataset, classes=classes, image_shape=image_shape
            )
            return train_dataset


# Function to create YOLO-compatible dataset
def create_yolo_dataset(dataset, classes, image_shape, S, B):
    try:
        yolo_dataset = []
        C = len(classes)
        class_to_idx = {cls: idx for idx, cls in enumerate(classes)}
        for img, target in dataset:
            try:
                # Extract bounding boxes and labels
                bboxes = target["boxes"]
                if not isinstance(bboxes, list):
                    d_box = [bboxes]
                else:
                    d_box = bboxes

                # boxes = [[float(obj["bndbox"]["xmin"]), float(obj["bndbox"]["ymin"]),
                #           float(obj["bndbox"]["xmax"]), float(obj["bndbox"]["ymax"])]
                #          for obj in d_box]

                labels = target["labels"]

                # Resize image
                img = transforms.ToPILImage()(img)
                # image = Image.open(img).convert("RGB")
                image = img.resize(image_shape)
                image = transforms.ToTensor()(image)

                # YOLO format: [label, x_center, y_center, width, height]
                image_info = {"path": image, "boxes": []}
                for box, label in zip(bboxes, labels):
                    x_center = ((box[0] + box[2]) / 2) / image_shape[0]
                    y_center = ((box[1] + box[3]) / 2) / image_shape[1]
                    width = (box[2] - box[0]) / image_shape[0]
                    height = (box[3] - box[1]) / image_shape[1]
                    yolo_box = [label, x_center, y_center, width, height]
                    image_info["boxes"].append(yolo_box)

                # yolo_dataset.append(image_info)
                image_info["boxes"] = torch.as_tensor(
                    image_info["boxes"], dtype=torch.float32
                )

                S = S
                B = B
                # Convert To Cells
                label_matrix = torch.zeros((S, S, C + 5 * B))
                for box in image_info["boxes"]:
                    class_label, x, y, width, height = box.tolist()
                    class_label = int(class_label)

                    # i,j represents the cell row and cell column
                    i, j = int(S * y), int(S * x)
                    x_cell, y_cell = S * x - j, S * y - i

                    """
                    Calculating the width and height of cell of bounding box,
                    relative to the cell is done by the following, with
                    width as the example:
        
                    width_pixels = (width*self.image_width)
                    cell_pixels = (self.image_width)
        
                    Then to find the width relative to the cell is simply:
                    width_pixels/cell_pixels, simplification leads to the
                    formulas below.
                    """
                    width_cell, height_cell = (
                        width * S,
                        height * S,
                    )

                    # If no object already found for specific cell i,j
                    # Note: This means we restrict to ONE object
                    # per cell!
                    #             print(i, j)
                    if label_matrix[i, j, C] == 0:
                        # Set that there exists an object
                        label_matrix[i, j, C] = 1

                        # Box coordinates
                        box_coordinates = torch.tensor(
                            [x_cell, y_cell, width_cell, height_cell]
                        )

                        label_matrix[i, j, 4:8] = box_coordinates

                        # Set one hot encoding for class_label
                        label_matrix[i, j, class_label] = 1
            except:
                continue
            data_yolo = [image_info["path"], label_matrix]
            yolo_dataset.append(data_yolo)

        return yolo_dataset
    except Exception as e:
        raise e


# Function to create Faster R-CNN-compatible dataset
def create_fasterrcnn_dataset(dataset, classes, image_shape):
    fasterrcnn_dataset = []
    for img, target in dataset:
        # Extract bounding boxes and labels
        boxes = target["annotation"]["object"]
        if not isinstance(boxes, list):
            boxes = [boxes]

        boxes = [
            [
                float(obj["bndbox"]["xmin"]),
                float(obj["bndbox"]["ymin"]),
                float(obj["bndbox"]["xmax"]),
                float(obj["bndbox"]["ymax"]),
            ]
            for obj in boxes
        ]

        labels = [classes.index(obj["name"]) for obj in boxes]

        # Resize image
        image = Image.open(img).convert("RGB")
        image = image.resize(image_shape)

        # Faster R-CNN format: {"boxes": [[x1, y1, x2, y2], ...], "labels": [label1, ...]}
        image_info = {"path": image, "boxes": boxes, "labels": labels}
        fasterrcnn_dataset.append(image_info)

    return fasterrcnn_dataset


def test_code():
    main_method = "MyModel"
    input_shape = "input_shape"
    output_classes = "output_classes"

    def MyModel(input_shape=(224, 224, 3), output_classes=3):
        base_mobilenet_model = MobileNet(
            input_shape=input_shape, include_top=False, weights=None
        )
        multi_disease_model = Sequential()
        multi_disease_model.add(base_mobilenet_model)
        multi_disease_model.add(GlobalAveragePooling2D())
        multi_disease_model.add(Dropout(0.5))
        multi_disease_model.add(Dense(output_classes, activation="sigmoid"))
        return multi_disease_model


def get_model_parameters(**kwargs) -> None:
    model = kwargs["model"]
    framework = kwargs["framework"]

    if framework == PYTORCH_FRAMEWORK:
        if not kwargs["preweights"]:
            parameters = [val.cpu().numpy() for _, val in model.state_dict().items()]
        else:
            model.load_state_dict(torch.load(PRETRAINED_WEIGHTS_FILENAME, map_location=torch.device('cpu')))
            parameters = [val.cpu().numpy() for _, val in model.state_dict().items()]
    else:
        parameters = model.get_weights()

    weight_file_path = kwargs["weight_file_path"]
    weights_file_name = kwargs["weights_file_name"]

    with open(os.path.join(weight_file_path, f"{weights_file_name}.pkl"), "wb") as f:
        pickled = pickle.dumps(parameters)
        optimized_pickle = pickletools.optimize(pickled)
        f.write(optimized_pickle)

    del parameters


def get_model_output(model) -> int:
    dummy_data = np.random.rand(1, 224, 224, 3)
    # Get prediction
    predictions = model.predict(dummy_data)

    # return the class output
    return np.argmax(predictions[0])


def validate_kwargs(
    kwargs, allowed_kwargs, error_message="Keyword argument not understood:"
):
    """Checks that all keyword arguments are in the set of allowed keys."""
    for kwarg in kwargs:
        if kwarg not in allowed_kwargs:
            raise TypeError(error_message, kwarg)


def get_model_params_count(framework="tensorflow", model=None) -> int:
    """
    calculate total trainable parameters of a given model
    """
    if framework == TENSORFLOW_FRAMEWORK:
        return model.count_params()
    else:
        return sum(p.numel() for p in model.parameters() if p.requires_grad)
