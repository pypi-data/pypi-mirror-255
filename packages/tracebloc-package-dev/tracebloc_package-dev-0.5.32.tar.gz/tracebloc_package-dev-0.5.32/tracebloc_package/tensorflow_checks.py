from silence_tensorflow import silence_tensorflow

silence_tensorflow()
from .utils import *


class TensorflowChecks:
    def __init__(self, **kwargs):
        validate_kwargs(
            kwargs,
            {
                "model",
                "model_name",
                "model_type",
                "category",
                "classes",
                "message",
                "progress_bar",
                "tmp_path",
            },
        )
        self.message = kwargs["message"]
        self.model = kwargs["model"]
        self.model_name = kwargs["model_name"]
        self.model_type = kwargs["model_type"]
        self.category = kwargs["category"]
        self.progress_bar = kwargs["progress_bar"]
        self.tmp_path = kwargs["tmp_path"]
        self.classes = kwargs["classes"]
        self.average_weights_file_path = None
        self.loss = None

    def is_model_supported(self):
        """
        Check if model contains:
            - input_shape
            - classes
        """
        tensorflow_supported_apis = (tf.keras.models.Sequential, tf.keras.Model)
        model = self.model
        supported = isinstance(model, tensorflow_supported_apis)
        if supported:  # pragma: no cover
            # check if it is of model subclassing api
            if not hasattr(model, "input_shape"):
                self.message = "\nModel file not provided as per docs: unsupported API used for Model"  # pragma: no cover
                raise Exception("input shape missing")  # pragma: no cover
        self.progress_bar.update(1)

    def layer_instance_check(self):
        """
        If model layers are of type keras layers
        """
        for layer in self.model.layers:
            if not isinstance(layer, tf.keras.layers.Layer):
                self.message = "\nLayers in Model are not supported by Tensorflow"  # pragma: no cover
                raise Exception("invalid layer")  # pragma: no cover
        self.progress_bar.update(1)

    def small_training_loop(self, weight_filename, custom_loss=False):
        try:
            if custom_loss:
                try:
                    # check for custom loss
                    import sys

                    if os.path.exists(os.path.join(self.tmp_path, "loss.py")):
                        sys.path.append(self.tmp_path)
                        from loss import Custom_loss
                    else:
                        raise Exception(
                            "loss.py file missing in the zip.\n Please refer docs for more information."
                        )
                except Exception as e:
                    raise e
            else:
                Custom_loss = tf.keras.losses.BinaryCrossentropy()
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(),
                loss=Custom_loss,
            )
            # Get the input shape and output_classes
            model_input_shape, classes = get_model_info(model=self.model)
            # mock dataset for small training
            training_dataset = dummy_dataset_tensorflow(
                input_shape=model_input_shape,
                num_classes=classes,
                num_examples=20,
                category=self.category,
            )
            self.model.fit(training_dataset, epochs=1, verbose=0)
            # dump weights from trained model will be used in averaging check
            get_model_parameters(
                model=self.model,
                weight_file_path=self.tmp_path,
                weights_file_name=TRAINED_WEIGHTS_FILENAME,
                framework=TENSORFLOW_FRAMEWORK,
                preweights=False,
            )
            if self.progress_bar is not None:
                self.progress_bar.update(1)
        except Exception as e:  # pragma: no cover
            self.message = (
                "\nModel not support training on image classification dataset."
            )
            raise

    def check_original_model_channels(self):
        """
        check for model channels to be 3
        """
        model_channel = self.model
        if model_channel.input_shape[3] != 3:
            self.message = (
                "\nPlease provide model input shape with 3 channels"  # pragma: no cover
            )
            raise Exception("invalid input shape")  # pragma: no cover
        self.progress_bar.update(1)

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
        no_images_array = [20, 20]
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
            raise

    def load_averaged_weights(self):
        try:
            with open(self.average_weights_file_path, "rb") as f:
                parameters = pickle.load(f)
            self.model.set_weights(parameters)
            del parameters
            self.progress_bar.update(1)
        except Exception as e:
            raise e

    def model_func_checks(self):
        try:
            self.is_model_supported()
            self.check_original_model_channels()
            self.layer_instance_check()
            self.small_training_loop(TRAINED_WEIGHTS_FILENAME)
            if not os.path.exists(
                    os.path.join(self.tmp_path, f"{PRETRAINED_WEIGHTS_FILENAME}.pkl")
            ):
                get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_path,
                    weights_file_name=PRETRAINED_WEIGHTS_FILENAME,
                    framework=TENSORFLOW_FRAMEWORK,
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
