import pickletools
import shutil
import sys
import torch
import requests, json, pickle
from importlib.machinery import SourceFileLoader
from termcolor import colored
import os
import rich
from tqdm import tqdm
from .utils import *
from .functional_checks import CheckModel
from .tensorflow_checks import TensorflowChecks
from .pytorch_checks import TorchChecks

# hide warnings from tensorflow
import warnings

warnings.filterwarnings("ignore")


class Model:
    """
    Make sure model file and weights are in current directory
    Parameters: modelname

    modelname: model file name eg: vggnet, if file name is vggnet.py

    """

    def __init__(self, modelname, token, weights=False, url=""):
        self.model_check_class = None
        self.progress_bar = None
        self.progress_bar_2 = None
        self.__modelname = ""
        self.__model_path = ""
        self.__weights_path = ""
        self.__framework = TENSORFLOW_FRAMEWORK
        self.__category = CLASSIFICATION
        self.__model_type = ""
        self.__image_size = 224
        self.__batch_size = 16
        self.__classes = 0
        self.__ext = ".py"
        self.model = None
        self.loss = None
        self.__get_paths(modelname)
        self.__token = token
        self.weights = weights
        self.__url = url + "upload/"
        self.__check_model_url = url + "check-model/"
        # self.__url = 'http://127.0.0.1:8000/upload/'
        self.__recievedModelname = self.upload()

    def __get_paths(self, path):
        """
        take path provided by user as modelname
        updates model path, weights path and model name
        """
        # check if user provided a filename
        if "/" not in path:
            path = "./" + path
        # check if user provided path with .py extension
        root, ext = os.path.splitext(path)
        if ext:
            if ext != self.__ext:
                self.__ext = ".zip"
            # assign the provided path to model's path
            self.__model_path = path
            # get weights path --> remove .py from the given path and add _weights.pkl after it
            if os.path.exists(path.rsplit(".", 1)[0] + "_weights.pkl"):
                self.__weights_path = path.rsplit(".", 1)[0] + "_weights.pkl"
            else:
                self.__weights_path = path.rsplit(".", 1)[0] + "_weights.pth"
            # get model name --> get model name from given path
            self.__modelname = path.rsplit(".", 1)[0].split("/")[-1]
        else:
            # get models path --> add .py at the end of given path
            if os.path.exists(path + ".zip"):
                self.__ext = ".zip"
            self.__model_path = path + self.__ext
            # get weights path --> add _weights.pkl after given path
            if os.path.exists(path + "_weights.pkl"):
                self.__weights_path = path + "_weights.pkl"
            else:
                self.__weights_path = path + "_weights.pth"
            # get model name --> get filename from given path
            self.__modelname = path.split("/")[-1]

    def getModelId(self):
        if self.__recievedModelname is not None:
            return (
                self.__recievedModelname,
                self.__modelname,
                self.__ext,
                self.__model_path,
                self.__framework,
                self.__model_type,
                self.__category,
                self.__image_size,
                self.__batch_size,
                self.__classes,
            )

    def upload(self):
        # load model from current directory
        status = False
        message = None
        # create progress bar with total number of nested functions
        self.progress_bar = tqdm(total=10, desc="Model Checks Progress")
        try:
            # call check model class for model checks
            model_checks_generic = CheckModel(
                self.progress_bar,
                model_name=self.__modelname,
                model_path=self.__model_path,
            )
            (
                status,
                message,
                model_name,
                progress_bar,
            ) = model_checks_generic.model_func_checks()
            if not status:
                model_checks_generic.remove_tmp_file()
                text = colored(
                    message,
                    "red",
                )
                print(text, "\n")
                self.progress_bar.close()
                return None
        except:
            text = colored(
                f"\nUpload failed. There is no model with the name '{self.__modelname}' in your folder '{os.getcwd()}'.",
                "red",
            )
            print(text, "\n")
            rich.print(
                "For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs[/link]"
            )
            self.progress_bar.close()
            return None
        try:
            loaded_model = model_checks_generic.model
            self.__framework = model_checks_generic.framework
            self.__model_type = model_checks_generic.model_type
            self.__category = model_checks_generic.category
            self.__classes = model_checks_generic.output_classes
            if self.__framework == PYTORCH_FRAMEWORK:
                self.__image_size = int(model_checks_generic.image_size)
                self.__batch_size = int(model_checks_generic.batch_size)
            # get model trainable parameters
            total_params = get_model_params_count(
                framework=self.__framework, model=loaded_model
            )
            if total_params > MODEL_PARAMS_LIMIT:
                message = f"Please provide model with trainable parameters less than {MODEL_PARAMS_LIMIT}"
                model_checks_generic.remove_tmp_file()
                text = colored(
                    message,
                    "red",
                )
                print(text, "\n")
                self.progress_bar.close()
                return None
            # dump weights from non-trained model will be used in averaging check
        except:
            text = colored(
                f"\nUpload failed due to {message}",
                "red",
            )
            print(text, "\n")
            rich.print(
                "For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs[/link]"
            )
            self.progress_bar.close()
            return None
        try:
            if self.weights:
                if self.__framework == PYTORCH_FRAMEWORK:
                    shutil.copy2(
                        self.__weights_path,
                        os.path.join(
                            model_checks_generic.tmp_file_path,
                            PRETRAINED_WEIGHTS_FILENAME + ".pth",
                        ),
                    )
                else:
                    shutil.copy2(
                        self.__weights_path,
                        os.path.join(
                            model_checks_generic.tmp_file_path,
                            PRETRAINED_WEIGHTS_FILENAME + ".pkl",
                        ),
                    )
                    self.progress_bar.update(1)
        except:
            text = colored(
                f"\nUpload failed. There is no weights with the name '{self.__modelname}' in your folder '{os.getcwd()}'.",
                "red",
            )
            print(text, "\n")
            rich.print(
                "For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs[/link]"
            )
            self.progress_bar.close()
            return None
        try:
            if self.__framework == PYTORCH_FRAMEWORK:
                self.model_check_class = TorchChecks(
                    model=loaded_model,
                    model_name=model_name,
                    model_type=self.__model_type,
                    category=self.__category,
                    classes=self.__classes,
                    message=message,
                    progress_bar=self.progress_bar,
                    tmp_path=model_checks_generic.tmp_file_path,
                    image_size=self.__image_size,
                    batch_size=self.__batch_size,
                )
            elif self.__framework == TENSORFLOW_FRAMEWORK:
                self.model_check_class = TensorflowChecks(
                    model=loaded_model,
                    model_name=model_name,
                    model_type=self.__model_type,
                    category=self.__category,
                    classes=self.__classes,
                    message=message,
                    progress_bar=self.progress_bar,
                    tmp_path=model_checks_generic.tmp_file_path,
                )
            (
                status,
                message,
                model_name,
                progress_bar,
            ) = self.model_check_class.model_func_checks()
            if not status:
                model_checks_generic.remove_tmp_file()
                text = colored(
                    message,
                    "red",
                )
                print(text, "\n")
                self.progress_bar.close()
                return None
            model_checks_generic.load_model(update_progress_bar=True)
            self.model = model_checks_generic.model
            if self.model_check_class.loss is not None:
                self.loss = self.model_check_class.loss
            model_checks_generic.remove_tmp_file(update_progress_bar=True)
            self.progress_bar.close()
            updated_model_name = self.__upload_model()
            self.progress_bar_2.close()
            return updated_model_name
        except FileNotFoundError:
            text = colored(
                f"\nUpload failed due to reason {message}",
                "red",
            )
            print(text, "\n")
            rich.print(
                "For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs[/link]"
            )
            self.progress_bar.close()
            return None
        except Exception as e:
            text = colored(
                f"\nUpload failed.",
                "red",
            )
            print(text, "\n")
            if self.__url != "https://tracebloc.azurewebsites.net/":
                print(
                    f"Error in Upload is {e} at {sys.exc_info()[-1].tb_lineno} with message : {message}"
                )
            self.progress_bar.close()
            return None

    def __upload_model(self):
        try:
            self.progress_bar_2 = tqdm(total=1, desc="Model Upload Progress")
            model_file = open(self.__model_path, "rb")
            files = {"upload_file": model_file}
            if self.weights:
                weights_valid = self.checkWeights()
                if not weights_valid:
                    return None
                model_weights = open(self.__weights_path, "rb")
                files["upload_weights"] = model_weights
                values = {
                    "model_name": self.__modelname,
                    "setWeights": True,
                    "type": "functional_test",
                }
            else:
                values = {
                    "model_name": self.__modelname,
                    "setWeights": False,
                    "type": "functional_test",
                }
            # call check-model API to do functional test
            header = {"Authorization": f"Token {self.__token}"}
            r = requests.post(
                self.__check_model_url, headers=header, files=files, data=values
            )
            if self.weights:
                model_weights.close()
            model_file.close()
            body_unicode = r.content.decode("utf-8")
            content = json.loads(body_unicode)
            text = content["text"]
            check_status = content["check_status"]
            if not check_status:
                tex = colored(
                    text,
                    "red",
                )
                print(tex, "\n")
                return None
            self.progress_bar_2.update(1)
            return content["model_name"]
        except Exception as e:
            text = colored(
                f"\nUpload failed with message :{e}",
                "red",
            )
            print(text, "\n")
            self.progress_bar_2.close()

    def checkWeights(self):
        # load model weights from current directory
        try:
            weights_file = open(self.__weights_path, "rb")
        except FileNotFoundError:
            text = colored(
                f"Weights Upload failed. No weights file found with the name '{self.__modelname}_weights.pkl'\n in "
                f"path '{os.getcwd()}'.",
                "red",
            )
            print(text, "\n")
            rich.print(
                "For more information check the [link=https://docs.tracebloc.io/user-uploadModel]docs[/link]"
            )
            return False
        # Load weights to check if it works
        try:
            if self.__framework == TENSORFLOW_FRAMEWORK:
                we = pickle.load(weights_file)
                self.model.set_weights(we)
                weights_file.close()
                return True
            elif self.__framework == PYTORCH_FRAMEWORK:
                try:
                    self.model.load_state_dict(torch.load(self.__weights_path))
                    weights_file.close()
                    return True
                except Exception as e:
                    text = colored(
                        f"\nWeights upload failed with message: \n{e}",
                        "red",
                    )
                    print(text, "\n")

                    return False
            else:
                raise Exception("\nFramework not valid")
        except ValueError:
            weights_file.close()
            text = colored(
                "Weights upload failed. Provide weights compatible with the model provided.",
                "red",
            )
            print(text, "\n")
            print(
                "For more information check the docs 'https://docs.tracebloc.io/weights'"
            )
            return False, []
        except Exception as e:
            weights_file.close()
            text = colored(
                f"Weights upload failed with error: \n{e}",
                "red",
            )
            print(text, "\n")
            print(
                "For more information check the docs 'https://docs.tracebloc.io/weights'"
            )
            raise
