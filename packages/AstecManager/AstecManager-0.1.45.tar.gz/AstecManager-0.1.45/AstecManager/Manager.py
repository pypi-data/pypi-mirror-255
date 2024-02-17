from datetime import datetime
import os, sys
from threading import Thread
from dataclasses import dataclass
from collections import defaultdict
import time
import copy
import traceback
import AstecManager.omerotools as omerolib
from multiprocessing import cpu_count
from numpy.linalg import norm
import numpy as np
from AstecManager.libs.analyze import apply_analysis,plotsignaltonoise,plotsignaltonoise_tofolder,plotmarsinfos
from skimage import exposure
from AstecManager.libs.data import imread
from AstecManager.libs.jsonlib import addDictToMetadata,printMetadata
import subprocess
from AstecManager.libs.contourlib import compute_contour
import xml.etree.ElementTree as ET
xml_metadata = "metadata.xml"

def get_omero_config(parameters):
    omero_config_file = None
    if "omero_config_file" in parameters:
        if parameters["omero_config_file"] is not None:
            omero_config_file = parameters["omero_config_file"].replace('"', '').replace("'", "")
        if omero_config_file is not None and not os.path.isfile(omero_config_file):
            return None
    return omero_config_file

def compute_user(parameters):
    user = "KB"
    if "user" in parameters:
        user = parameters["user"]
    return user
def brightness(img):
    if len(img.shape) == 3:
        # Colored RGB or BGR (*Do Not* use HSV images with this function)
        # create brightness with euclidean norm
        return np.average(norm(img, axis=2)) / np.sqrt(3)
    else:
        # Grayscale
        return np.average(img)




def convertScale(img, alpha):
    """Add bias and gain to an image with saturation arithmetics. Unlike
    cv2.convertScaleAbs, it does not take an absolute value, which would lead to
    nonsensical results (e.g., a pixel at 44 with alpha = 3 and beta = -210
    becomes 78 with OpenCV, when in fact it should become 0).
    """

    new_img = img * alpha
    new_img[new_img < 0] = 0
    new_img[new_img > 255] = 255
    return new_img.astype(np.uint8)


def decrease_brightness(img):

    img[img == img.max()] = 0
    better_contrast = exposure.equalize_adapthist(img, clip_limit=0.03)
    return better_contrast


