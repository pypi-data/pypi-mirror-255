import inspect
import sys
import dis
import re
import shutil
from inspect import getmembers, isfunction, isclass
from .utils import *


# base class for checks on model file
class CheckModel:
    MAX_MODEL_NAME_LENGTH = 64
    message = ""
    model = None
    tmp_file_path = ""
    file_name = "model.py"
    tmp_file = ""
    main_method = ""
    main_class = ""
    input_shape = ""
    output_classes = ""
    image_size = 224
    batch_size = 16
    framework = ""
    model_type = ""
    category = CLASSIFICATION
    notallowed = ["__MACOSX", "__pycache__"]
    input_shape_patt = re.compile("(^input_shape\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    out_classes_patt = re.compile("(^output_classes\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    main_method_patt = re.compile("(^main_method\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    main_class_patt = re.compile("(^main_class\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    framework_patt = re.compile("(^framework\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    image_size_patt = re.compile("(^image_size\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    batch_size_patt = re.compile("(^batch_size\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    model_type_patt = re.compile("(^model_type\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")

    def __init__(
        self, progress_bar, model_name=None, model_path=None
    ):  # pragma: no cover
        self.model_name = model_name
        self.model_path = model_path
        self.progress_bar = progress_bar
        self.file_not_allowed = False

    def prepare_file(self, temp_file):
        try:
            main_file, remove_lines, filelines = self.get_variables(temp_file)
            if main_file and self.framework == TENSORFLOW_FRAMEWORK:
                self.tmp_file = os.path.join(self.tmp_file_path, self.file_name)
                if self.main_method == "":
                    self.add_method(temp_file, remove_lines)
                else:
                    self.edit_file(temp_file, filelines, remove_lines)
            elif self.framework == PYTORCH_FRAMEWORK and main_file:
                self.tmp_file = os.path.join(self.tmp_file_path, self.file_name)
                self.edit_file(temp_file, filelines, remove_lines)
            elif main_file and self.framework == "":
                raise Exception("\nFramework argument missing in file")
        except Exception as e:
            raise e

    def get_variables(self, temp_file):
        main_file = False
        remove_lines = []
        with open(temp_file, "r") as tmp_fp:
            filedata = tmp_fp.read()
            if TORCH_HUB_PATTERN in filedata:
                self.file_not_allowed = True

        common_pattern_dict = {
            self.framework_patt: "framework",
            self.model_type_patt: "model_type",
            self.out_classes_patt: "output_classes",
            self.input_shape_patt: "input_shape",
            self.main_method_patt: "main_method",
            self.main_class_patt: "main_class",
            self.image_size_patt: "image_size",
            self.batch_size_patt: "batch_size",
        }

        for linenum, fileline in enumerate(filedata.split("\n")):
            for pattern, attribute in common_pattern_dict.items():
                if pattern.match(fileline):
                    old_line = fileline
                    value = re.sub(
                        f"({attribute}\s{{0,}}[=]\s{{0,}})",
                        "",
                        fileline.replace("'", "").replace('"', ""),
                    ).strip()

                    # Convert value to int if it's a number
                    if value.isdigit():
                        value = int(value)

                    setattr(self, attribute, value)

                    if self.framework_patt.match(old_line):
                        if not main_file:
                            self.file_name = os.path.split(temp_file)[1]
                            main_file = True

                    remove_lines.append(linenum)
                    break

        if main_file:
            if self.framework == "":
                print("Framework parameter missing from file")
                return False, [], []
            self.category = CLASSIFICATION if self.model_type == "" else DETECTION
            if self.category == DETECTION and self.output_classes == "":
                print("Output classes parameter missing from file")
                return False, [], []

        return main_file, remove_lines, filedata.split("\n")

    def replace_vars(self, code):
        if re.search(
            f"[^a-zA-Z_\-0-9]{self.input_shape}[^a-zA-Z_\-0-9]", code
        ) or re.search(f"{self.input_shape}[^a-zA-Z_\-0-9]", code):
            allresultsi = re.findall(
                f"[^a-zA-Z_\-0-9]{self.input_shape}[^a-zA-Z_\-0-9]", code
            )
            if allresultsi == []:
                allresultsi = re.findall(f"{self.input_shape}[^a-zA-Z_\-0-9]", code)
            for found in allresultsi:
                replace_text = found.replace(self.input_shape, "input_shape")
                code = code.replace(found, replace_text)
        if re.search(
            f"[^a-zA-Z_\-0-9]{self.output_classes}[^a-zA-Z_\-0-9]", code
        ) or re.search(f"{self.output_classes}[^a-zA-Z_\-0-9]", code):
            allresultso = re.findall(
                f"[^a-zA-Z_\-0-9]{self.output_classes}[^a-zA-Z_\-0-9]", code
            )
            if allresultso == []:
                allresultso = re.findall(f"{self.output_classes}[^a-zA-Z_\-0-9]", code)
            for found in allresultso:
                replace_text = found.replace(self.output_classes, "output_classes")
                code = code.replace(found, replace_text)
        return code

    def replace_variable(self, var_name, replacement, code):
        pattern = (
            f"[^a-zA-Z_\\-0-9]{var_name}[^a-zA-Z_\\-0-9]|{var_name}[^a-zA-Z_\\-0-9]"
        )
        all_results = re.findall(pattern, code)
        if not all_results:
            return code
        for found in all_results:
            replace_text = found.replace(var_name, str(replacement))
            code = code.replace(found, replace_text)
        return code

    def edit_file(self, temp_file, filelines, remove_lines=[]):
        edited_data = []
        search_super = False

        for linenum, fileline in enumerate(filelines):
            if linenum in remove_lines:
                continue
            else:
                if self.framework == TENSORFLOW_FRAMEWORK:
                    fileline = self.edit_tensorflow(fileline)
                elif self.framework == PYTORCH_FRAMEWORK:
                    fileline, search_super = self.edit_pytorch(fileline, search_super)

                edited_data.append(fileline)

        with open(temp_file, "w") as tmp_fp:
            tmp_fp.writelines("\n".join(edited_data))

    def edit_tensorflow(self, fileline):
        if re.search(f"def {self.main_method}\(.*\)", fileline):
            fileline = fileline.replace(str(self.main_method), "MyModel")
        fileline = self.replace_variable(self.input_shape, "input_shape", fileline)
        try:
            if not isinstance(self.output_classes, (int)):
                fileline = self.replace_variable(
                    self.output_classes, "output_classes", fileline
                )
            else:
                fileline = self.replace_variable(
                    "output_classes", self.output_classes, fileline
                )
        except:
            pass
        return fileline

    def edit_pytorch(self, fileline, search_super):
        if re.search(f"class {self.main_class}\(.*\)", fileline):
            fileline = fileline.replace(str(self.main_class), "MyModel")
            search_super = True
        if search_super and re.search(
            rf"super\s*\(\s*{re.escape(self.main_class)}\s*,\s*self\s*\)", fileline
        ):
            fileline = fileline.replace(str(self.main_class), "MyModel")
        try:
            if not isinstance(self.output_classes, (int)):
                fileline = self.replace_variable(
                    self.output_classes, "output_classes", fileline
                )
            else:
                fileline = self.replace_variable(
                    "output_classes", self.output_classes, fileline
                )
        except:
            pass
        return fileline, search_super

    def get_imports(self, codelines):
        instructions = [
            inst for inst in dis.get_instructions(codelines) if "IMPORT" in inst.opname
        ]
        import_line_num = set(inst.starts_line for inst in instructions)
        return sorted(import_line_num)

    def get_parameters(self, codelines, remove_lines=[]):
        import_lines = []
        myMethod = []
        input_shape = ""
        output_classes = ""
        return_obj = ""
        all_members = getmembers(self.model)
        for member_name, member_type in all_members:
            if isinstance(member_type, tf.keras.Sequential):
                return_obj = member_name

        import_line_nums = self.get_imports(codelines)
        codelines = codelines.split("\n")
        for linenum, code in enumerate(codelines):
            if (
                re.search("(.*\s{0,}=\s{0,}[tf.]{0,}[keras.]{0,}Model\(.*\))", code)
                and return_obj == ""
            ):
                return_obj = re.sub(
                    "(\s{0,}=\s{0,}[tf.]{0,}[keras.]{0,}Model\(.*\))", "", code
                )
            code = self.replace_vars(code)
            if code == "":
                continue
            elif (linenum) in remove_lines:
                continue
            elif (linenum + 1) in import_line_nums:
                import_lines.append(code.strip())
            elif re.search("(input_shape\s{0,}[=]\s{0,}\([0-9\, ]{7,}\))", code):
                input_shape = re.sub("(input_shape\s{0,}[=]\s{0,})", "", code)
            elif re.search("(output_classes\s{0,}[=]\s{0,})", code):
                output_classes = re.sub("(output_classes\s{0,}[=]\s{0,})", "", code)
            else:
                code = code.replace("    ", "\t")
                myMethod.append(code)
        return import_lines, input_shape, output_classes, myMethod, return_obj

    def prepare_wrapper_code(self, codelines, remove_lines=[]):
        (
            import_lines,
            input_shape,
            output_classes,
            myMethod,
            return_obj,
        ) = self.get_parameters(codelines, remove_lines)

        updated_code = "\n".join(import_lines)
        updated_code += f"\ndef MyModel(input_shape={input_shape}, output_classes={output_classes}):"
        updated_code += "\n\t" + "\n\t".join(myMethod)
        updated_code += f"\n\treturn {return_obj}"

        return updated_code

    def add_method(self, file="", remove_lines=[]):
        try:
            if not file:
                file = self.tmp_file
            with open(file, "r") as file_obj:
                codelines = file_obj.read()
            updated_code = self.prepare_wrapper_code(codelines, remove_lines)
            with open(file, "w") as file_obj:
                file_obj.write(updated_code)
        except Exception as e:
            self.message = f"Error: {str(e)}"
            raise

    def check_MyModel(self):
        """
        Check if model is MyModel is present in model file
        """
        try:
            if self.framework == TENSORFLOW_FRAMEWORK:
                getmembers(self.model, isfunction)
            else:
                getmembers(self.model, isclass)
            self.progress_bar.update(1)
        except Exception:  # pragma: no cover
            self.message = "Please upload file as per docs"
            raise

    def load_model(self, filename="", update_progress_bar=False):
        if filename == "":
            filename = self.file_name
        try:
            sys.path.append(self.tmp_file_path)
            self.model = SourceFileLoader(
                f"{filename}", f"{self.tmp_file}"
            ).load_module()
            self.model = self.model.MyModel()
            if update_progress_bar:
                self.progress_bar.update(1)
        except Exception as e:
            if self.message == "":
                self.message = f"Error loading the model file, {str(e)}"
            raise

    def extract_multiple_file(self):
        import zipfile

        with open(self.model_path, "rb") as file:
            with zipfile.ZipFile(file, "r") as zip_ref:
                zip_ref.extractall(self.tmp_file_path)
        return False

    def load_model_file(self):
        self.tmp_file_path = os.path.join(
            self.model_path.rsplit("/", 1)[0],
            f"tmpmodel_{self.model_name[: self.MAX_MODEL_NAME_LENGTH]}",
        )
        if not os.path.isdir(self.tmp_file_path):
            os.mkdir(self.tmp_file_path)
        # check if file contains the MyModel function
        try:
            file = self.model_path.rsplit("/", 1)[1]
            if os.path.splitext(str(file))[1] == ".zip":
                self.extract_multiple_file()
            else:
                self.tmp_file = os.path.join(self.tmp_file_path, str(file))
                self.file_name = str(file)
                shutil.copy2(self.model_path, self.tmp_file_path)
            for tmp_f in os.listdir(self.tmp_file_path):
                if not (os.path.isdir(tmp_f) or tmp_f in self.notallowed):
                    self.prepare_file(os.path.join(self.tmp_file_path, tmp_f))
            self.load_model(filename=self.file_name)
            self.check_MyModel()
        except Exception as e:  # pragma: no cover
            if os.path.exists(self.tmp_file_path):
                shutil.rmtree(self.tmp_file_path)
            if self.message == "":
                self.message = f"\nError loading the model file as {e}"
            raise

    def remove_tmp_file(self, update_progress_bar=False):
        """
        remove temporary model file
        """
        if os.path.exists(self.tmp_file_path):  # pragma: no cover
            shutil.rmtree(self.tmp_file_path)
        if update_progress_bar:
            self.progress_bar.update(1)

    def model_func_checks(self):
        try:
            self.load_model_file()
            self.message = "all checks passed"
            eligible = not self.file_not_allowed
        except Exception as e:
            self.message = f"\n\nModel checks failed with error:\n {e}"
            eligible = False

        if not eligible:
            if self.file_not_allowed:
                self.message = f"\n\nWe don't support torch hub models, please provide torchvision models"
            return eligible, self.message, None, self.progress_bar

        return True, self.message, self.model_name, self.progress_bar
