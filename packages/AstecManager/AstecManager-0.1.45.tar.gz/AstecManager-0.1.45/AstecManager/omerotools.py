import subprocess

import omero
import ezomero
import os
import numpy as np
from os.path import join,isfile
from threading import Thread
from multiprocessing import cpu_count

def run_command(command):
    splitted = command.split(" ")
    subcommand = []
    for s in splitted:
        subcommand.append(s.replace('"',''))
    subprocess.run(subcommand)

def is_image(file_name):
    splited_name = file_name.split('.')
    return splited_name[1] is not None and splited_name[1] in ['mha','nii','inr']

class process_upload_image(Thread):
    def __init__(self, dataset_id,image_path,omeroinstance):
        super(process_upload_image, self).__init__()
        self.image_path = image_path
        self.dataset_id = dataset_id
        self.omeroinstance = omeroinstance

    def run(self):
        self.omeroinstance.add_image_to_dataset_java(self.image_path,self.dataset_id)

class process_upload_annotation_file(Thread):
    def __init__(self, dataset_id,file_path,omeroinstance):
        super(process_upload_annotation_file,self).__init__()
        self.image_path = file_path
        self.dataset_id = dataset_id
        self.omeroinstance = omeroinstance

    def run(self):
        self.omeroinstance.add_file_to_dataset(self.dataset_id,self.image_path)

class process_download(Thread):
    def __init__(self, folder_out, image_id, omeroinstance):
        super(process_download, self).__init__()
        self.folder_out = folder_out
        self.image_id = image_id
        self.omeroinstance = omeroinstance

    def run(self):
        self.image_name_compress = self.omeroinstance.get_image_object(self.image_id).getName()
        self.image_name = join(self.folder_out, self.image_name_compress.replace(".gz", ""))
        if isfile(self.image_name):
            print(" --> already download " + self.image_name)
        else:
            self.omeroinstance.export_image(self.image_id, self.image_name)

def parse_parameters_file(filename):
    """Parse file lines and split along the "="


    Parameters
    ----------
    filename : string
        path to the file

    Returns
    -------
    Dict
        dict where each key is the left part of the splitted line, values being the corresponding sright part

    """
    result = {}
    try:
        f = open(filename, "r+")
    except:
        print("Unable to open file" + str(filename))
        return None
    else:
        lines = f.readlines()
        for line in lines:
            if line != "" and line != "\n" and not line.startswith("#"):
                tab = line.replace("\n", "").split("=")
                result[tab[0]] = tab[1]
        f.close()
    return result