# Automatic brightness and contrast optimization with optional histogram clipping
def automatic_brightness_and_contrast(image, clip_hist_percent=1):
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index - 1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum / 100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size - 1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    auto_result = convertScale(image, alpha)
    return auto_result, alpha, beta
    """


def import_credentials(cred_file):
    config = {}
    f = open(cred_file, "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        line_params = line.replace("'", "").replace('"', '').strip().split("=")
        if len(line_params) > 1:
            if line_params[0] == "username":
                config["login"] = line_params[1]
            elif line_params[0] == "password":
                config["password"] = line_params[1]
            elif line_params[0] == "host":
                config["host"] = line_params[1]
            elif line_params[0] == "port":
                config["port"] = int(line_params[1])
            elif line_params[0] == "group":
                config["group"] = line_params[1]
    return config


def compute_astec_command(astec_command):
    final_command_arg0 = ""
    if "fuse" in astec_command.lower():
        final_command_arg0 = "astec_fusion"
    if "mars" in astec_command.lower():
        final_command_arg0 = "astec_mars"
    if "seg" in astec_command.lower() or astec_command.lower() == "astec_astec":
        final_command_arg0 = "astec_astec"
    if "post" in astec_command.lower():
        final_command_arg0 = "astec_postcorrection"
    if "properties" in astec_command.lower():
        final_command_arg0 = "astec_embryoproperties"
    if "intra" in astec_command.lower():
        final_command_arg0 = "astec_intraregistration"
    return final_command_arg0


def compute_source_astec_dir(astec_command, params_dict):
    dir_to_create = ""
    if "mars" in astec_command.lower():
        if "EXP_FUSE" in params_dict:
            dir_to_create = "FUSE/FUSE_" + params_dict["EXP_FUSE"].replace("'", "").replace('"','')
        else:
            dir_to_create = "FUSE/FUSE_RELEASE"
    if "seg" in astec_command.lower() or astec_command.lower() == "astec_astec":
        if "EXP_FUSE" in params_dict:
            dir_to_create = "FUSE/FUSE_" + params_dict["EXP_FUSE"].replace("'", "").replace('"','')
        else:
            dir_to_create = "FUSE/FUSE_RELEASE"
    if "post" in astec_command.lower():
        if "EXP_SEG" in params_dict:
            dir_to_create = "SEG/SEG_" + params_dict["EXP_SEG"].replace("'", "").replace('"','')
        else:
            dir_to_create = "SEG/SEG_RELEASE"
    return dir_to_create


def compute_astec_dir(astec_command, params_dict):
    dir_to_create = []
    if "fuse" in astec_command.lower():
        if "EXP_FUSE" in params_dict:
            splitted_fuse = params_dict["EXP_FUSE"].replace("'", "").replace("[", "").replace("]", "").split(",")
            for fuse in splitted_fuse:
                dir_to_create.append("FUSE/FUSE_" + fuse)
        else:
            dir_to_create.append("FUSE/FUSE_RELEASE")
    if "mars" in astec_command.lower():
        if "EXP_SEG" in params_dict:
            dir_to_create.append("SEG/SEG_" + params_dict["EXP_SEG"].replace("'", "").replace('"',''))
        else:
            dir_to_create.append("SEG/SEG_RELEASE")
    if "seg" in astec_command.lower() or astec_command.lower() == "astec_astec":
        if "EXP_SEG" in params_dict:
            dir_to_create.append("SEG/SEG_" + params_dict["EXP_SEG"].replace("'", "").replace('"',''))
        else:
            dir_to_create.append("SEG/SEG_RELEASE")
    if "post" in astec_command.lower():
        if "EXP_POST" in params_dict:
            dir_to_create.append("POST/POST_" + params_dict["EXP_POST"].replace("'", "").replace('"',''))
        else:
            dir_to_create.append("POST/POST_RELEASE")
    if "properties" in astec_command.lower():
        if "EXP_INTRAREG" in params_dict:
            dir_to_create.append("INTRAREG/INTRAREG_" + params_dict["EXP_INTRAREG"].replace("'", "").replace('"',''))
        else:
            dir_to_create = "INTRAREG/INTRAREG_RELEASE"
    if "intra" in astec_command.lower():
        if "EXP_INTRAREG" in params_dict:
            dir_to_create.append("INTRAREG/INTRAREG_" + params_dict["EXP_INTRAREG"].replace("'", "").replace('"',''))
        else:
            dir_to_create.append("INTRAREG/INTRAREG_RELEASE")
    return dir_to_create


def compute_astec_tag(astec_command):
    tag = ""
    if "fuse" in astec_command.lower():
        tag = "fuse"
    elif "mars" in astec_command.lower() or "seg" in astec_command.lower() or astec_command.lower() == "astec_astec":
        tag = "seg"
    elif "post" in astec_command.lower():
        tag = "post"
    elif "intra" in astec_command.lower():
        tag = "intrareg"
    elif "properties" in astec_command.lower():
        tag = "embryoproperties"
    return tag



def is_file_image(file):
    return file.endswith('.mha') or file.endswith('nii') or file.endswith(".inr")


def is_file_image_or_compressed(file):
    return file.endswith('.mha') or file.endswith('nii') or file.endswith('.mha.gz') or file.endswith(
        'nii.gz') or file.endswith(".inr") or file.endswith(".inr.gz")


@dataclass
class astec_instance:
    astec_command: str
    folder_embryo: str
    embryo_name: str
    mars_path: str = None
    compress_result: bool = True
    params_dict: dict = defaultdict
    begin_time: int = -1
    end_time: int = -1
    omero_result: bool = True
    omero_config_file: str = ""
    tag_list: list = None
    keep_temp: bool = False
    envastec: str = "astec-dev"
    paramsuffix: str = ""
    omero_input: bool = False
    input_project: str = ""
    input_set: str = ""


class download_omero_inputs(Thread):
    def __init__(self, target_folder, project_name, dataset_name):
        Thread.__init__(self)
        self.target_folder = target_folder
        self.project_name = project_name
        self.dataset_name = dataset_name
        self.unzip = dataset_name

    def run(self):
        pyom = omerolib.connect()
        pyom.download_omero_set(self.project_name, self.dataset_name, self.target_folder)


class start_astec_cleaner(Thread):
    def __init__(self, astec_command, params_dict, name_embryo, send_to_omero, begin, end, compress_result=True,
                 omero_config_file="", tag_list=None, keep_temp=False):
        Thread.__init__(self)
        self.cleaner_folder = ""
        self.astec_command = astec_command
        self.name_embryo = name_embryo
        self.params_dict = params_dict
        self.stop_signal = False
        self.omero_result = send_to_omero
        self.compress_result = compress_result
        self.omero_file = []
        self.omero_config_file = omero_config_file
        self.omero_project_name = ""
        self.omero_dataset_name = ""
        self.dataset_id = -1
        self.begin = int(begin)
        self.end = int(end)
        self.project_id = -1
        self.tag_list = tag_list
        self.keep_temp = keep_temp

    def stop_cleaning(self):
        self.stop_signal = True

    def list_images(self, folder):
        images = []
        onlyfiles = [f for f in os.listdir(folder) if
                     os.path.isfile(os.path.join(folder, f))]
        for file in onlyfiles:
            if is_file_image(file):
                images.append(file)
        return images

    def get_images_at_t(self, time, folder):
        images = self.list_images(folder)
        result = []
        for image in images:
            if "_t{:03d}".format(time) in image:
                result.append(image)
        return result

    def image_t_exists(self, time, folder):
        images = self.list_images(folder)
        flag = False
        for image in images:
            if "_t{:03d}".format(time) in image:
                flag = True
        return flag

    def compress_and_delete(self, file):
        subprocess.run(["gzip", "-f", file])
        subprocess.run(["rm", file])

    def clean_at_t(self, time, pyom):
        print("Cleaning embryo : " + str(self.name_embryo) + " at t = " + str(time))
        for clean in self.cleaner_folder:
            images = self.get_images_at_t(time, clean)
            for image in images:
                if image is not None and is_file_image(image):
                    imagepath = os.path.join(clean, image)
                    if self.omero_result:
                        if not image in self.omero_file and not "mars" in image:
                            print("Uploading image : " + str(imagepath))
                            pyom.add_image_to_dataset_java(imagepath, self.dataset_id)
                            self.omero_file.append(image)
                            if self.compress_result:
                                print("Compressing image : " + str(imagepath))
                                self.compress_and_delete(str(imagepath))
                    elif self.compress_result:
                        print("Compressing image : " + str(imagepath))
                        self.compress_and_delete(imagepath)

        for recon in self.reconstructions_folder:
            print("Reconstruction : " + str(recon))
            if os.path.isdir(recon):
                images_reconstruction = self.get_images_at_t(time, recon)
                for image_reconstruction in images_reconstruction:
                    if image_reconstruction is not None:
                        if self.omero_result and "REC-MEMBRANE" in recon:
                            if self.reco_dataset_id is not None:
                                if not image_reconstruction in self.omero_file:
                                    print("Uploading image : " + str(os.path.join(recon, image_reconstruction)))
                                    pyom.add_image_to_dataset_java(os.path.join(recon, image_reconstruction), self.reco_dataset_id)
                                    self.omero_file.append(image_reconstruction)
                        if is_file_image(image_reconstruction) and not ".gz" in images_reconstruction:
                            print("Compressing reconstruction : " + str(os.path.join(recon, image_reconstruction)))
                            self.compress_and_delete(os.path.join(recon, image_reconstruction))
        if self.keep_temp:
            print("temp")
            for clean in self.cleaner_folder:
                temp_folder = clean + "/TEMP_{:03d}/".format(time)
                if os.path.isdir(temp_folder):
                    images = []
                    onlyfiles = [f for f in os.listdir(temp_folder) if
                                 os.path.isfile(os.path.join(temp_folder, f))]
                    print("Compressing TEMP : " + "/TEMP_{:03d}/".format(time))
                    for file2 in onlyfiles:
                        self.compress_and_delete("gzip", "-f", os.path.join(temp_folder, file2))

    def compute_recon_dir(self, params_dict):
        reconstruction_dir = []
        for dir in self.cleaner_folder:
            reconstruction_dir.append(dir + "/RECONSTRUCTION/")
        if "EXP_RECONSTRUCTION" in params_dict:
            reconstruction_dir.append("REC-MEMBRANE/REC_" + params_dict["EXP_RECONSTRUCTION"].replace('"', '').replace("'", ""))
            reconstruction_dir.append("REC-SEED/REC_" + params_dict["EXP_RECONSTRUCTION"].replace('"','').replace("'", ""))
            reconstruction_dir.append("REC-MORPHOSNAKE/REC_" + params_dict["EXP_RECONSTRUCTION"].replace('"','').replace("'", ""))
        else:
            if "EXP_SEG" in params_dict:
                reconstruction_dir.append("REC-MEMBRANE/REC_" + params_dict["EXP_SEG"].replace('"','').replace( "'", ""))
                reconstruction_dir.append("REC-SEED/REC_" + params_dict["EXP_SEG"].replace('"', '').replace("'", ""))
                reconstruction_dir.append("REC-MORPHOSNAKE/REC_" + params_dict["EXP_SEG"].replace('"','').replace("'", ""))
        return reconstruction_dir

    def copy_logs_files(self, source_folder, target_folder):
        range_t = len(source_folder)
        for i in range(0, range_t):
            source = source_folder[i]
            target = target_folder[i]
            if os.path.isdir(source):
                if not os.path.isdir(target):
                    os.makedirs(target)
                onlyfiles = [f for f in os.listdir(source) if
                             os.path.isfile(os.path.join(source, f)) and (".py" in f or ".log" in f)]
                for file in onlyfiles:
                    print("copy " + str(file) + " to " + str(target))
                    subprocess.run(["cp", os.path.join(source, file), target])

    def run(self):
        dirs = compute_astec_dir(self.astec_command, self.params_dict)
        self.cleaner_folder = []
        input_folder = []
        target_logs = []
        source_logs = []
        for dir in dirs:
            self.cleaner_folder.append(dir.replace('"', '').replace("'", ""))
            input_folder = dir.replace('"', '').replace("'", "")
        for clean in self.cleaner_folder:
            target_logs = os.path.join(clean, "LOGS")
        for input in input_folder:
            source_logs = os.path.join(input, "LOGS")
        for clean in self.cleaner_folder:
            while not os.path.isdir(clean):
                time.sleep(5)

        self.reconstructions_folder = self.compute_recon_dir(self.params_dict)

        pyom = None
        tag_step = compute_astec_tag(self.astec_command)
        if self.omero_result:
            # Connect to OMERO
            pyom = omerolib.connect(file_path=self.omero_config_file)
            # Determine ASTEC folder depending on the step
            astec_dir = compute_astec_dir(self.astec_command, self.params_dict)
            # OMERO Dataset depending of ASTEC parameters
            self.omero_dataset_name = astec_dir[0].replace("POST/", "").replace("SEG/", "").replace("FUSE/", "").replace(
                '"', '').replace("'", "")
            self.omero_dataset_recon_name = None
            for recon in self.reconstructions_folder:
                if "REC-MEMBRANE" in recon:
                    self.omero_dataset_recon_name = recon.replace("REC-MEMBRANE/","").replace('"', '').replace("'", "")

            # Project = embryo name
            self.omero_project_name = self.name_embryo
            # GET or CREATE project
            if pyom.get_project_by_name(self.omero_project_name) is None:
                pyom.create_project(self.omero_project_name)
            self.o_project = pyom.get_project_by_name(self.omero_project_name)
            self.project_id = self.o_project.getId()
            # GET or CREATE dataset
            if pyom.get_dataset_by_name(self.omero_dataset_name, self.project_id) is None:
                pyom.create_dataset(self.omero_dataset_name, self.project_id)

            if  self.omero_dataset_recon_name is not None and pyom.get_dataset_by_name(self.omero_dataset_recon_name, self.project_id) is None:
                pyom.create_dataset(self.omero_dataset_recon_name, self.project_id)
            self.dataset_id = pyom.get_dataset_by_name(self.omero_dataset_name, self.project_id).getId()
            self.reco_dataset_id = pyom.get_dataset_by_name(self.omero_dataset_recon_name, self.project_id).getId()
        # Manage time points at runtime
        for current_time in range(self.begin, self.end + 1):
            if current_time < self.end:
                for dir in self.cleaner_folder:
                    while not self.image_t_exists(current_time + 1, dir):
                        time.sleep(10)
                    self.clean_at_t(current_time, pyom)
            else:
                for dir in self.cleaner_folder:
                    while not self.image_t_exists(self.end, dir):
                        time.sleep(10)
                    self.clean_at_t(current_time, pyom)

        # upload xml and attachements at the end
        if self.omero_result:
            onlyfiles = []
            for dir in self.cleaner_folder:
               for f in os.listdir(dir):
                   if os.path.isfile(os.path.join(dir, f)):
                       onlyfiles.append(os.path.join(dir, f))
            for file in onlyfiles:
                if not is_file_image_or_compressed(file):
                    if pyom is not None:
                        print("Upload attachment file")
                        pyom.add_file_to_dataset(self.dataset_id, file)
            if self.tag_list is not None and len(self.tag_list) > 0:
                dataset = pyom.get_dataset_by_id(self.dataset_id, project=self.project_id)
                if dataset is not None:
                    for tag in self.tag_list:
                        pyom.add_tag(dataset, tag)
                    if tag_step != "":
                        pyom.add_tag(dataset, tag_step)
                else:
                    print("could not find dataset : " + str(self.dataset_id))
        self.copy_logs_files(source_logs, target_logs)
        if self.omero_result:
            if os.path.isfile(xml_metadata):
                pyom.add_file_to_dataset(self.dataset_id,xml_metadata)
        if pyom is not None:
            pyom.o_close()
        # omero the non images files and non gz files


def compute_input_folder(astec_command, params_dict):
    dir_to_create = ""
    if "seg" in astec_command.lower() or astec_command.lower() == "astec_astec":
        if "EXP_FUSE" in params_dict:
            dir_to_create = "FUSE/FUSE_" + params_dict["EXP_FUSE"].replace("'", "").replace('"','')
        else:
            dir_to_create = "FUSE/FUSE_RELEASE"
    elif "post" in astec_command.lower():
        if "EXP_SEG" in params_dict:
            dir_to_create = "SEG/SEG_" + params_dict["EXP_SEG"].replace("'", "").replace('"','')
        else:
            dir_to_create = "SEG/SEG_RELEASE"
    else:
        return None
    return dir_to_create


class start_astec_command(Thread):
    def __init__(self, astec_instance):
        Thread.__init__(self)
        self.astec_command = astec_instance.astec_command
        self.embryo_folder = astec_instance.folder_embryo
        self.name_embryo = astec_instance.embryo_name
        self.begin = astec_instance.begin_time
        self.end = astec_instance.end_time
        self.mars_path = astec_instance.mars_path
        self.params_dict = astec_instance.params_dict
        self.keep_temp = astec_instance.keep_temp
        self.use_omero_input = astec_instance.omero_input
        self.omero_config_file = astec_instance.omero_config_file
        self.omero_project_name = astec_instance.input_project
        self.omero_dataset_name = astec_instance.input_set
        self.astecenv = astec_instance.envastec
        self.paramsuffix = astec_instance.paramsuffix
        self.running_dir = ""
    def copy_logs_files(self, source_folder, target_folder):
        range_t = len(source_folder)
        for i in range(0, range_t):
            source = source_folder[i]
            target = target_folder[i]
            if os.path.isdir(source):
                if not os.path.isdir(target):
                    os.makedirs(target)
                onlyfiles = [f for f in os.listdir(source) if
                             os.path.isfile(os.path.join(source, f)) and (".py" in f or ".log" in f)]
                for file in onlyfiles:
                    print("copy " + str(file) + " to " + str(target))
                    subprocess.run(["cp", os.path.join(source, file), target])

    def run(self):
        print("Managining data for " + self.astec_command + " on embryo " + self.embryo_folder)
        final_command_arg0 = compute_astec_command(self.astec_command)
        dir_to_create = []
        dirs = compute_astec_dir(self.astec_command, self.params_dict)
        for dir in dirs:
            dir_to_create.append(dir)
        self.running_dir = dir_to_create
        if self.use_omero_input:
            folder_target = compute_input_folder(self.astec_command, self.params_dict)
            if folder_target is None:
                print("Unable to comput input files folders , exiting")
                return
            os.makedirs(folder_target)
            pyom = omerolib.connect(file_path=self.omero_config_file)
            pyom.download_omero_set(self.omero_project_name, self.omero_project_name, folder_target)
        if final_command_arg0 != "astec_embryoproperties":
            for dir in dir_to_create:
                if dir != "":
                    final_dir = dir.replace('"', '').replace("'", "").replace("[", "").replace("]", "")
                    if not os.path.isdir(final_dir):
                        os.makedirs(final_dir, mode=0o777)
            if self.mars_path is not None and final_command_arg0 == "astec_astec":
                if not os.path.isdir(self.running_dir[0].replace("'", "").replace('"', '')):
                    os.makedirs(self.running_dir[0].replace("'", "").replace('"', ''), mode=0o777)
                print("Copying mars for " + self.astec_command + " on embryo " + self.embryo_folder)
                os.system("cp " + str(self.mars_path).replace("'", "").replace('"', '') + " " + str(
                    self.running_dir[0]).replace("'", "").replace('"', '') + "/")
        print("Generating parameters for " + self.astec_command + " on embryo " + self.embryo_folder)
        parameters_name = self.astec_command + "_" + self.running_dir[0].replace("/", "_").replace("\\",
                                                                                                   "_").replace(
            '"', '') + "_" + self.paramsuffix + ".py"
        parameter_content = ""
        parameter_content += 'PATH_EMBRYO = "."\n'
        parameter_content += 'EN = "' + str(self.name_embryo).replace("'","").replace('"','') + '"\n'
        parameter_content += 'begin = ' + str(int(self.begin)) + '\n'
        if self.end != -1:
            parameter_content += 'end = ' + str(int(self.end)) + '\n'
        for dict_key in self.params_dict:
            if not dict_key == "mars_path" and not dict_key == "begin" and not dict_key == "end" and not dict_key == "raw_delay" and not dict_key == "delta":
                value_param = self.params_dict[dict_key]
                if not isinstance(self.params_dict[dict_key], bool) and isinstance(self.params_dict[dict_key], str):
                    if not '"' in self.params_dict[dict_key] and not "'" in self.params_dict[dict_key]:
                        value_param = "'"+self.params_dict[dict_key]+"'"
                parameter_content += str(dict_key) + ' = ' + str(value_param) + '\n'
        print("Writing parameters file for " + self.astec_command)
        f = open(parameters_name, "w+")
        f.write(parameter_content)
        f.close()
        commandrun = ""
        if self.keep_temp:
            commandrun = " conda run -n " + self.astecenv + " " + final_command_arg0 + " -k -p " + parameters_name
        else:
            commandrun = " conda run -n " + self.astecenv + " " + final_command_arg0 + " -p " + parameters_name
        os.system(commandrun)
        print("Command finished for " + self.astec_command)
        inputf = compute_input_folder(self.astec_command,self.params_dict)
        if inputf is not None:
            source_logs = []
            target_logs = []
            source_logs.append(os.path.join(inputf, "LOGS"))
            for inputfold in self.running_dir:
                target_logs.append(os.path.join(inputfold, "LOGS"))
            self.copy_logs_files(source_logs, target_logs)
        os.system("rm " + parameters_name)


class Manager:
    def __init__(self,astec_env="astec"):
        self.running_sessions = []
        self.running_cleaners = []
        self.to_run_list = []
        self.stop_run = False
        self.astec_instance = astec_env

    def add_to_run(self, astec_command, folder_embryo, embryo_name, begin_time, params_dict=None, end_time=-1,
                   mars_path=None, compress_result=True, omero_result=False, omero_config_file="", tag_list=None,
                   keep_temp=False, paramsuffix="", omeroinput=False, inputproject=None,
                   inputset=None):
        ai = astec_instance(astec_command, folder_embryo, embryo_name, mars_path, compress_result,
                            copy.deepcopy(params_dict),
                            begin_time, end_time, omero_result, omero_config_file, tag_list, keep_temp, self.astec_instance,
                            paramsuffix, omeroinput, inputproject, inputset)
        self.to_run_list.append(ai)


    def start_running(self, thread_number=-1):
        cpuCount = cpu_count()
        thread_count = cpuCount * 2 / 6
        if thread_number != -1:
            thread_count = thread_number
        for param in self.to_run_list:
            if len(self.running_sessions) >= thread_count:
                tc = self.running_sessions.pop(0)
                tc.join()
            tc = start_astec_command(param)
            tc.start()
            if param.compress_result or param.omero_result:
                tc2 = start_astec_cleaner(param.astec_command, param.params_dict, param.embryo_name, param.omero_result,
                                          param.begin_time, param.end_time,
                                          param.compress_result, param.omero_config_file, param.tag_list,
                                          param.keep_temp)
                tc2.start()
            self.running_sessions.append(tc)
            if param.compress_result or param.omero_result:
                self.running_cleaners.append(tc2)
        while len(self.running_sessions) > 0:
            tc = self.running_sessions.pop(0)
            if param.compress_result or param.omero_result:
                tc2 = self.running_cleaners.pop(0)
            if tc is not None:
                tc.join()
            if (param.compress_result or param.omero_result) and tc2 is not None:
                tc2.stop_cleaning()
                tc2.join()
        self.running_sessions = []
        self.running_cleaners = []
        self.to_run_list = []

    def compute_graphs_test_segmentation(self, embryo_name, begin, end):
        #atlas_path = self.compute_atlas()
        #ref_lineage = atlas_path[0]
        mincells_test = 64
        maxcells_test = 500

        folder_out = os.path.join("analysis/", "test_segmentation")
        lineages = [
            "POST/POST_test_maximum_gace/" + embryo_name + "_post_lineage.xml",
            "POST/POST_test_maximum_glace/" + embryo_name + "_post_lineage.xml",
            "POST/POST_test_addition_gace/" + embryo_name + "_post_lineage.xml",
            "POST/POST_test_addition_glace/" + embryo_name + "_post_lineage.xml"]
        names = ["SEG_test_maximum_gace", "SEG_test_maximum_glace", "SEG_test_addition_gace", "SEG_test_addition_glace"]

        apply_analysis(lineages, names, folder_out, embryo_name, mincells_test, maxcells_test, begin, end,
                       path=embryo_name + "_output_comparison.png", ref_lineage=None, data_path=folder_out)
        if os.path.isfile("histogram_branch_data.csv"):
            os.system("rm histogram_branch_data.csv")

    def compute_graphs_post(self, embryo_name, begin, end,post_list):
        #atlas_path = self.compute_atlas()
        #ref_lineage = atlas_path[0]
        mincells_test = 64
        maxcells_test = 500
        folder_out = os.path.join("analysis/", "post_segmentation")
        lineages = []
        names = []
        for exp_post in post_list:
            lineages.append( "."+ "/POST/POST_" + str(exp_post) + "/" + embryo_name + "_post_lineage.xml")
            names.append("POST_"+str(exp_post))

        apply_analysis(lineages, names, folder_out, embryo_name, mincells_test, maxcells_test, begin, end,
                       path=embryo_name + "_output_comparison.png", is_post=True, ref_lineage=None,
                       data_path=folder_out)
        if os.path.isfile("histogram_branch_data.csv"):
            os.system("rm histogram_branch_data.csv")


    def compute_folder_graphs_post(self, embryo_folder,embryo_name, begin, end,post_list):
        #atlas_path = self.compute_atlas()
        #ref_lineage = atlas_path[0]
        mincells_test = 64
        maxcells_test = 500
        folder_out = os.path.join(".", os.path.join("analysis/", "post_segmentation"))
        lineages = []
        names = []
        for exp_post in post_list:
            lineages.append( "."+ "/POST/POST_" + str(exp_post) + "/" + embryo_name + "_post_lineage.xml")
            names.append("POST_"+str(exp_post))

        apply_analysis(lineages, names, folder_out, embryo_name, mincells_test, maxcells_test, begin, end,
                       path=embryo_name + "_output_comparison.png", is_post=True, ref_lineage=None,
                       data_path=folder_out)
        if os.path.isfile("histogram_branch_data.csv"):
            os.system("rm histogram_branch_data.csv")
    def compute_images_from_movie(self, image, embryo_name):
        """
        print("-> Reading image")
        image_movie = imread(image)
        shape = image_movie.shape
        z_stack_count = shape[2]
        img_array = []
        for i in range(0, z_stack_count):
            img_array.append(image_movie[:, :, i])
        shape = image_movie[:, :, i].shape
        image_list = []
        print("-> Writing video file")
        for i in range(len(img_array)):
            print("Frame : " + str(i))
            # opencv_image = cv2.cvtColor(decrease_brightness(img_array[i]), cv2.COLOR_GRAY2BGR)
            opencv_image = cv2.cvtColor(img_array[i], cv2.COLOR_GRAY2BGR)
            image_link = join(embryo_name, 'frame' + str(i) + '.jpg')
            image_list.append(image_link)
            cv2.imwrite(image_link, opencv_image)
            height, width = img_array[i].shape
        return image_list, height, width
        """

    def compute_video_from_movie(self, embryo_name, intrareg_folder, fuse_folder):
        """
        print("Creating video")
        path = "."
        path_intrareg = join(join(path, "INTRAREG"), "INTRAREG_" + str(intrareg_folder) + "/MOVIES/")
        path_fuse = join(path_intrareg, join("FUSE", "FUSE_" + str(fuse_folder))).replace('"', '').replace("'", "")
        final_path = join(join(path, "analysis").replace("'", "").replace('"', ''), "fuse")
        if not os.path.exists(final_path):
            os.makedirs(final_path)
        image_files = [f for f in listdir(path_fuse) if isfile(join(path_fuse, f)) and (".nii" in f or ".mha" in f)]
        image_list, height, width = self.compute_images_from_movie(os.path.join(path_fuse, image_files[0]), embryo_name)
        ouputname = join(final_path, 'fusion_movie.avi')
        framerate = int(len(image_list) / 15)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        video = cv2.VideoWriter(ouputname, fourcc, framerate, (width, height))
        if not video.isOpened():
            print('Error cannot create ' + 'fusion_movie.avi')
            quit()

        for image in image_list:
            img = cv2.imread(image)
            video.write(img)
            os.system("rm " + str(image))
        cv2.destroyAllWindows()
        video.release()
        os.system('ffmpeg -i ' + ouputname + '  ' + ouputname.replace('.avi', '.mp4'))
        os.system('rm -f ' + ouputname)
        """

    def plot_signal_to_noise(self, embryo_name, parameters,one_stack_only=False,stack_chosen=0):
        print("-> Analyzing raw data intensities, this step may be long (you can continue the pipeline , please do not delete Raw Images)")
        plotsignaltonoise(embryo_name, parameters,one_stack_only=one_stack_only,stack_chosen=stack_chosen)

    def plot_signal_to_noise_tofolder(self, folder,embryo_name,one_stack_only=False,stack_chosen=0):
        plotsignaltonoise_tofolder(folder,embryo_name,one_stack_only=one_stack_only,stack_chosen=stack_chosen)

    def plot_mars_info(self, embryo_name, exp_seg, begin_time, working_resolution=0.3):
        plotmarsinfos(embryo_name, exp_seg, begin_time, resolution=working_resolution)

    def generate_init_naming_parameters(self, cell_count, xml_folder, xml_file, embryo_name):
        atlas_path = self.compute_atlas()
        now = datetime.now()
        parameters_name = "init_naming" + str(now.timestamp()).replace('.', '') + ".py"
        final_file = os.path.join(xml_folder.replace(str(embryo_name) + "/", ""), xml_file)
        txt = ""
        txt += "inputFile = '" + str(final_file) + "'" + "\n"
        txt += "outputFile = '" + str(final_file) + "'" + "\n"
        txt += "cell_number = " + str(cell_count) + "\n"
        txt += 'atlasFiles = '+atlas_path + "\n"
        txt += "check_volume=False" + "\n"
        f = open(parameters_name, "w+")
        f.write(txt)
        f.close()
        return parameters_name

    def generate_surface(self, exp_fuse, exp_post, begin, end, xmloutput, embryo_name, exp_intrareg):
        fuse_path =  "./"+embryo_name+"/INTRAREG/INTRAREG_" + str(exp_intrareg) + "/FUSE/FUSE_" + str(exp_fuse)
        fuse_template = os.path.join(fuse_path, embryo_name + "_intrareg_fuse_t%03d.nii").replace("'", "").replace('"', '')
        post_path = "./"+embryo_name+"/INTRAREG/INTRAREG_" + str(exp_intrareg) + "/POST/POST_" + str(exp_post)
        post_template = os.path.join(post_path, embryo_name + "_intrareg_post_t%03d.nii").replace("'", "").replace('"', '')
        os.system("conda run -n astec mc-cellProperties  -fusion-format " + str(
                fuse_template) + " -segmentation-format " + str(post_template) + " -first " + str(
                begin) + " -last " + str(end) + " -o " + str(
                xmloutput) + " -feature contact-surface -feature barycenter -v -v -v -v -v")


    def compute_atlas(self):
        from importlib_resources import files
        path = []
        path.append(files("AstecManager.atlas").joinpath("pm1.xml"))
        path.append(files("AstecManager.atlas").joinpath("pm3.xml"))
        path.append(files("AstecManager.atlas").joinpath("pm4.xml"))
        path.append(files("AstecManager.atlas").joinpath("pm5.xml"))
        path.append(files("AstecManager.atlas").joinpath("pm7.xml"))
        path.append(files("AstecManager.atlas").joinpath("pm8.xml"))
        path.append(files("AstecManager.atlas").joinpath("pm9.xml"))
        return path

    def generate_prop_naming_parameters(self, xml_folder, xml_file, embryo_name):
        atlas_path = self.compute_atlas()
        atlases_files = []
        now = datetime.now()
        parameters_name = "prop_naming" + str(now.timestamp()).replace('.', '') + ".py"
        txt = ""
        final_file = os.path.join(xml_folder.replace(str(embryo_name) + "/", ""), xml_file)
        txt += "inputFile = '" + str(final_file) + "'" + "\n"
        txt += "outputFile = '" + str(final_file) + "'" + "\n"
        txt += "confidence_atlases_nmin = 2" + "\n"
        txt += "confidence_atlases_percentage = 0" + "\n"
        txt += 'atlasFiles = '+str(atlas_path) + "\n"
        atlases_files.append("pm9.xml")
        f = open(parameters_name, "w+")
        f.write(txt)
        f.close()
        return parameters_name,atlas_path

    def backup_xml(self, xml_file):
        split_name = xml_file[1:len(xml_file)].split(".")
        backup_name = split_name[0] + "_backup." + split_name[1]
        os.system("cp " + str(xml_file) + " ." + str(backup_name))

    def compute_cell_count(self, mars_path):
        count = -1
        image_first = imread(mars_path)
        if mars_path is not None:
            count = len(np.unique(image_first)) - 1
        return count

    def generate_init_naming(self, xml_folder, xml_file, begin_time_name, embryo_name, exp_fuse, exp_post, begin, end,
                             exp_intrareg):

        print(" -> Generate init naming")
        xml_path = os.path.join(xml_folder, xml_file)
        mars_path = os.path.join(xml_folder, begin_time_name)
        source = open(xml_path)
        tree = ET.parse(source)
        tree = tree.getroot()
        lineage_elem = tree.find("cell_contact_surface")
        print("     - backup xml")
        self.backup_xml(xml_path)
        surface_xml = xml_path.replace("lineage", "lineage_surfaces")
        if lineage_elem is None:
            print("     - generate surfaces in side xml")
            self.generate_surface(exp_fuse, exp_post, begin, end, surface_xml, embryo_name, exp_intrareg)
            print("     - merging 2 xml")
            os.system(
                "conda run -n astec astec_embryoproperties -i " + xml_path + " " + surface_xml + " -o " + xml_path)
            print("     - cleaning temp xml")
            os.system("rm " + str(surface_xml))
        print("     - compute cell count from mars")
        cell_count = self.compute_cell_count(mars_path)
        print("     - generate naming parameter file")
        parameter_file = self.generate_init_naming_parameters(cell_count, xml_folder, xml_file, embryo_name)
        print("     - running naming")
        os.system("conda run -n astec-dev astec_atlas_init_naming -v -v -v -p " + str(
            parameter_file))
        os.system("rm " + str(parameter_file))

    def propagate_naming(self, xml_folder, xml_file, embryo_name):
        print(" -> Propagate naming")
        print("     - generate parameters")
        parameter_file,atlases_files = self.generate_prop_naming_parameters(xml_folder, xml_file, embryo_name)
        print("     - propagation of naming")
        os.system("conda run -n astec-dev astec_atlas_naming -v -v -v -p " + str(
            parameter_file))
        print("     - cleaning")
        os.system("rm " + str(parameter_file))
        return atlases_files

    def writeStepToJson(self, parameters,step,embryo_folder=".",logFolder=None):
        parameters["step"] = step
        addDictToMetadata(embryo_folder,parameters,addDictToMetadata,logFolder)
    def downscale_folder(self, parameters):
        embryo_name = parameters["embryo_name"].replace('"','').replace("'","")
        omero_config_file = get_omero_config(parameters)
        voxel_size = float(parameters["resolution"])
        embryo_folder = "."
        input_folder = os.path.join(embryo_folder, "FUSE/FUSE_" + str(parameters["EXP_FUSE"]))
        output_folder = os.path.join(embryo_folder, "FUSE/FUSE_" + str(parameters["EXP_FUSE"]) + "_down0"+str(voxel_size).split(".")[1])
        files = os.listdir(input_folder)
        files.sort()
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        for file in files:
            # make sure file is an image
            if file.endswith(('.mha', '.nii', '.mha.gz', '.nii.gz', '.inr', '.inr.gz')):
                img_path = os.path.join(input_folder, file)
                print("     -> " + str(img_path))
                img_t = os.path.join(output_folder, file)
                os.system("conda run -n astec applyTrsf -iso " + str(voxel_size) + " " + img_path + " " + img_t)

        if omero_config_file is not None:
            self.upload_on_omero(omero_config_file, embryo_name, "FUSE_" + str(parameters["EXP_FUSE"]) + "_down0"+str(voxel_size).split(".")[1],
                                 output_folder)


    def downscale_contour_folder(self, parameters):
        voxel_size = float(parameters["resolution"])
        embryo_folder = "."
        input_folder = os.path.join(embryo_folder, "CONTOUR/CONTOUR_" + str(parameters["EXP_CONTOUR"]))
        output_folder = os.path.join(embryo_folder, "CONTOUR/CONTOUR_" + str(parameters["EXP_CONTOUR_DOWNSCALED"]))
        template_format = parameters["template_file"]
        files = os.listdir(input_folder)
        files.sort()
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        for file in files:
            # make sure file is an image
            if file.endswith(('.mha', '.nii', '.mha.gz', '.nii.gz', '.inr', '.inr.gz')):
                img_path = os.path.join(input_folder, file)
                time = int(file.split("_t")[1].split(".")[0])
                print("     -> " + str(img_path))
                img_t = os.path.join(output_folder, file)
                img_template = template_format.format(time)
                os.system("conda run -n astec applyTrsf -ref " + str(img_template) + " -iso " + str(voxel_size) + " " + img_path + " " + img_t)
    def save_upload_parameters(self, omero_project_name, omero_dataset_name, embryo_folder,user=None):
        parameters = {}
        parameters["user"] = user
        parameters["omero_project"] = omero_project_name
        parameters["omero_dataset"] = omero_dataset_name
        parameters["input_folder"] = embryo_folder
        self.writeStepToJson(parameters, "upload_to_omero", embryo_folder=".")
    def upload_on_omero(self, config_file, omero_project_name, omero_dataset_name, input_folder, include_logs=False,embryo_name=None,user=None):
        config_array = omerolib.parse_parameters_file(config_file)
        om_login = config_array['login']
        om_pw = config_array['password']
        om_host = config_array['host']
        om_port = int(config_array['port'])
        om_group = config_array['group']
        om_secure = config_array['secure']
        embryo_folder = "."

        pyom = omerolib.connect(login=om_login, passwd=om_pw, server=om_host, port=om_port, group=om_group,
                                secure=om_secure)
        pyom.upload_omero_set(omero_project_name.replace("'", "").replace('"', ''),
                              omero_dataset_name.replace("'", "").replace('"', ''),
                              input_folder.replace("'", "").replace('"', ''), include_logs=include_logs)
        self.save_upload_parameters(omero_project_name, omero_dataset_name,embryo_folder,user)


    def download_from_omero(self, parameters):
        config_file = get_omero_config(parameters)
        omero_project_name = parameters["embryo_name"].replace('"','').replace("'","")
        omero_dataset_name = parameters["dataset_name"]
        output_folder = parameters["output_folder"]
        if config_file is None:
            print("OMERO config file is not bound, unable to upload")
            exit()
        if not os.path.isfile(config_file):
            print("Unable to find OMERO config file , unable to upload")
            exit()
        config_array = omerolib.parse_parameters_file(config_file)
        om_login = config_array['login']
        om_pw = config_array['password']
        om_host = config_array['host']
        om_port = int(config_array['port'])
        om_group = ""
        if 'group' in config_array:
            om_group = config_array['group']
        om_secure = config_array['secure']
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)

        pyom = omerolib.connect(login=om_login, passwd=om_pw, server=om_host, port=om_port, group=om_group,
                                secure=om_secure)
        pyom.download_omero_set(omero_project_name.replace("'", "").replace('"', ''),
                                omero_dataset_name.replace("'", "").replace('"', ''),
                                output_folder.replace("'", "").replace('"', ''))

    def compute_contours(self, parameters):

        omero_config_file = get_omero_config(parameters)
        normalisation = parameters["normalisation"]
        background_folder_name = parameters["EXP_BACKGROUND"]
        voxel_size = parameters["resolution"]
        embryo_name = parameters["embryo_name"].replace('"','').replace("'","")
        user = compute_user(parameters)
        embryo_folder ="./"
        compute_contour(embryo_folder, background_folder_name, reducvoxelsize=float(voxel_size),
                        target_normalization_max=normalisation, correction_vsize=True,user=user)
        contour_folder = "CONTOUR/CONTOUR_RELEASE_" + str(voxel_size).split(".")[1]
        if omero_config_file is not None:
            self.upload_on_omero(omero_config_file, embryo_name, "CONTOUR_RELEASE_" + str(voxel_size).split(".")[1],
                                 contour_folder)
        parameters["contour_folder"] = contour_folder
        self.writeStepToJson(parameters, "compute_contour", embryo_folder=".")

    def name_embryo(self, parameters):
        embryo_name = parameters["embryo_name"].replace('"','').replace("'","")
        begin = parameters["begin"]
        end = parameters["end"]
        lineage_path = "INTRAREG/INTRAREG_" + str(parameters["EXP_INTRAREG"])+"/POST/POST_" + parameters["EXP_POST"] + "/"
        lineage_name = embryo_name + "_intrareg_post_lineage.xml"
        mars_filename = embryo_name + "_intrareg_post_t{:03d}.nii".format(begin)
        self.generate_init_naming(lineage_path.replace('"', '').replace("'", ""),
                                  lineage_name.replace('"', '').replace("'", ""),
                                  mars_filename.replace('"', '').replace("'", ""),
                                  embryo_name.replace('"', '').replace("'", ""),
                                  str(parameters["EXP_FUSE"]).replace('"', '').replace("'", ""),
                                  str(parameters["EXP_POST"]).replace('"', '').replace("'", ""), begin, end,
                                  str(parameters["EXP_INTRAREG"]).replace('"', '').replace("'", ""))
        atlases_files = self.propagate_naming(lineage_path.replace('"', '').replace("'", ""),
                              lineage_name.replace('"', '').replace("'", ""),
                              embryo_name.replace('"', '').replace("'", ""))
        parameters["atlas"] = self.compute_atlas()
        logFolder = "./INTRAREG/INTRAREG_"+ str(parameters["EXP_INTRAREG"]).replace('"', '').replace("'", "")+"/LOGS/"
        self.writeStepToJson(parameters, "name_embryo", embryo_folder=".", logFolder=logFolder)


    def copy_raw_data(self, parameters):

        searcher = compute_user(parameters)

        if not "embryo_name" in parameters:
            print("Embryo name is not provided in parameters ")
            exit()
        if not "input_folder" in parameters:
            print("Distant raw data folder path is not provided in parameters")
            exit()
        input_folder = parameters["input_folder"]
        embryo_dir = "."
        if not os.path.isdir(embryo_dir):
            os.makedirs(embryo_dir)
        raw_data_output = os.path.join(embryo_dir, "RAWDATA")
        if not os.path.isdir(raw_data_output):
            os.makedirs(raw_data_output)
        try:
            subprocess.run(['rsync', '-avzr', str(input_folder), raw_data_output + "/"], check=True)
            self.writeStepToJson(parameters, "copy_rawdata", embryo_folder=".")
        except subprocess.CalledProcessError:
            print('Error during the copy of the data , please verify the parameters and try again')


    def downscale_mars(self, parameters):
        voxel_size = parameters["resolution"]
        if not "mars_file" in parameters:
            print("Please specify a MARS file path")
            exit()
        if not "output_folder" in parameters:
            print("Please specify the folder for the downscaled file")
            exit()
        if not "template_file" in parameters:
            print("Please specify the corresponding fusion image (downscaled version)")
            exit()
        mars = parameters["mars_file"]
        if not os.path.isfile(mars):
            print(str(mars))
            print("MARS file does not exist")
            exit()
        fusion = parameters["template_file"]
        if not os.path.isfile(fusion):
            print("template file does not exist")
            exit()
        output_folder = parameters["output_folder"]
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        marsname = mars.replace("\\", "/").split("/")[-1]
        output_file = os.path.join(output_folder, marsname)
        os.system("conda run -n astec applyTrsf -ref " + str(fusion) + " -interpolation nearest -iso " + str(
            voxel_size) + " " + str(mars) + " " + str(output_file))
        self.writeStepToJson(parameters, "downscale_mars", embryo_folder=".")

    def apply_downscaling(self,parameters):
        downscale_contour = bool(parameters["use_contour"])
        if not "embryo_name" in parameters:
            print("Please specify a embryo name")
            exit()
        if not "begin" in parameters:
            print("Please specify a begin point")
            exit()
        if not "EXP_FUSE" in parameters:
            print("Please specify a fuse exp")
            exit()
        if downscale_contour and not "EXP_CONTOUR" in parameters:
            print("Please specify a contour exp")
            exit()
        if downscale_contour and not "EXP_CONTOUR_DOWNSCALED" in parameters:
            print("Please specify a contour exp downscaled")
            exit()
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        embryo_folder = "."
        voxel_size = 0.6
        time_point = 0
        if "begin" in parameters:
            time_point = int(parameters["begin"])
        if not "resolution" in parameters:
            parameters["resolution"] = voxel_size
        else :
            voxel_size = float(parameters["resolution"])
        mars_path = os.path.join(embryo_folder,"MARS/"+embryo_name+"_mars_t{:03d}.nii".format(time_point))
        parameters["mars_file"] = mars_path
        mars_output_path = os.path.join(embryo_folder,"MARS0"+str(voxel_size).split(".")[1]+"/")
        parameters["output_folder"] = mars_output_path

        embryo_folder = "."
        input_folder = os.path.join(embryo_folder, "FUSE/FUSE_" + str(parameters["EXP_FUSE"]))
        fusion_output_dir = os.path.join(embryo_folder, "FUSE/FUSE_" + str(parameters["EXP_FUSE"]) + "_down0"+str(voxel_size).split(".")[1])
        input_fuse_template = os.path.join(fusion_output_dir,embryo_name+"_fuse_t{:03d}.nii".format(time_point))
        parameters["template_file"] = input_fuse_template
        print("     > Downscaling Fusion")
        self.downscale_folder(parameters)
        print("     > Downscaling Mars")
        self.downscale_mars(parameters)
        input_fuse_template = os.path.join(fusion_output_dir, embryo_name + "_fuse_t{:03d}.nii")
        parameters["template_file"] = input_fuse_template
        #Create function that downscale countours
        if downscale_contour:
            print("     > Downscaling Contours")
            self.downscale_contour_folder(parameters)

    def test_fusion(self,parameters,parameter_exploration=False,rerun=False,one_stack_only=False,stack_chosen=0):
        embryo_name = parameters["embryo_name"].replace('"', '').replace("'", "")
        parameters["fusion_xzsection_extraction"] = "True"
        # TESTS DEPENDENT PARAMETERS, DO NOT CHANGE
        #
        #
        #
        if rerun or parameter_exploration:
            parameters["fusion_strategy"] = "hierarchical-fusion"
            parameters["EXP_FUSE"] = "01_right_hierarchical"
            parameters["acquisition_orientation"] = "right"
            self.start_fusion(parameters,run_now=False, keep_temp=False,one_stack_only=one_stack_only,stack_chosen=stack_chosen)

            parameters["fusion_strategy"] = "direct-fusion"
            parameters["EXP_FUSE"] = "01_right_direct"
            parameters["acquisition_orientation"] = "right"
            self.start_fusion(parameters,run_now=False, keep_temp=False,one_stack_only=one_stack_only,stack_chosen=stack_chosen)

            parameters["fusion_strategy"] = "hierarchical-fusion"
            parameters["EXP_FUSE"] = "01_left_hierarchical"
            parameters["acquisition_orientation"] = "left"

            self.start_fusion(parameters,run_now=False, keep_temp=False,one_stack_only=one_stack_only,stack_chosen=stack_chosen)

            parameters["fusion_strategy"] = "direct-fusion"
            parameters["EXP_FUSE"] = "01_left_direct"
            parameters["acquisition_orientation"] = "left"

            self.start_fusion(parameters,run_now=False, keep_temp=False,one_stack_only=one_stack_only,stack_chosen=stack_chosen)
            self.start_running(thread_number=4)
        else :
            parameters["fusion_strategy"] = "hierarchical-fusion"
            parameters["EXP_FUSE"] = "01_test"
            parameters["acquisition_orientation"] = "right"
            self.start_fusion(parameters, keep_temp=False,one_stack_only=one_stack_only,stack_chosen=stack_chosen)


    def start_fusion(self,parameters,run_now=True,keep_temp=False,channel_count=1,one_stack_only=False,stack_chosen=0):
        omero_config_file = get_omero_config(parameters)
        embryo_name = parameters["embryo_name"].replace('"','').replace("'","")

        begin = parameters["begin"]
        end = parameters["end"]
        real_parameters = {}
        real_parameters["acquisition_resolution"] = (.195, .195, 1.)
        real_parameters["target_resolution"] = .3
        real_parameters["result_image_suffix"] = 'nii'
        real_parameters["acquisition_slit_line_correction"] = True
        real_parameters["acquisition_cropping_opening"] = 2
        real_parameters["acquisition_cropping"] = False
        real_parameters["raw_crop"] = True
        real_parameters["fusion_crop"] = True

        real_parameters["fusion_preregistration_compute_registration"] = True
        real_parameters["fusion_preregistration_normalization"] = False
        real_parameters["fusion_registration_normalization"] = False
        real_parameters["fusion_stack_preregistration_normalization"] = False
        real_parameters["fusion_stack_registration_normalization"] = False
        real_parameters["fusion_xzsection_extraction"] = False

        # DATA DEPENDENT PARAMETERS , SHOUD NOT CHANGE IF UPDATED ONCE
        #
        #
        #

        real_parameters["DIR_RAWDATA"] = "RAWDATA"
        if (one_stack_only and stack_chosen == 0) or not one_stack_only:
            real_parameters["DIR_LEFTCAM_STACKZERO"] = "stack_0_channel_0_obj_left"
            real_parameters["DIR_RIGHTCAM_STACKZERO"] = "stack_0_channel_0_obj_right"
        if (one_stack_only and stack_chosen == 1) or not one_stack_only:
            real_parameters["DIR_LEFTCAM_STACKONE"] = "stack_1_channel_0_obj_left"
            real_parameters["DIR_RIGHTCAM_STACKONE"] = "stack_1_channel_0_obj_right"
        if channel_count > 1:
            if (one_stack_only and stack_chosen == 0) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKZERO_CHANNEL_2"] = "stack_0_channel_1_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKZERO_CHANNEL_2"] = "stack_0_channel_1_obj_right"
            if (one_stack_only and stack_chosen == 1) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKONE_CHANNEL_2"] = "stack_1_channel_1_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKONE_CHANNEL_2"] = "stack_1_channel_1_obj_right"
        if channel_count > 2:
            if (one_stack_only and stack_chosen == 0) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKZERO_CHANNEL_3"] = "stack_0_channel_2_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKZERO_CHANNEL_3"] = "stack_0_channel_2_obj_right"
            if (one_stack_only and stack_chosen == 1) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKONE_CHANNEL_3"] = "stack_1_channel_2_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKONE_CHANNEL_3"] = "stack_1_channel_2_obj_right"
        if channel_count > 3:
            if (one_stack_only and stack_chosen == 0) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKZERO_CHANNEL_4"] = "stack_0_channel_3_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKZERO_CHANNEL_4"] = "stack_0_channel_3_obj_right"
            if (one_stack_only and stack_chosen == 1) or not one_stack_only:
                real_parameters["DIR_LEFTCAM_STACKONE_CHANNEL_4"] = "stack_1_channel_3_obj_left"
                real_parameters["DIR_RIGHTCAM_STACKONE_CHANNEL_4"] = "stack_1_channel_3_obj_right"
        real_parameters["acquisition_leftcam_image_prefix"] = "Cam_Left_000"
        real_parameters["acquisition_rightcam_image_prefix"] = "Cam_Right_000"
        real_parameters["fusion_weighting"] = "guignard"
        real_parameters["fusion_strategy"] = 'hierarchical-fusion'

        real_parameters["EXP_FUSE"] = '01'
        real_parameters["acquisition_orientation"] = 'right'
        real_parameters["acquisition_mirrors"] = False
        real_parameters["acquisition_leftcamera_z_stacking"] = 'direct'
        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]

        self.add_to_run("FUSE", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False,omero_result=(omero_config_file is not None),omero_config_file=omero_config_file,keep_temp=keep_temp)
        if run_now:
            self.start_running(thread_number=1)
            logFolder = "./FUSE/FUSE_"+str(real_parameters["EXP_FUSE"]).replace("'","").replace('"','')+"/LOGS/"
            self.writeStepToJson(real_parameters,"fusion",".",logFolder=logFolder)
            #self.write_fusions_parameters(parameters, keep_temp=keep_temp)
        return real_parameters

    def compute_fusion_movie(self,parameters):
        real_parameters = {}
        real_parameters["EXP_INTRAREG"] = '01_TEST'
        real_parameters["intra_registration_movie_fusion_images"] = True
        embryo_name = parameters["embryo_name"].replace('"','').replace("'","")

        begin = parameters["begin"]
        end = parameters["end"]
        for key in parameters:
            real_parameters[key] = parameters[key]

        try:
            self.add_to_run("INTRAREG", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False)

            self.start_running(thread_number=1)
            logFolder = "./INTRAREG/INTRAREG_" + str(real_parameters["EXP_INTRAREG"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(real_parameters,"intrareg_movie",".",logFolder=logFolder)

            self.compute_video_from_movie(embryo_name, real_parameters["EXP_INTRAREG"], real_parameters["EXP_FUSE"])
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error fusion movie : " + str(strlog))
    def final_fusion(self, parameters,one_stack_only=False,stack_chosen=0):
        embryo_name = parameters["embryo_name"].replace('"','').replace("'","")
        if not "EXP_FUSE" in parameters:
            parameters["EXP_FUSE"] = "01"
        number_of_channels = 1
        if "number_of_channels" in parameters:
            try :
                number_of_channels = int(parameters["number_of_channels"])
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error number of channel is not an integer: " + str(strlog))
        real_parameters = self.start_fusion(parameters,channel_count=number_of_channels,one_stack_only=one_stack_only,stack_chosen=stack_chosen)
        try :
            self.compute_fusion_movie(real_parameters)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during movie computation : "+str(strlog))

        try:
            print("PLotting intensities"
                  "")
            self.plot_signal_to_noise(embryo_name, real_parameters,one_stack_only=one_stack_only,stack_chosen=stack_chosen)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during signal plot: "+str(strlog))


    def start_mars(self,parameters):
        use_contour = parameters["use_contour"]
        omero_config_file = get_omero_config(parameters)
        embryo_name = parameters["embryo_name"].replace('"','').replace("'","")
        embryo_dir ="."
        begin = int(parameters["begin"])
        end = int(parameters["end"])
        normalisation = 1000
        if "normalisation" in parameters:
            normalisation = parameters["normalisation"]
        voxel_size = parameters["resolution"]
        real_parameters = {}

        real_parameters["sigma_TV"] = 4.5
        real_parameters["result_image_suffix"] = "nii"
        real_parameters["intensity_enhancement"] = 'gace'

        if use_contour:
            real_parameters["EXP_CONTOUR"] = "RELEASE_" + str(voxel_size).split(".")[1]
            real_parameters["outer_contour_enhancement"] = 'from_contour_image'
            real_parameters["enhancement_normalization_max_value"] = normalisation
            real_parameters["enhancement_transformation"] = "normalization_to_u16"
            real_parameters["normalization_max_value"] = normalisation
            real_parameters["intensity_transformation"] = "normalization_to_u16"
        user = None
        if "user" in parameters:
            user = parameters["user"]
        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]
        self.add_to_run("MARS", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False,omero_result=(omero_config_file is not None),omero_config_file=omero_config_file)
        self.start_running(thread_number=1)
        real_parameters["uploaded_to_omero"] = (omero_config_file is not None)
        logFolder = "./SEG/SEG_" + str(real_parameters["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.writeStepToJson(real_parameters,"mars",".",logFolder=logFolder)

        try:
            self.plot_mars_info(embryo_name, "mars_add", begin, working_resolution=voxel_size)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during mars add plot: " + str(strlog))
        return real_parameters

    def test_mars(self,parameters):
        parameters["EXP_SEG"] = "mars_add"
        parameters["reconstruction_images_combination"] = "addition"
        real_parameters = self.start_mars(parameters)

        real_parameters["EXP_SEG"] = "mars_max"
        real_parameters["reconstruction_images_combination"] = "maximum"
        self.start_mars(real_parameters)

    def test_segmentation(self,parameters):
        # TESTS DEPENDENT PARAMETERS, DO NOT CHANGE
        #
        #
        #
        if True:
            parameters["EXP_SEG"] = "test_addition_glace"
            parameters["reconstruction_images_combination"] = "addition"
            parameters["intensity_enhancement"] = "glace"
            self.start_segmentation(parameters,run_now=True)
        if True:
            logFolder = "./SEG/SEG_" + str(parameters["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
            parameters2 = parameters
            parameters2["EXP_SEG"] = "test_addition_gace"
            parameters2["reconstruction_images_combination"] = "addition"
            parameters2["intensity_enhancement"] = "gace"
            self.start_segmentation(parameters2,run_now=False)
            logFolder2 = "./SEG/SEG_" + str(parameters2["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"

            parameters3 = parameters
            parameters3["EXP_SEG"] = "test_maximum_glace"
            parameters3["reconstruction_images_combination"] = "maximum"
            parameters3["intensity_enhancement"] = "glace"
            logFolder3 = "./SEG/SEG_" + str(parameters3["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.start_segmentation(parameters3,run_now=False)
            parameters4 = parameters
            parameters4["EXP_SEG"] = "test_maximum_gace"
            parameters4["reconstruction_images_combination"] = "maximum"
            parameters4["intensity_enhancement"] = "gace"

            self.start_segmentation(parameters4,run_now=False)
            logFolder4 = "./SEG/SEG_" + str(parameters4["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"

            self.start_running(thread_number=4)
            self.writeStepToJson(parameters,"segmentation_test",".",logFolder=logFolder)
            self.writeStepToJson(parameters2,"segmentation_test",".",logFolder=logFolder2)
            self.writeStepToJson(parameters3,"segmentation_test",".",logFolder=logFolder3)
            self.writeStepToJson(parameters4,"segmentation_test",".",logFolder=logFolder4)

        # Embryo dependant parameters

        parameters["EXP_SEG"] = 'test_maximum_gace'
        parameters["EXP_POST"] = 'test_maximum_gace'

        self.start_post_correction(parameters,run_now=False)
        parameters2 = parameters
        parameters2["EXP_SEG"] = 'test_addition_glace'
        parameters2["EXP_POST"] = 'test_addition_glace'

        self.start_post_correction(parameters2,run_now=False)
        parameters3 = parameters
        parameters3["EXP_SEG"] = 'test_addition_gace'
        parameters3["EXP_POST"] = 'test_addition_gace'

        self.start_post_correction(parameters3,run_now=False)

        parameters4 = parameters
        parameters4["EXP_SEG"] = 'test_maximum_glace'
        parameters4["EXP_POST"] = 'test_maximum_glace'

        self.start_post_correction(parameters4,run_now=False)


        if True:
            self.start_running(thread_number=4)
        self.compute_graphs_test_segmentation(parameters["embryo_name"], parameters["begin"], parameters["end"])
        logFolder = "./POST/POST_" + str(parameters["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.writeStepToJson(parameters, "post_correction_test", ".", logFolder=logFolder)
        logFolder2 = "./POST/POST_" + str(parameters2["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.writeStepToJson(parameters2,"post_correction_test",".",logFolder=logFolder2)
        logFolder3 = "./POST/POST_" + str(parameters3["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.writeStepToJson(parameters3,"post_correction_test",".",logFolder=logFolder3)
        logFolder4 = "./POST/POST_" + str(parameters4["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
        self.writeStepToJson(parameters4,"post_correction_test",".",logFolder4)


    def start_segmentation(self,parameters,run_now=True):
        use_contour = parameters["use_contour"]
        omero_config_file = get_omero_config(parameters)
        normalisation = 1000
        if "normalisation" in parameters:
            normalisation = parameters["normalisation"]
        voxel_size = parameters["resolution"]

        MARS_PATH = parameters["mars_path"]
        embryo_name = parameters["embryo_name"].replace("'","").replace('"','')
        begin = int(parameters["begin"])
        end = int(parameters["end"])

        real_parameters = {}

        real_parameters["sigma_TV"] = 4.5
        real_parameters["result_image_suffix"] = "nii"
        real_parameters["intensity_enhancement"] = 'gace'
        real_parameters["EXP_FUSE"] = "01"
        if use_contour:
            real_parameters["EXP_CONTOUR"] = "RELEASE_" + str(voxel_size).split(".")[1]
            real_parameters["outer_contour_enhancement"] = "from_contour_image"
            real_parameters["enhancement_normalization_max_value"] = normalisation
            real_parameters["enhancement_transformation"] = "normalization_to_u16"
            real_parameters["normalization_max_value"] = normalisation
            real_parameters["intensity_transformation"] = "normalization_to_u16"

        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]
        self.add_to_run("SEG", ".", embryo_name, begin, parameters, end_time=end, compress_result=False,
                           mars_path=MARS_PATH,omero_result=(omero_config_file is not None),omero_config_file=omero_config_file)
        if run_now:
            self.start_running(thread_number=1)
            real_parameters["uploaded_on_omero"] = (omero_config_file is not None)
            logFolder = "./SEG/SEG_" + str(parameters["EXP_SEG"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(real_parameters,"segmentation",".",logFolder=logFolder)
            #self.segmentation_parameters(real_parameters)
        return real_parameters

    def start_post_correction(self,parameters,run_now=True):
        embryo_name = parameters["embryo_name"].replace('"','').replace("'","")
        omero_config_file = get_omero_config(parameters)
        begin = int(parameters["begin"])
        end = int(parameters["end"])
        voxel_size = parameters["resolution"]
        real_parameters = {}
        real_parameters["EXP_POST"] = '01'
        real_parameters["intra_registration_resolution"] = voxel_size
        real_parameters["test_branch_length"] = True
        real_parameters["test_early_division"] = True
        real_parameters["test_volume_correlation"] = True
        real_parameters["test_postponing_division"] = True
        real_parameters["result_image_suffix"] = 'nii'
        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]
        self.add_to_run("POST", ".", embryo_name, begin, parameters, end_time=end, compress_result=False,omero_result=(omero_config_file is not None),omero_config_file=omero_config_file)
        if run_now:
            self.start_running(thread_number=1)
            real_parameters["uploaded_on_omero"] = (omero_config_file is not None)
            logFolder = "./POST/POST_" + str(parameters["EXP_POST"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(real_parameters,"post_correction",".",logFolder=logFolder)
            #self.post_correction_parameters(parameters)
            try :
                self.compute_graphs_post(embryo_name, begin, end , [parameters["EXP_POST"]])
            except :
                strlog = traceback.format_exc()
                print("Error during computation of the Post correction graphs"+ str(strlog))
        return real_parameters


    def apply_intrareg(self,parameters):
        omero_config_file = get_omero_config(parameters)
        embryo_name = parameters["embryo_name"].replace("'","").replace('','"')
        begin = parameters["begin"]
        end = parameters["end"]
        real_parameters = {}
        real_parameters["EXP_INTRAREG"] = "01"
        real_parameters["delta"] = 1
        real_parameters["raw_delay"] = 0
        real_parameters["intra_registration_template_type"] = 'POST-SEGMENTATION'
        real_parameters["intra_registration_template_threshold"] = 2
        real_parameters["intra_registration_margin"] = 20
        real_parameters["intra_registration_resample_post_segmentation_images"] = True
        real_parameters["intra_registration_resample_segmentation_images"] = False
        real_parameters["intra_registration_movie_post_segmentation_images"] = True
        real_parameters["intra_registration_movie_segmentation_images"] = False
        real_parameters["intra_registration_rebuild_template"] = True
        for key_param in parameters:
            real_parameters[key_param] = parameters[key_param]

        # PRODUCTION PARAMETERS, UPDATE WITH THE TEST CHOSEN PREVIOUSLY
        #
        #
        #

        try:
            self.add_to_run("INTRAREG", ".", embryo_name, begin, real_parameters, end_time=end, compress_result=False)

            self.start_running(thread_number=1)
            real_parameters["uploaded_on_omero"] = (omero_config_file is not None)
            logFolder = "./INTRAREG/INTRAREG_" + str(real_parameters["EXP_INTRAREG"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(real_parameters, "intraregistration", ".",logFolder=logFolder)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during seg intrareg: " + str(strlog))
        if omero_config_file is not None:
            try:
                intra_folder = "INTRAREG/INTRAREG_" + str(parameters["EXP_INTRAREG"]) + "/POST/POST_" + str(
                                                parameters["EXP_POST"])
                self.upload_on_omero(omero_config_file, embryo_name, "INT_POST_" + str(parameters["EXP_POST"]),
                                        intra_folder, include_logs=True)
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error during intrareg upload: " + str(strlog))
            try:
                intra_fuse_folder = "INTRAREG/INTRAREG_" + str(
                    parameters["EXP_INTRAREG"]) + "/FUSE/FUSE_" + str(parameters["EXP_FUSE"])
                self.upload_on_omero(omero_config_file, embryo_name, "INT_FUSE_" + str(parameters["EXP_FUSE"]),
                                        intra_fuse_folder, include_logs=True)
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error during fuse upload: " + str(strlog))
            try:
                rec = None
                if "EXP_RECONSTRUCTION" in params_dict:
                    rec = "REC_" + params_dict["EXP_RECONSTRUCTION"].replace('"', '').replace("'", "")
                else:
                    if "EXP_SEG" in params_dict:
                        rec = "REC_" + params_dict["EXP_SEG"].replace('"', '').replace("'", "")
                intra_rec_folder = "INTRAREG/INTRAREG_" + str(
                    parameters["EXP_INTRAREG"]) + "/REC-MEMBRANE/"+rec
                self.upload_on_omero(omero_config_file, embryo_name, "INT_"+rec,intra_rec_folder, include_logs=False)
            except Exception as e:
                strlog = traceback.format_exc()
                print("Error during fuse upload: " + str(strlog))
        return real_parameters

    def compute_properties(self,parameters):
        embryo_name = parameters["embryo_name"]
        begin = parameters["begin"]
        end = parameters["end"]
        try:
            self.add_to_run("PROPERTIES", ".", embryo_name, begin, parameters, end_time=end, compress_result=False)
            self.start_running(thread_number=1)
            logFolder = "./INTRAREG/INTRAREG_" + str(parameters["EXP_INTRAREG"]).replace("'", "").replace('"', '') + "/LOGS/"
            self.writeStepToJson(parameters,"embryo_properties",".",logFolder=logFolder)
        except Exception as e:
            strlog = traceback.format_exc()
            print("Error during seg properties: " + str(strlog))

    def prod_segmentation(self,parameters):
        parameters["embryo_name"] = parameters["embryo_name"].replace('"','').replace("'","")
        if "begin" in parameters:
            parameters["begin"] = int(parameters["begin"])
        if "end" in parameters:
            parameters["end"] = int(parameters["end"])
        if not "EXP_SEG" in parameters:
            parameters["EXP_SEG"] = '01'
        real_parameters = self.start_segmentation(parameters)

        # Embryo dependant parameters
        if not "EXP_POST" in real_parameters:
            real_parameters["EXP_POST"] = '01'
        real_parameters = self.start_post_correction(real_parameters)
        if not "EXP_INTRAREG" in real_parameters:
            real_parameters["EXP_INTRAREG"] = '01'
        real_parameters = self.apply_intrareg(real_parameters)

        self.compute_properties(real_parameters)

    def downscale_fuse_folder(self,input_fuse,output_fuse,voxel_size=0.6):
        files = os.listdir(input_fuse)
        files.sort()
        if not os.path.isdir(output_fuse):
            os.makedirs(output_fuse)
        for file in files:
            # make sure file is an image
            if file.endswith(('.mha', '.nii', '.mha.gz', '.nii.gz', '.inr', '.inr.gz')):
                img_path = os.path.join(input_fuse, file)
                print("     -> " + str(img_path))
                img_t = os.path.join(output_fuse, file)
                if not os.path.isfile(img_t):
                    os.system("conda run -n astec applyTrsf -iso " + str(voxel_size) + " " + img_path + " " + img_t)
    def downscale_folder_seg(self,input_folder,output_folder,voxel_size,downscaled_fuse_folder):
        files = os.listdir(input_folder)
        files.sort()
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        fuse_folder = downscaled_fuse_folder
        for file in files:
            # make sure file is an image
            if file.endswith(('.mha', '.nii', '.mha.gz', '.nii.gz', '.inr', '.inr.gz')):
                img_path = os.path.join(input_folder, file)
                fuse_path = os.path.join(fuse_folder,file.replace("post","fuse"))
                img_o = os.path.join(output_folder, file)
                if not os.path.isfile(img_o):
                    print("     -> " + str(img_path))
                    os.system("conda run -n astec applyTrsf -interpolation nearest -ref " + str(fuse_path) + " -iso " + str(voxel_size) + " " + img_path + " " + img_o)

    def generate_suraces_array(self,path_lineage,contact_surfaces_ratio = 1,lineage_names=None):
        from AstecManager.libs.lineage import Get_Cell_Names
        from AstecManager.libs.data import get_id_t
        if lineage_names is None:
            lineage_names = path_lineage
        cell_values = {}
        names = Get_Cell_Names(lineage_names) #Array longid => name
        source = open(path_lineage)
        tree = ET.parse(source)
        tree = tree.getroot()
        lineage_elem = tree.find("cell_contact_surface")
        if lineage_elem is not None:
            for cell in lineage_elem.findall('cell'):#The subcell
                cell_id = cell.get('cell-id')
                tc,idc = get_id_t(cell_id)
                if idc == 1:
                    cell_name = "background"
                elif str(cell_id) in names.keys():
                    cell_name = names[str(cell_id)]
                else:
                    cell_name = str(cell_id)
                if idc != 1: #NO BACKGROUND
                    for subcell in cell.findall('cell'):#The subcell
                        subcell_id = subcell.get('cell-id')
                        subt,subid = get_id_t(subcell_id)
                        if subid == 1:
                            name_subcell = "background"
                        elif str(subcell_id) in names.keys():
                            name_subcell = names[str(subcell_id)]
                        else:
                            name_subcell = str(subcell_id)
                        subcell_child = subcell.text
                        if subcell_child is not None and subcell_child != "None":
                            subcell_contact_surfaces = str(subcell_child.replace("'", "").replace(" ", ""))
                        if not cell_name in cell_values:
                            cell_values[cell_name]  = {}
                        if not tc in cell_values[cell_name]:
                            cell_values[cell_name][tc] = []
                        cell_values[cell_name][tc].append((name_subcell,float(subcell_contact_surfaces)*contact_surfaces_ratio))
        return cell_values

    def get_pourcent_diff(self,v1,v2):
        if v1 < 0 or v2 < 0:
            print("No negative values in contact surfaces")
            return -1
        if v1 == 0 and v2 == 0:
            print("no contact surface ???")
            return -1
        return abs((v1-v2)/((v1+v2)/2)* 100)

    def plot_shifts(self,cells_shifts,embryo_name):
        import matplotlib.pyplot as plt
        import numpy as np
        if not os.path.isdir("./"+embryo_name+"/plots"):
            os.makedirs("./"+embryo_name+"/plots")
        for t in cells_shifts:
            mean = np.mean(cells_shifts[t])
            fig = plt.figure()
            display ={}
            display[t] = cells_shifts[t]
            plt.boxplot(cells_shifts[t])
            plt.ylabel("Distribution of contact surface shifts")
            plt.xlabel("Time point")
            plt.title("Contact surfaces shift between full and downscale for : "+str(embryo_name))
            fig.set_size_inches(18.5, 10.5)
            plt.savefig("./"+embryo_name+"/plots/shifts_t"+str(t)+".png")
            plt.clf()

    def plot_surfaces(self, half_surfaces_by_t, full_surfaces_by_t,embryo_name, means_by_t, pvalues_by_t):
        import matplotlib.pyplot as plt
        if not os.path.isdir("./"+embryo_name+"/plots"):
            os.makedirs("./"+embryo_name+"/plots")
        for t in half_surfaces_by_t:
            half_list = half_surfaces_by_t[t]
            full_list = full_surfaces_by_t[t]
            mean_shift = means_by_t[t]
            pvalue = pvalues_by_t[t]
            display ={}
            display["half"] = half_list
            display["full"] = full_list
            plt.boxplot(display.values(),labels=display.keys())
            plt.title("Contact surfaces full and half for : "+str(embryo_name))
            plt.ylabel("Distribution of surfaces of contact ")
            plt.xlabel("Time point")
            plt.legend(["Mean shift = "+str(mean_shift)])
            plt.tight_layout()
            plt.savefig("./"+embryo_name+"/plots/surfaces_t"+str(t)+".png")
            plt.clf()
            
    def plot_all_surfaces(self, half_surfaces, full_surfaces,embryo_name):
        import matplotlib.pyplot as plt
        if not os.path.isdir("./"+embryo_name+"/plots"):
            os.makedirs("./"+embryo_name+"/plots")
        display ={}
        display["half"] = half_surfaces
        display["full"] = full_surfaces
        plt.boxplot(display.values(),labels=display.keys())
        plt.title("Contact surfaces full and half for : "+str(embryo_name))
        plt.ylabel("Distribution of surfaces of contact ")
        plt.xlabel("Time point")
        plt.tight_layout()
        plt.savefig("./"+embryo_name+"/plots/all_surfaces.png")
        plt.clf()

    def plot_all_surfaces_distrib(self, full_surfaces,means,bins,embryo_name):
        import matplotlib.pyplot as plt
        if not os.path.isdir("./"+embryo_name+"/plots"):
            os.makedirs("./"+embryo_name+"/plots")
        fig, ax1 = plt.subplots()
        distrib_boundaries = [0,max(full_surfaces)]
        mean_boudaries = [0,max(means)]
        ax2 = ax1.twinx()
        l1 = ax1.hist(full_surfaces,bins=bins,label="Percentiles of contact surfaces stored by size")
        l2 = ax2.plot(means,color="red",label="Mean of distance between full resoltion and half resolution")
        plt.title("Contact surfaces distribution for : "+str(embryo_name))
        ax1.set_xlabel("Distribution of surfaces of contact")
        #ax1.set_ylim(distrib_boundaries)
        #ax2.set_ylim(mean_boudaries)
        ax1.set_ylabel("Number of contact surfaces")
        ax2.set_ylabel("Mean of distance between resolutions")
        plt.tight_layout()
        # ask matplotlib for the plotted objects and their labels
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)
        fig.set_size_inches(22.5, 10.5)
        plt.savefig("./"+embryo_name+"/plots/all_surfaces_distrib.png")
        plt.clf()


    def plot_pvalues(self,pvalues_by_t , embryo_name):
        import matplotlib.pyplot as plt
        if not os.path.isdir("./" + embryo_name):
            os.makedirs("./" + embryo_name)
        fig = plt.figure()
        plt.plot(pvalues_by_t.keys(),pvalues_by_t.values(), label='p-values', color='red')
        plt.title("P-values of contact surfaces distribution for : " + str(embryo_name))
        plt.ylabel("p-value ")
        plt.xlabel("Time point")
        plt.xticks(rotation = 45)
        fig.set_size_inches(18.5, 10.5)
        plt.savefig("./" + embryo_name + "/pvalues.png")
        plt.clf()
    def plot_means(self,means_by_t , std_by_t,embryo_name):
        import matplotlib.pyplot as plt
        if not os.path.isdir("./" + embryo_name):
            os.makedirs("./" + embryo_name)
        fig = plt.figure()
        plt.errorbar(means_by_t.keys(), means_by_t.values(), std_by_t.values(), linestyle='None', marker='^')
        plt.plot(means_by_t.keys(),means_by_t.values(), label='means', color='red')
        plt.title("Mean and standart deviation of shifts between surfaces contact for : " + str(embryo_name))
        plt.ylabel("Mean ")
        plt.xlabel("Time point")
        plt.xticks(rotation = 45)
        fig.set_size_inches(22.5, 10.5)
        plt.savefig("./" + embryo_name + "/means.png")
        plt.clf()
    def compare_surfaces_downscale(self,embryo_name,input_folder_prefix,input_folder_suffix,times,fuse_folder_prefix):
        from scipy.stats import spearmanr
        from matplotlib import pyplot as plt
        from AstecManager.libs.data import get_id_t
        from AstecManager.libs.lineage import Get_Cell_Names_Swapped,SaveTabToXMLInfo
        input_folder = input_folder_prefix+embryo_name+input_folder_suffix
        fuse_folder = input_folder_prefix+embryo_name+fuse_folder_prefix
        downscaled_folder = input_folder+"_06"
        downscaled_fuse_folder = fuse_folder+"_06"
        self.downscale_fuse_folder(fuse_folder,downscaled_fuse_folder)
        #fuse_template = os.path.join(fuse_folder,embryo_name+"_intrareg_fuse_t{:03d}.nii")
        self.downscale_folder_seg(input_folder,downscaled_folder,0.6,downscaled_fuse_folder)
        # Downscale folder intrareg/intrareg_01/post/post_machin into intrareg/intrareg_01/post/post_machin_down06
        # Recompute embryo properties in downscaled
        lineage_file = os.path.join(input_folder,embryo_name+"_intrareg_lineage.xml")
        lineage_file_down_names = os.path.join(downscaled_folder,embryo_name+"_intrareg_lineage.xml")
        lineage_file_down = os.path.join(downscaled_folder,embryo_name+"_intrareg_lineage_contact.xml")
        names = Get_Cell_Names_Swapped(lineage_file_down_names)
        os.system("cp "+str(lineage_file)+" "+str(lineage_file_down_names))
        if not os.path.isfile(lineage_file_down):
            self.generate_surface("INT_FUSE_01_V2_06", "CORR_INT_POST_V2_06", times[0], times[1], lineage_file_down, embryo_name, "01")
        # In full res , create new information with contact surface by name (for each cell, for each time , all surfaces at this time)
        surfaces_full = self.generate_suraces_array(lineage_file)
        surfaces_half = self.generate_suraces_array(lineage_file_down,lineage_names=lineage_file_down_names,contact_surfaces_ratio=4)
        #surfaces_half = self.generate_suraces_array(lineage_file_down,lineage_names=lineage_file_down_names)
        cell_to_cell_shift = {}
        max_shift = -100000
        shift_list_by_name = {}
        all_shifts = []
        shift_list_by_t = {}
        all_surfaces_full = []
        all_surfaces_half = []
        means_by_t = {}
        std_by_t = {}
        all_pair_full = []
        pvalues_by_t = {}
        half_surface_by_t = {}
        full_surface_by_t = {}
        for cell_name in surfaces_full:
            if not cell_name in cell_to_cell_shift:
                cell_to_cell_shift[cell_name] = {}
            for t in surfaces_full[cell_name]:
                if not t in cell_to_cell_shift[cell_name]:
                    cell_to_cell_shift[cell_name][t] = []
                for surfacepair in surfaces_full[cell_name][t]:
                    subcell_name = surfacepair[0]
                    subcell_surface = surfacepair[1]
                    down_subcell_surface = None
                    for pair in surfaces_half[cell_name][t]:
                        if pair[0] == subcell_name:
                            down_subcell_surface = pair[1]
                    if down_subcell_surface is None:
                        print("Error between surface of "+str(cell_name)+" and "+str(subcell_name)+" at time : "+str(t))
                    else :
                        all_surfaces_full.append(subcell_surface)
                        all_surfaces_half.append(down_subcell_surface)
                        if not str(t) in full_surface_by_t:
                            full_surface_by_t[str(t)] = []
                        full_surface_by_t[str(t)].append(subcell_surface)
                        if not str(t) in half_surface_by_t:
                            half_surface_by_t[str(t)] = []
                        half_surface_by_t[str(t)].append(down_subcell_surface)
                        shift = self.get_pourcent_diff(subcell_surface,down_subcell_surface)
                        if shift != -1:
                            all_shifts.append(shift)
                            if not cell_name in shift_list_by_name:
                                shift_list_by_name[cell_name] = []
                            shift_list_by_name[cell_name].append(shift)
                            if not str(t) in shift_list_by_t:
                                shift_list_by_t[str(t)] = []
                            shift_list_by_t[str(t)].append(shift)
                            cell_to_cell_shift[cell_name][t].append((subcell_name,shift,subcell_surface))
                            all_pair_full.append((subcell_name,shift,subcell_surface))
                            if shift > 0:
                                print("Shift exist for cell " + str(cell_name) +" and cell "+str(subcell_name)+" value = "+str(shift))
        idtocolor = {}
        for t in half_surface_by_t:
            half_list = half_surface_by_t[t]
            full_list = full_surface_by_t[t]
            res = spearmanr(half_list, full_list)
            pvalues_by_t[t] = res.pvalue
            means_by_t[t] = np.mean(shift_list_by_t[t])
            std_by_t[t] = np.std(shift_list_by_t[t])

        for t in means_by_t:
            if means_by_t[t] > max_shift:
                max_shift = means_by_t[t]
        for cell_name in cell_to_cell_shift:
            for t in cell_to_cell_shift[cell_name]:
                for pair in cell_to_cell_shift[cell_name][t]:
                    if pair[1] > max_shift:
                        #find idcell for pair[0]
                        if not cell_name in names:
                            if not cell_name in idtocolor or idtocolor[cell_name] < pair[1]:
                                idtocolor[cell_name] = pair[1]
                        else:
                            idscells =names[cell_name]
                            for idc in idscells:
                                tc,idcell = get_id_t(idc)
                                if str(tc)==str(t):
                                    if not idc in idtocolor or idtocolor[idc] < pair[1]:
                                        idtocolor[idc] = pair[1]




        #save info to xml
        SaveTabToXMLInfo(lineage_file_down_names,lineage_file_down_names,idtocolor,"float_shift_pourcent_contact_surfaces")
        min_all = min(all_surfaces_full)
        max_all = max(all_surfaces_full)
        sortd_surface = sorted(all_pair_full,key=lambda x: x[2])
        shift_by_bins = [None]*101
        means_by_bins = [None]*101
        linspacesurfaces=np.linspace(0,100,num=100,endpoint=True)
        current_index = 0
        current_count = 0
        max_by_pourcent = int(len(sortd_surface)/100)
        for pair in sortd_surface:
            subcellname = pair[0]
            shift = pair[1]
            surfacevalue = pair[2]
            if current_count >= max_by_pourcent:
                current_index += 1
                current_count = 1
                if shift_by_bins[current_index] is None:
                    shift_by_bins[current_index] = []
                shift_by_bins[current_index] = [shift]
            else:
                if shift_by_bins[current_index] is None:
                    shift_by_bins[current_index] = []
                shift_by_bins[current_index].append(shift)
                current_count += 1
        for i in range(0,len(shift_by_bins)):
            list_shift = shift_by_bins[i]
            if list_shift is not None:
                mean = np.mean(list_shift)
                means_by_bins[i] = mean
        self.plot_all_surfaces_distrib(all_surfaces_full,means_by_bins,linspacesurfaces,embryo_name)

        #self.plot_all_surfaces(all_surfaces_half,all_surfaces_full,embryo_name)
        #self.plot_surfaces(half_surface_by_t,full_surface_by_t,embryo_name, means_by_t, pvalues_by_t)
        #self.plot_pvalues(pvalues_by_t,embryo_name)
        #self.plot_means(means_by_t,std_by_t,embryo_name)
        fig = plt.figure()
        fig.set_tight_layout(False)


        # find a plot (box plot for each cell) ??
        # Spearman ? statistical validation

    def compute_all_surfaces_downscale(self):
        input_folder_prefix = "/Users/bgallean/Data/"
        input_folder_suffix = "/INTRAREG/INTRAREG_01/POST/POST_CORR_INT_POST_V2"
        fuse_folder_prefix = "/INTRAREG/INTRAREG_01/FUSE/FUSE_INT_FUSE_01_V2"
        names = ["Astec-pm1","Astec-pm3","Astec-pm4","Astec-pm5","Astec-pm7","Astec-pm8","Astec-pm9"]
        #names = ["Astec-pm1"]
        times = [(1,192),(0,89),(0,89),(0,89),(4,83),(1,88),(1,63)]
        for i in range(0,len(names)):
            self.compare_surfaces_downscale(names[i],input_folder_prefix,input_folder_suffix,times[i],fuse_folder_prefix)
    def upload_data(self,parameters):
        omero_config_file = get_omero_config(parameters)
        project_name = parameters["project_name"]
        dataset_name = parameters["dataset_name"]
        input_folder = parameters["input_folder"]
        if omero_config_file is None:
            print("OMERO config file is not bound, unable to upload")
            exit()
        if not os.path.isfile(omero_config_file):
            print("Unable to find OMERO config file , unable to upload")
            exit()
        self.upload_on_omero(omero_config_file, project_name, dataset_name, input_folder,
                                include_logs=True)
    def printEmbryoMetadata(self):
        printMetadata("./")