class connect:
    def __init__(self, login=None, passwd=None, server=None, port=None, group=None, secure=False,file_path=None):
        if file_path is None:
            self.params_connect(login,passwd,server,port,group)
        else :
            self.file_connect(file_path)

    def params_connect(self,login=None, passwd=None, server=None, port=None, group=None, secure=False):
        if login is not None:
            self.login = login

        self.secure = False
        if secure is not None:
            self.secure = secure

        if passwd is not None:
            self.o_passwd = passwd

        if server is not None:
            self.server = server

        if port is not None:
            self.port = port

        if group is not None:
            self.group = group

        self.omero_cmd="omero"

        self.connection = None
        self.connected = False
        self.o_connect()

    def file_connect(self,file_path):
        parameters = parse_parameters_file(file_path)

        self.login = ""
        if parameters['login'] is not None:
            self.login = parameters['login']
        self.secure = False
        if parameters['secure'] is not None:
            self.secure = bool(parameters['secure'])
        self.o_passwd = ""
        if parameters['password'] is not None:
            self.o_passwd = parameters['password']
        self.server = ""
        if parameters['host'] is not None:
            self.server = parameters['host']
        self.port = -1
        if parameters['port'] is not None:
            self.port = int(parameters['port'])
        self.group = ""
        if parameters['group'] is not None:
            self.group = parameters['group']
        self.omero_cmd = "omero"

        self.connection = None
        self.connected = False
        self.o_connect()

    def o_connect(self):
        self.connection = ezomero.connect(user=self.login, group=self.group, password=self.o_passwd, host=self.server,
                                          port=self.port, secure=self.secure)
        if self.connection is None:
            self.connected = False
        else:
            self.connected = True
            #self.connection.c.enableKeepAlive(60)
            #self.connection.keepAlive()
        return self.connected

    def o_reconnect(self):
        self.connected = False
        try:
            self.connection.connect()
            self.connected = True
        except Exception as e:
            print("ERROR during omero connection " + str(e))
            raise e
        return self.connection

    def o_close(self):
        if self.connection is not None:
            self.connected = False
            self.connection.close()



    ###
    #
    # To start this script , please provide a parameters file , using the following syntax : python3 download_omero_set.py parameters_file_path/file.txt
    #
    ###
    def download_omero_set(self, project_name, dataset_name, folder_output):
        cpuCount = cpu_count()
        maxNumberOfThreads =3
        threads = []
        found = False
        found_path = False
        run_command("mkdir " + str(folder_output).replace('"','').replace(",",""))
        for p in self.list_projects():
            if not found and p.getName().lower() == project_name.lower():
                found = True
                for path in p.listChildren():
                    if not found_path and path.getName().lower() == dataset_name.lower():
                        found_path = True
                        list_files = self.get_images_ids(path.getId())
                        for image in list_files:
                            if len(threads) >= maxNumberOfThreads:  # Waitfor a free process if too much threads
                                tc = threads.pop(0)
                                tc.join()
                            tc = process_download(folder_output.replace('"','').replace(",",""), image, self)
                            tc.start()
                            threads.append(tc)
                        while len(threads) > 0:
                            tc = threads.pop(0)
                            tc.join()

    def upload_omero_set(self,project_name,dataset_name,input_folder,mintime=None,maxtime=None,tag_list=None,include_logs=False):
        cpuCount = cpu_count()
        maxNumberOfThreads = 3
        imagefiles = [f for f in os.listdir(input_folder) if
                      isfile(join(input_folder, f)) and is_image(f)]
        logfiles = []
        if os.path.isdir(os.path.join(input_folder,"LOGS")):
            logfiles = [f for f in os.listdir(os.path.join(input_folder,"LOGS")) if
                          isfile(join(input_folder, f))]
        nonimagefiles = [f for f in os.listdir(input_folder) if
                         isfile(join(input_folder, f)) and not is_image(f)]

        embryolist = self.list_projects()
        dataset = None
        project = None
        if embryolist is not None:
            for o_emb in embryolist:
                if o_emb.getName()==project_name:
                    project = o_emb
                    for path in self.get_datasets(o_emb.getid()):
                        if path.getName() == dataset_name:
                            dataset = path

        if project is None:
            # create it
            project_id = self.create_project(project_name)
            # store in project
            project = self.get_project_by_id(project_id)
        else:
            project_id = project.getId()
        # find dataset id
        if dataset is None:
            print("Didn't find dataset with name : "+str(dataset_name))
            dataset_id = self.create_dataset(dataset_name, project_id=project_id)
        else :
            dataset_id = dataset.getId()
        # if doesnt exist , create it
        # for each image
        # start thread and upload image

        image_name_list = self.get_images_filename(dataset_id)

        threads = []
        for image_f in imagefiles:
            if len(threads) >= maxNumberOfThreads:  # Waitfor a free process if too much threads
                tc = threads.pop(0)
                tc.join()
            if not image_f in image_name_list:
                tc = process_upload_image(dataset_id, os.path.join(input_folder, image_f), self)
                tc.start()
                threads.append(tc)
        while len(threads) > 0:
            tc = threads.pop(0)
            tc.join()

        # for each non image
        # start thread and upload it like attachment
        threads = []
        for file_f in nonimagefiles:
            if len(threads) >= maxNumberOfThreads:  # Waitfor a free process if too much threads
                tc = threads.pop(0)
                tc.join()
            tc = process_upload_annotation_file(dataset_id, os.path.join(input_folder, file_f), self)
            tc.start()
            threads.append(tc)
        while len(threads) > 0:
            tc = threads.pop(0)
            tc.join()
        if include_logs:
            threads = []
            for file_f in logfiles:
                if len(threads) >= maxNumberOfThreads:  # Waitfor a free process if too much threads
                    tc = threads.pop(0)
                    tc.join()
                tc = process_upload_annotation_file(dataset_id, os.path.join(os.path.join(input_folder,"LOGS"), file_f), self)
                tc.start()
                threads.append(tc)
            while len(threads) > 0:
                tc = threads.pop(0)
                tc.join()

        # add KVP minTime
        if maxtime is not None:
            if not self.has_kvp(project, "maxTime", int(maxtime)):
                self.add_kvp(project, "maxTime", int(maxtime))
        # add KVP maxTime
        if maxtime is not None:
            if not self.has_kvp(project, "minTime", int(mintime)):
                self.add_kvp(project, "minTime", int(mintime))
        if tag_list is not None:
            for tag in tag_list:
                self.add_tag(project,tag)
    def get_images_ids(self, dataset_id):
        """
        Retrive list of image ids associated to the dataset_id

        Parameters
        ----------
        path_id : int
            id of the dataset in omero to get image from

        Returns
        -------
        List
            List of the ids of image linked to this dataset

        """
        return ezomero.get_image_ids(self.connection, dataset=dataset_id)

    def get_image_object(self, image_id):
        """
        retrieve OMERO image object for the given image_id

        Parameters
        ----------
        image_id : int
            id of the image in omero to get object

        Returns
        -------
        Omero Image Object
            return the image object from omero (without data)

        """
        image_obj, pixels = ezomero.get_image(self.connection, image_id, no_pixels=True)
        return image_obj

    def get_image_data(self, image_id):
        """
        Retrieve pixels for the given image id

        Parameters
        ----------
        image_id : int
            id of the image in omero to get object

        Returns
        -------
        Numpy Array
            return the pixels of the image stored in OMERO (ordered by axis XYZTC)

        """
        image_obj, pixels = ezomero.get_image(self.connection, image_id, dim_order="xyztc")
        return pixels

    def add_file_to_dataset(self, dataset_id, file):
        """
        Add the file from path to the dataset given by its id as an annotation

        Parameters
        ----------
        dataset_id : int
            id of the dataset to link annotation file to
        file : string
            path to the file to add

        """
        namespace = omero.constants.metadata.NSCLIENTMAPANNOTATION
        ezomero.post_file_annotation(self.connection, "Dataset", dataset_id, file, namespace)

    def add_image_to_dataset_java(self, image_path, dataset_id):
        """
        Upload image using path to a dataset by its id , through Java Omero Lib (jar)

        Parameters
        ----------
        image_path : string
            path to the image to upload
        dataset_id : int
            id of the dataset to link image file to


        """
        #First Login
        run_command(self.omero_cmd + ' -s ' + self.server + ' -u ' + self.login + ' -w ' + self.o_passwd + ' login')
        return run_command(
            self.omero_cmd  + ' import --skip minmax --skip thumbnails --skip upgrade -d ' + str(
                dataset_id) + ' ' + image_path)

    def add_image_to_dataset_cli(self, image_path, dataset_id):
        """
        Upload image using path to a dataset by its id , through Java Omero Lib (jar)

        Parameters
        ----------
        image_path : string
            path to the image to upload
        dataset_id : int
            id of the dataset to link image file to


        """
        from omero.cli import CLI
        args = ["login"]
        args += ["-s",self.server]
        args += ["-u", self.login]
        args += ["-w",self.o_passwd]
        cli = CLI()
        cli.load_plugins()
        cli.invoke(args)
        # First Login
        #run_command(self.omero_cmd + ' -s ' + self.server + ' -u ' + self.login + ' -w ' + self.o_passwd + ' login')
        args = ["import"]
        args += ["--skip","minmax"]
        args += ["--skip","thumbnails"]
        args += ["--skip","upgrade"]
        args += ["-d", dataset_id]
        args += [image_path]
        cliupload = CLI()
        cliupload.load_plugins()
        cliupload.invoke(args)
        #return run_command(
        #    self.omero_cmd + ' import --skip minmax --skip thumbnails --skip upgrade -d ' + str(
        #        dataset_id) + ' ' + image_path)
    def imread(self, filename, verbose=True):
        """Reads an image file completely into memory

        :Parameters:
         - `filename` (str)

        :Returns Type:
            |numpyarray|
        """
        if verbose:
            print(" --> Read " + filename)
        if filename.find('.inr') > 0 or filename.find('mha') > 0:
            # from morphonet.ImageHandling import SpatialImage
            from morphonet.ImageHandling import imread as imreadINR
            data = imreadINR(filename)
            return np.array(data)
        elif filename.find('.nii') > 0:
            from nibabel import load as loadnii
            im_nifti = loadnii(filename)
            return np.array(im_nifti.dataobj).astype(np.dtype(str(im_nifti.get_data_dtype())))
        else:
            from skimage.io import imread as imreadTIFF
            return imreadTIFF(filename)
        return None

    def add_image_to_dataset_ezomero(self, image_path, dataset_id, source_image_id=None):
        """
         Upload image using path to a dataset by its id , through EZOmero python library. Copy existing image if source_image_id param is not None

         Parameters
         ----------
         image_path : string
             path to the image to upload
         dataset_id : int
             id of the dataset to link image file to
        source_image_id : int (optional)
            if not None, id of the original image that will be source for the new image


         """
        image_np = np.asarray(self.imread(image_path))
        if source_image_id is not None:
            ezomero.post_image(self.connection, image_np, image_path.split('/')[-1], dataset_id=dataset_id)
        else:
            ezomero.post_image(self.connection, image_np, image_path.split('/')[-1], dataset_id=dataset_id, source_image_id=source_image_id)

    def add_image_to_dataset(self, image_path, dataset_id, source_image_id=None):
        """
         Upload image using path to a dataset by its id. Copy existing image if source_image_id param is not None
         NOTE : this function is just a bridge to ezomero upload, but it should be kept in case we change the system

         Parameters
         ----------
         image_path : string
             path to the image to upload
         dataset_id : int
             id of the dataset to link image file to
        source_image_id : int (optional)
            if not None, id of the original image that will be source for the new image
         """
        if self.omero_cmd == "" or self.omero_cmd is None:
            self.add_image_to_dataset_ezomero(image_path,dataset_id)
        else :
            self.add_image_to_dataset_java(image_path, dataset_id)

    def export_image_with_java(self, image_id, path_image):
        """
        Download image by it's ID to a path , using Java Omero Library (jar)

        Parameters
        ----------
        image_id : int
            id of the image in omero to get object
        path_image : string
            path where to store the image to (including image name)

        Returns
        -------
        bool
            True if download is a success , false otherwise

        """
        # print("export_image_with_java lien Download "+str(Imageid))
        cmd = self.omero_cmd+' -s ' + self.server + ' -u ' + self.login + ' -w ' + self.o_passwd + ' -p ' + str(
            self.port) + ' download Image:' + str(image_id) + ' "' + os.path.dirname(os.path.abspath(path_image))+'"'
        run_command(cmd)
        if not os.path.isfile(path_image):
            print("--> ERROR Omero Import ID " + str(image_id))
            return False
        return True


    def export_image(self, image_id, path_image):
        """
        Download image by it's ID to a path

        Parameters
        ----------
        image_id : int
            id of the image in omero to get object
        path_image : string
            path where to store the image to (including image name)

        Returns
        -------
        bool
            True if download is a success , false otherwise

        """
        # print(" export_image"+str(Imageid))
        java_succes = self.export_image_with_java(image_id, path_image)
        if java_succes:
            return True
        else:
            print("---> Unable to use java command to download image")
            return False
            print("---> trying using ezomero")
            self.save_image_to_file_ezomero(image_id, path_image)
            """
            if not os.path.isfile(path_image):
                try:
                    self.save_image_to_file_omeropy(Imageid, path_image)
                except:
                    print("Unable to download image file")
            """

    def imsave(self, filename, img):
        """Save a numpyarray as an image to filename.

        The filewriter is choosen according to the file extension.

        :Parameters:
         - `filename` (str)
         - `img` (|numpyarray|)
        """

        if filename.find('.inr') > 0 or filename.find('mha') > 0:
            from morphonet.ImageHandling import SpatialImage
            from morphonet.ImageHandling import imsave as imsaveINR
            return imsaveINR(filename, SpatialImage(img))
        elif filename.find('.nii') > 0:
            import nibabel as nib
            from nibabel import save as savenii
            print("new save")
            new_img = nib.Nifti1Image(img, np.eye(4))
            im_nifti = savenii(new_img, filename)
            return im_nifti

        else:
            from skimage.io import imsave as imsaveTIFF
            return imsaveTIFF(filename, img)
        return None

    def save_image_to_file_ezomero(self, image_id, file_path):
        """
        Download image by it's ID to a path, using ezomero

        Parameters
        ----------
        image_id : int
            id of the image in omero to get object
        file_path : string
            path where to store the image to (including image name)

        """
        pixels = self.get_image_data(image_id)
        self.imsave(file_path, pixels)


    def get_data_from_image_path(self, image_name):
        """
        retrieve time and clean path from an image_name

        Parameters
        ----------
        image_name : string
            image_name

        Returns
        -------
        int
            time point for the image
        string
            cleaned_image_name

        """
        import re
        image = image_name
        s = "###."
        splitted_name = image.split(".")
        time = int(splitted_name[0][-3:len(splitted_name[0])])
        new_path = re.sub('\d\d\d\.', s, image)
        return time, new_path

    def get_project_by_name(self,project_name):
        """
        Get OMERO project object using name

        Parameters
        ----------
        project_name : string
            target project name

        Returns
        -------
        Omero Project Object or None
            Project Object retrieved from OMERO

        """
        projects = self.list_projects()
        for p in projects:
            if p.getName().lower() == project_name.lower():
                return p
        return None

    def get_project_by_id(self,project_id):
        """
        Get OMERO project object using id

        Parameters
        ----------
        project_id : id
            target project id

        Returns
        -------
        Omero Project Object or None
            Project Object retrieved from OMERO

        """
        projects = self.list_projects()
        for p in projects:
            if p.getid() == project_id:
                return p
        return None

    def get_datasets(self,project=None):
        """
        Retrieve list of datasets for a defined project, if project is None look for Orphans datasets

        Parameters
        ----------
        project : project or None
            project to list dataset from

        Returns
        -------
        List
            List of the omero Datasets objects

        """
        if project is not None:

            p = self.connection.getObject("Project", project)
            datasets = p.listChildren()
        else:
            datasets = self.connection.listOrphans("Dataset")
        return datasets

    def get_dataset_by_name(self,dataset_name,project=None):
        """
          Retrieve the dataset object by its name for a defined project, if project is None look for Orphans datasets

          Parameters
          ----------
          dataset_name : string
            name to look for in datasets

          project : project or None
              project to list dataset from

          Returns
          -------
          OMERO dataset object or None
              Found dataset in OMERO

          """
        datasets = self.get_datasets(project=project)
        for p in datasets:
            if p.getName().lower() == dataset_name.lower():
                return p
        return None

    def get_dataset_by_id(self,dataset_id,project=None):
        """
          Retrieve the dataset object by its id for a defined project, if project is None look for Orphans datasets

          Parameters
          ----------
          dataset_id : int
            id to look for in datasets
          project : project or None
              project to list dataset from

          Returns
          -------
          OMERO dataset object or None
              Found dataset in OMERO

          """
        datasets = self.get_datasets(project=project)
        for p in datasets:
            if p.getid() == dataset_id:
                return p
        return None

    def create_dataset(self,dataset_name,project_id=None,dataset_description=None):
        """
          Create a dataset in OMERO , attached to a project or not (given by its id) , with provided description or not

          Parameters
          ----------
          dataset_name : string
            name of the dataset to create
          project_id : int
            if exists, link the created dataset to this project
          dataset_description : string
            if exists, add the description to the dataset


          Returns
          -------
          OMERO dataset object
              return the dataset in omero if successfuly created

          """
        return ezomero.post_dataset(self.connection,dataset_name,project_id=project_id,description=dataset_description)

    def create_project(self,project_name,project_description=None):
        """
          Create a project in OMERO , with provided description or not

          Parameters
          ----------
          project_name : string
            name of the project to create
          project_description : string
            if exists, add the description to the dataset

          Returns
          -------
          OMERO project object
              return the project in omero if successfuly created

          """
        return ezomero.post_project(self.connection,project_name,description=project_description)

    def list_projects(self):
        """
            Return a list of all projects currently available for the connection

            Returns
            -------
            List
                return the projects object found

            """
        if self.connection is not None:
            return self.connection.listProjects()

    def create_tag(self, tag, description):
        """
          Create a tag in OMERO if it does not exist already

          Parameters
          ----------
          tag : string
            name of the tag to create
          description : string
            description of the tag

          Returns
          -------
          OMERO tag object
              return the tag (created or already existing)

          """
        tag_ann = self.get_tag(tag)  # Check if the tag already exyst
        if tag_ann is None:  # Create a new TAG
            print(" --> Create tag " + tag)
            tag_ann = omero.gateway.TagAnnotationWrapper(self.connection)
            tag_ann.setValue(tag)
            if description is not None:
                tag_ann.setDescription(description)
            tag_ann.save()
        return tag_ann

    def get_tag_name(self,connection,tag_id):
        """
            Retrieve name for a tag id

            Parameters
            ------------
            connection : omero connection objects

            tag_id : int
                id of the tag

            Returns
            -----------

            name : basestring
                name of the tag
        """
        return ezomero.get_tag(connection,tag_id)

    def has_dataset_tag_id(self,connection,tag_id,dataset_id):
        """
            Verify if a dataset has a tag by its id

            Parameters
            -----------

            connection : omero connection objects

            tag_id : int
                id of the tag

            dataset_id : int
                id of the dataset

            Returns
            --------

            flag : bool
                True if dataset has tag , False otherwise
        """
        list_ids = self.get_tag_id_list(connection,"Dataset",dataset_id)
        return tag_id in list_ids

    def has_dataset_tag_name(self,connection,tag_name,dataset_id):
        """
            Verify if a dataset has a tag by its name

            Parameters
            -----------

            connection : omero connection objects

            tag_name : string
                name of the tag

            dataset_id : int
                id of the dataset

            Returns
            --------

            flag : bool
                True if dataset has tag , False otherwise
        """
        list_names = self.get_tag_name_list(connection,"Dataset",dataset_id)
        return tag_name in list_names

    def has_project_tag_id(self,connection,tag_id,project_id):
        """
            Verify if a project has a tag by its id

            Parameters
            -----------

            connection : omero connection objects

            tag_id : int
                id of the tag

            project_id : int
                id of the project

            Returns
            --------

            flag : bool
                True if project has tag , False otherwise
        """
        list_ids = self.get_tag_id_list(connection,"Project",project_id)
        return tag_id in list_ids

    def find_associated_rawdata_path(self, project):
        """
            Find the rawdata path in the project, and retrieve it

            Parameters
            --------------
            project_id : int
                id of the project object

            Returns
            --------

            dataset : OMERO dataset object
                Raw Images dataset object if found , None otherwise
        """
        final_dataset = None
        p = self.connection.getObject("Project", project.getId())
        datasets = p.listChildren()
        for dataset_obj in datasets:
            if self.has_set_tag(dataset_obj, "fuse"):
                final_dataset = dataset_obj
                break
        return final_dataset


    def has_project_tag_name(self,connection,tag_name,project_id):
        """
            Verify if a project has a tag by its name

            Parameters
            -----------

            connection : omero connection objects

            tag_name : string
                name of the tag

            project_id : int
                id of the project

            Returns
            --------

            flag : bool
                True if project has tag , False otherwise
        """
        list_names = self.get_tag_name_list(connection,"Project",project_id)
        return tag_name in list_names

    def get_tag_id_list(self,connection,object_type,id):
        """
            Get list of tags id for an object

            Parameters
            -----------
            connection : omero connection object

            object_type : basestring
                type of the object to retrieve tags from ("Image","Dataset", "Project")

            id : int
                id of the object with type object_type

            Returns
            -----------
            id_list : list of int

        """
        list_ids = ezomero.get_tag_ids(connection,object_type,id)
        list_name = []
        for tag_id in list_ids:
            list_name.append(self.get_tag_name(connection,tag_id))
        return list_name

    def get_tag_name_list(self,connection,object_type,id):
        """
            Get list of tags name for an object

            Parameters
            -----------
            connection : omero connection object

            object_type : basestring
                type of the object to retrieve tags from ("Image","Dataset", "Project")

            id : int
                id of the object with type object_type

            Returns
            -----------
            name list : list of string

        """
        list_ids = ezomero.get_tag_ids(connection,object_type,id)
        list_name = []
        for tag_id in list_ids:
            list_name.append(self.get_tag_name(connection,tag_id))
        return list_name

    def get_tag(self, name):
        """
          Get a tag in OMERO

          Parameters
          ----------
          name : string
            name of the tag to find

          Returns
          -------
          OMERO tag object or None
              return the tag if found

          """
        listTag = self.connection.getObjects("Annotation")
        for t in listTag:
            #if t.OMERO_TYPE == omero.model.TagAnnot  #AttributeError: module 'omero.model' has no attribute 'TagAnnot'
            if t.getValue() == name:
                return t
        return None

    def get_user_id(self, username):
        """
          Get user id by it's username

          Parameters
          ----------
          username : string
            name of the user to find

          Returns
          -------
          int
              id of the user found
        """
        return ezomero.get_user_id(self.connection, username)

    def get_connected_user_id(self):
        """
          Get user id for current logged in user

          Returns
          -------
          int
              id of the user connected
        """
        return self.get_user_id(self.login)

    def get_annotation(self, project, map_ann):
        """
          Get annotation instance on the project using annotation object

          Parameters
          ----------
          project : OMERO project object
            project to list annotation from
          map_ann : OMERO annotation object
            annotation to find on this project

          Returns
          -------
          OMERO annotation instance or None
              Annotation instance if found on the dataset, None otherwise
        """
        try:
            for ann in project.listAnnotations():
                if ann.getId() == map_ann.getId():
                    return ann
        except ValueError:
            print(" PyOmero : Error getting annotation " + ValueError)
        return None

    def remove_annotations_startswith(self, project, startswith):
        """
          Remove all annotation from project that begins with a name expression

          Parameters
          ----------
          project : OMERO project object
            project to remove annotation from
          startswith : string
            name start of the annotation to remove

        """
        try:
            annotations_toremove = []
            for ann in project.listAnnotations():
                if ann is not None and type(ann) == omero.gateway.TagAnnotationWrapper and ann.getValue().startswith(
                        startswith):
                    annotations_toremove.append(ann)
            for ann in annotations_toremove:
                self.connection.deleteObjects('Annotation', [ann.id], wait=True)
        except ValueError:
            print(" PyOmero : Error remove annotation " + ValueError)

    def get_all_annotations(self, project):
        """
          Get annotations instance on the project

          Parameters
          ----------
          project : OMERO project object
            project to list annotation from

          Returns
          -------
          List
              Annotation instances found on the project
        """
        annotations = []
        try:
            for ann in project.listAnnotations():
                annotations.append(ann)
        except ValueError:
            print(" PyOmero : Error getting annotation " + ValueError)
        return annotations

    def add_tag(self, dataset, tag, description=None):
        """
          Add tag to dataset using tag name , create it if needed

          Parameters
          ----------
          dataset : OMERO project object
            dataset to list annotation from
          tag : string
            tag name to add

        """
        if tag.strip() == "":
            print(" --> tag is empty")
            return False
        tag_ann = self.create_tag(tag, description)  # Check if the tag already exyst
        ann = self.get_annotation(dataset, tag_ann)
        if ann is None:
            print(" --> link tag " + tag + " to " + dataset.getName())
            dataset.linkAnnotation(tag_ann)
        else:
            print(" --> tag " + tag + " already linked to " + dataset.getName())

    def has_set_tag(self, dataset, tag_name):
        """
          check if given dataset has a tag

          Parameters
          ----------
          dataset : OMERO dataset object
            dataset to list annotation from
          tag_name : string
            name of the tag

          Returns
          -------
          bool
              True if dataset has the tag , false otherwise
        """
        target_object = self.connection.getObject("Dataset", dataset.getId())
        morphonet_tag_id = -1
        for tag_v in self.connection.getObjects("TagAnnotation", attributes={"textValue": tag_name}):
            morphonet_tag_id = tag_v.getId()
        # print(str(morphonet_tag_id.getId()))
        for ann in target_object.listAnnotations():
            if ann.getId() == morphonet_tag_id:
                return True
        return False

    def list_tags(self,dataset):
        """
          list all tags for dataset

          Parameters
          ----------
          dataset : OMERO dataset object
            dataset to list annotation from

          Returns
          -------
          List
              All the tags for the dataset
        """
        target_object = self.connection.getObject("Dataset", dataset.getId())
        return target_object.listAnnotations()

    def list_tags_name(self,dataset):
        """
          list all tags names for dataset

          Parameters
          ----------
          dataset : OMERO dataset object
            dataset to list annotation from

          Returns
          -------
          List
              All the tags name for the dataset
        """
        names = []
        target_object = self.connection.getObject("Dataset", dataset.getId())
        for t_o in target_object.listAnnotations():
            if t_o is not None and t_o.getName() is not None:
                names.append(t_o.getName())
        return names

    def remove_tag(self, dataset, name ):
        """
          Remove tag from the dataset by name

          Parameters
          ----------
          dataset : OMERO dataset object
            dataset to list annotation from
          name : string
            name of the tag

          Returns
          -------
          bool
              True if dataset has the tag , false otherwise
        """
        tag_ann = self.get_tag(name)
        if tag_ann is None:
            return False
        ann = self.get_annotation(dataset, tag_ann)
        if ann is None:
            return False
        self.connection.deleteObjects('Annotation', [ann.id], wait=True)
        print(" --> tab " + name + " removed ")
        return True


    def get_file(self, dataset, file_to_download, path_to_write=""):
        """
          Remove tag from the dataset by name

          Parameters
          ----------
          dataset : OMERO dataset object
            dataset to get file annotation from
          file_to_download : string
            name of the file
          path_to_write : string
            folder where to write file in

          Returns
          -------
          bool
              True if file has been written , false otherwise
        """
        try:
            for ann in dataset.listAnnotations():
                if isinstance(ann, omero.gateway.FileAnnotationWrapper):
                    if ann.getFileName() == os.path.basename(file_to_download):
                        # print("File ID:", ann.getFile().getId(), ann.getFile().getName(), "Size:", ann.getFile().getSize())
                        print(" Download Annotation File " + file_to_download)
                        file_path = os.path.join(path_to_write, ann.getFileName())
                        with open(str(file_path), 'wb') as f:
                            # print("\nDownloading file to", file_path, "...")
                            for chunk in ann.getFileInChunks():
                                f.write(chunk)
                        # print("File downloaded!")
                        return True
        except ValueError:
            print(" PyOmero : Error getting file " + ValueError)
        return False


    def get_images_filename(self, dataset_id):
        """
        Retrive list of image filename associated to the dataset_id

        Parameters
        ----------
        path_id : int
            id of the dataset in omero to get image from

        Returns
        -------
        dictionnary
            filename as key
            id as value

        """
        list_images = {}
        for im_id in self.get_images_ids(dataset_id):
            f = self.get_image_object(im_id).getName()
            list_images[f] = im_id
        return list_images
    def list_files(self, dataset):
        """
          List annotations file for dataset

          Parameters
          ----------
          dataset : OMERO dataset object
            dataset to get file annotation from

          Returns
          -------
          List
              List of all annotation files for the dataset
        """
        list_annotation = []
        try:
            for ann in dataset.listAnnotations():
                if isinstance(ann, omero.gateway.FileAnnotationWrapper):
                    list_annotation.append(ann.getFileName())
        except ValueError:
            print(" PyOmero : Error listing file " + ValueError)
        return list_annotation

    def add_kvp(self, project, key_data, value_data):
        """
          Add a key value pair for the project

          Parameters
          ----------
          project : OMERO project object
            project to add kvp to
          key_data : string
            key of the pair
          key_value : any
            value of the pair
        """
        map_ann = self.create_kvp(key_data, value_data)
        ann = self.get_annotation(project, map_ann)
        if ann is None:
            project.linkAnnotation(map_ann)
        # else:
        #    print(" --> link already exist " + key_data + " to " + project.getName())

    def create_kvp(self, key_data, value_data):
        """
          Create key vale pair

          Parameters
          ----------
          key_data : string
            key of the pair
          key_value : any
            value of the pair

          Returns
          -------
          KVP Object
              The key value pair created or found
        """
        try:
            t = self.get_kvp(key_data, value_data)
            if t is not None:
                return t

            # Create KVP
            map_ann = omero.gateway.MapAnnotationWrapper(self.connection)
            namespace = omero.constants.metadata.NSCLIENTMAPANNOTATION
            map_ann.setNs(namespace)
            map_ann.setValue([[key_data, value_data]])
            map_ann.save()
            return map_ann
        except ValueError:
            print(" PyOmero : Error creating key value pair " + ValueError)
        return None

    def get_kvp(self, key_data, value_data):
        """
          Get key value pair

          Parameters
          ----------
          key_data : string
            key of the pair
          key_value : any
            value of the pair

          Returns
          -------
          KVP Object or None
              The key value pair found, None otherwise
        """
        try:
            listKV = self.connection.getObjects("Annotation")
            for t in listKV:
                if t.OMERO_TYPE == omero.model.MapAnnotationI:
                    tkv = t.getValue()[0]
                    if tkv[0] == key_data and tkv[1] == value_data:
                        return t
        except ValueError:
            print(" PyOmero : Error has get key value pair " + ValueError)
        return None

    def get_ks(self, key_data):
        listKS = []
        try:
            listKV = self.connection.getObjects("Annotation")
            for t in listKV:
                if t.OMERO_TYPE == omero.model.MapAnnotationI:
                    tkv = t.getValue()[0]
                    if tkv[0] == key_data:
                        listKS.append(t)
        except ValueError:
            print(" PyOmero : Error has get key annotation " + ValueError)
        return listKS

    def has_kvp(self, project, key_data, value_data):
        """
          Check if project has key value pair

          Parameters
          ----------
          project : OMERO project object
            project to check KVP from
          key_data : string
            key of the pair
          value_data : any
            value of the pair

          Returns
          -------
          bool
              True if project has KVP false otherwise
        """
        try:
            t = self.get_kvp(key_data, value_data)
            if t is None:  # KV does not exist at all
                return False

            ann = self.get_annotation(project, t)
            if ann is None:  # KV does not exist at all
                return False
        except ValueError:
            print(" PyOmero : Error has key pair value" + ValueError)
        return True

    def get_v(self, project, key_data):
        """
          Get value for a KVP in a given project

          Parameters
          ----------
          project : OMERO project object
            project to check KVP from
          key_data : string
            key of the pair

          Returns
          -------
          any
              Value of the KVP in this project
        """
        try:
            listKS = self.get_ks(key_data)
            for k in listKS:
                ann = self.get_annotation(project, k)
                if ann is not None:
                    tkv = ann.getValue()[0]
                    return tkv[1]
        except ValueError:
            print(" PyOmero : Error getting value of key pair " + ValueError)
        return None


