## This library has been created to automatize and help users to segment using ASTEC software.
It will include tools to:
* enhance the data (contour computation, etc ...)
* manage the data (download and upload to distant storage, automatic compression, reduce size)
* segment the data (examples , etc ...)
* plot properties of the embryo data


# Table of contents
1. [Installation](#install)
2. [Update](#update)
3. [Fusion](#fusion)
4. [Fusion parameters tuning](#fusion-parameters-test)
5. [Fusion final run](#fusion-final-run)

## Install

you need to install conda on your computer
you can find a guide to install conda [here](/https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) 

Now that conda is installed,  open a new terminal, and type the following lines : 

`conda create -n AstecManager -c ome python=3.6 zeroc-ice36-python omero-py` \
`conda activate AstecManager` \
`python3.6 -m pip install AstecManager` \
`python3.6 -m pip install matplotlib`\
`python3.6 -m pip install h5py`\
`python3.6 -m pip install opencv-contrib-python`
`python3.6 -m pip install dataclasses`

AstecManager tool is now installed, with all the needed libraries.

## Update

Often, the tool will be updated to add features, and debug the existing ones. 

* To update the tool, you can simply start a terminal in the astecmanager folder and run :

`conda activate AstecManager` \
`python3.6 -m pip install AstecManager --upgrade` \

## Data Manager Integration

To store the data for further work and archives , the team uses a data manager called OMERO.
In the following pipeline, you will be able to upload the different data produced to OMERO , automatically.

In order to upload, you first need to create a file on your computer, somewhere no one can access and that you should not share !

The file should contain the following lines : 

```
host=adress.to.omero.instance
port=omero.port (usually 4064)
group=your team group
secure=True
java_arg=java
login=your omero login
password=your omero password
```

Save this file with the name you want, I prefer to use : omero_config.txt , and than copy the complete path to the file somewhere you can access.

In the following steps, to upload a data you produce, you will need to copy this path to the parameter "omero_config_file". I will explain this step everytime it will be needed.


## Fusion


The most crucial part of this process is combining the images, and it needs to be done quickly. You should begin this step right after copying the large Raw Images, and try to finish it as soon as you can.

These Raw Images are very large, roughly 3 gigabytes each. This means that if you're working with one time point, it will use up about 12 gigabytes of computer memory. Think about it this way: if you're dealing with an embryo at 300 different time points and you have multiple channels of images, your Raw Images folder could take up as much as 2 to 3 terabytes of space on your computer's hard drive.

Additionally, the Raw Images often have a significant amount of background information, which takes up a lot of memory. This background includes unnecessary data.

The fusion step is designed to address the problems we've just talked about:

- It keeps the most valuable information from each camera angle to create an isotropic image. An isotropic image means that it has the same characteristics, like intensity, across all regions.

- It reduces the memory needed for a single time point from around 12 gigabytes to a more manageable 500 megabytes.

- It also trims the image around the embryo, cutting out the excessive background and keeping only the essential information.

For more details about this step , please follow [this link](https://astec.gitlabpages.inria.fr/astec/astec_fusion.html#fusion-method-overview)

I would advise to split fusion in 2 steps 
* A test step where you will find the best parameters for this specific dataset.
* A production step where you will apply the best parameters to the complete dataset.

* Your folder hierarchy should look like this, before starting the fusion

``` 
     embryo name
         └───RAWDATA
             │───stack_0_channel_0_obj_left
             │───stack_0_channel_0_obj_right
             │───stack_1_channel_0_obj_left
             │───stack_1_channel_0_obj_right
             └───... (more if you have another channel)
             
```

#### Fusion parameters test
The fusion parameters test is a needed step , considering the high number of parameters needed for fusion , we can't take the time to try them one by one, on a large time sequence.

The test step is split in 2 sub steps : 

- 1st , a test fusion using the parameter set that is correct for the acquisition we have here
- If it's not working, 4 sets of parameter that could be correct 
- If it's still not working , you're invited to explore the fusion parameters documentation [here](https://astec.gitlabpages.inria.fr/astec/astec_parameters.html#astec-fusion-parameters)

To start the fusion test step , please download the template parameters file from this [link](https://seafile.lirmm.fr/f/1bbbadd9158d4e21858f/) , and save it to your embryo folder. Your file architecture should look like this : 
``` 
     embryo name
     │   └───RAWDATA
     │       │───stack_0_channel_0_obj_left
     │       │───stack_0_channel_0_obj_right
     │       │───stack_1_channel_0_obj_left
     │       │───stack_1_channel_0_obj_right
     │       └───... (more if you have another channel)
     └── start_fuse_test.py
```

And then , you should edit it to bind the good parameter for your embryo : 


```
parameters["embryo_name"] = "'<name>'" : replace <name> with the name of your embryo folder
parameters["begin"]=1 : for test, should be set to the only time point , and be the same than "end"
parameters["end"]=1 : for test, should be set to the only time point , and be the same than "begin"
parameters["user"] = "'<UI>'" : for every step , will be used to store an history of the data,<UI>  should be replaced by experimentator name and surname first letters
```

Setting up those parameters should be enough to start the first fusion test. In order to do so , open a terminal in the embryo folder ;

``` 
     embryo name   <-- Open a terminal here
     │   └───RAWDATA
     │       │───stack_0_channel_0_obj_left
     │       │───stack_0_channel_0_obj_right
     │       │───stack_1_channel_0_obj_left
     │       │───stack_1_channel_0_obj_right
     │       └───... (more if you have another channel)
     └── start_fuse_test.py
```

and then you can start the process with those commands : 

`conda activate AstecManager` \
`python3.6 start_fuse_test.py` 

This step will take a few minutes to run, and will generate a fusion image in this directory : 
``` 
     │──embryo name
     │    │───RAWDATA
     │    │    └─── ...
     │    └───FUSE
     │        └─── FUSE_01_test
     │           │─── embryo_name_fuse_t040.nii
     │           └─── ... 
     └─ start_fuse_test.py
``` 
###### Verify fusion 

Now that you generated the first fusion test , you need to verify the quality of the fusion. For this , we have to visually check if the generated image is correct, this can be done using
Fiji (here is a link to a documentation on how to use Fiji #TODO ). Here is an example of what a wrong fusion rotation may look like , which is the first error you can find : 


| Example of correct fusion | Example of fusion with wrong rotation |
|:-------------------------:|:-------------------------------------:|
| ![](doc_images/file.jpg)  |       ![](doc_images/file.jpg)        |

If the rotation seems good , you will need to check in the temporary images generated by the fusion , if the different steps were well parametered


Inside each fusion folder , you can find a folder called "XZSECTION_XXX" where "XXX" is the time point fused. 
Inside the folder , you will see 4 images : 

- embryoname_xyXXXX_stack0_lc_reg.mha
- embryoname_xyXXXX_stack0_lc_weight.mha
- embryoname_xyXXXX_stack0_rc_reg.mha
- embryoname_xyXXXX_stack0_rc_weight.mha
- embryoname_xyXXXX_stack1_lc_reg.mha
- embryoname_xyXXXX_stack1_lc_weight.mha
- embryoname_xyXXXX_stack1_rc_reg.mha
- embryoname_xyXXXX_stack1_rc_weight.mha

|       Left-cam stack 0 reg + weighting       |       Stack cameras matching        |       Stack 0 and 1 matching       |
|----------------------------------------------|-------------------------------------|------------------------------------|
| ![](doc_images/fuse_extraction_lcstack0.png) | ![](doc_images/leftandrightcam.png) | ![](doc_images/stacksmatching.png) |

On the left image  of the table you can see that the registration image (left), is matching the weighting used for the computation. It means that the weighting is correct.
On the middle image , you can see that the left camera and right camera of the same stack is matching.
On the right image, you can see that both stacks images are matching , so the fusion will be correct.

If the xzsection registration (the images containing <_reg> inside their names) are matching , and the weighing seem to be coherent , you can skip to final fusion step. 

If the xzsection registration (the images containing <_reg> inside their names) do not seem to match , either withing the same stack , or between the 2 different stacks, it means that you will need to explore 2 more parameters.
We made this step easier by creating a mode that tests automatically all 4 possibles combination for the parameters.

Modify your "start_fusion_test.py" file to change this line : 

```
manager.test_fusion(parameters,parameter_exploration=False)
```

to 

```
manager.test_fusion(parameters,parameter_exploration=True)
```

and then start your test step again , the same way you started it before : 

`conda activate AstecManager` \
`python3.6 start_fuse_test.py` 


if the xzsection weighting is not matching the image correctly, you may need to change the weighting function used in the fusion computation. In order to do this , modify your "start_fusion_test.py" file to add this line:
```
parameters["fusion_weighting"]= set it to "'uniform'" , "'ramp'" or "'corner'"
```
BEFORE the final line : 

```
manager.test_fusion(...
```

When you changed the file , you can run the fusion test again

`conda activate AstecManager` \
`python3.6 start_fuse_test.py` 

#### Final fusion

Now that you have finished the fusion test step , found the parameters that gives you a good result , and verified them on the fusion image itself + the temporary images generated in the XZSECTION
you can start the final fusion by downloading the parameter file here : 

Save it to the embryo folder, in the same location where you saved the test file , and start by editing it : 

```
parameters["embryo_name"] = "'<name>'" : replace <name> with the name of your embryo folder
parameters["begin"]=1 : for fusion, should be set to the first time point of the sequence
parameters["end"]=100 : for fusion, should be set to the last time point of the sequence
parameters["user"] = "'<UI>'" : for every step , will be used to store an history of the data,<UI>  should be replaced by experimentator name and surname first letters

parameters["number_of_channels"] = 1 : change this to the number of channel in the raw images acquisition. The same fusion will be applied to all channels

parameters["omero_config_file"]= "'/path/to/the/omero/config/file'" : if you want to upload the result images of the fusion, you can enter the path to your omero configuration file. If you didn't create the omero
file , please read the "Data Manager Integration" section of this documentation. After fusion, a new dataset will be created in the embryo project on OMERO (created if it doesn't exist) , and will contain all of the fusion images
```

Finally , you will need to modify the following lines : 

```
parameters["fusion_strategy"]= '"hierarchical-fusion"'
parameters["acquisition_orientation"]= '"right"'
```

If the fusion test ran fine during the test step , and you didn't need to start the 4 fusion test exploration, you can leave the lines as they are.
If not , please update them with the parameters that worked the best among the 4 tests fusion. 

  - if the FUSE_01_left_direct was the good one , change the parameters to :
    ```
    parameters["fusion_strategy"]= '"direct-fusion"'
    parameters["acquisition_orientation"]= '"left"'
    ```
  - if the FUSE_01_left_hierarchical was the good one , change the parameters to :
    ```
    parameters["fusion_strategy"]= '"hierarchical-fusion"'
    parameters["acquisition_orientation"]= '"left"'
    ```
  - if the FUSE_01_right_direct was the good one , change the parameters to :
    ```
    parameters["fusion_strategy"]= '"direct-fusion"'
    parameters["acquisition_orientation"]= '"right"'
    ```
  - if the FUSE_01_right_hierarchical was the good one , change the parameters to :
    ```
    parameters["fusion_strategy"]= '"hierarchical-fusion"'
    parameters["acquisition_orientation"]= '"right"'
    ```

And finally , if you added other parameters to the test file (for example weighing method modification) , please provide the corresponding lines in the final fusion file too. 

When all of this is ready , you can start the final fusion. Open a terminal in the embryo folder and run the following lines 

`conda activate AstecManager` \
`python3.6 start_fuse_production.py` 

The computation of the fusion step will take a few hours, depending on the number of time point in the embryo , and the number of channels to fuse. When finished , multiple new data will be generated : 
First, you can delete the following files and folders :
- folder FUSE/FUSE_01_left_direct
- folder FUSE/FUSE_01_left_hiearchical 
- folder FUSE/FUSE_01_right_direct 
- folder FUSE/FUSE_01_right_hiearchical 
- and the 2 python files "fuse_test.py", "fuse_post.py"

The final folder architecture after fusion will be this one :

``` 
experiment folder 
└───embryo specie
    │──embryo name
    │   │───INTRAREG
    │   │    └─── INTRAREG_01_TEST
    │   │          └─── MOVIES
    │   │               └─── FUSE
    │   │                   └─── FUSE_01
    │   │                       └─── embryo_name_intrareg_fuse_tbegin-tend_xy0XXX.mha
    │   │───RAWDATA
    │   │    └─── ...
    │   └───FUSE
    │       └─── FUSE_01
    │          │─── embryo_name_fuse_t000.nii
    │          │─── embryo_name_fuse_t001.nii
    │          └─── ... 
```

### Fusion verification

To verify the final fusion , we will use the image (with mha format) located in the following folder : "embryo_name/INTRAREG/INTRAREG_01_TEST/MOVIES/FUSE/FUSE_01/" . 

After opening the image in Fiji , you will see that it is a slice of the fusion image , where the Z axis (the slider at the bottom of image) correspond to this slide through time. 
To validate the fusion through time , make sure that the image orientation , and the fusion registration remains coherent, even if the embryo is slightly different, or may have moved between the 2 times.

|                     ...                      |               Time X                |             Time X +1              | ... |
|:--------------------------------------------:|:-----------------------------------:|:----------------------------------:|:---:|
| ![](doc_images/fuse_extraction_lcstack0.png) | ![](doc_images/leftandrightcam.png) | ![](doc_images/stacksmatching.png) |     |
(example of correct fusion through the time sequence)


|                     ...                      |               Time X                |             Time X +1              | ... |
|:--------------------------------------------:|:-----------------------------------:|:----------------------------------:|:---:|
| ![](doc_images/fuse_extraction_lcstack0.png) | ![](doc_images/leftandrightcam.png) | ![](doc_images/stacksmatching.png) |     |
(example of error during fusion through the time sequence)


## Backgrounds _(optional)_

To compute backgrounds, we will use a deep learning tool trained by the MorphoNet team. It will need a special power to run , and should be installed on a specific computer
In the team , we use a computer called loki. To get access to Loki using ssh , first ask the team.

To start background  , you first need to get the identifier of your dataset on omero.
For this goes to omero , find your project and the dataset (green folder) , and look at the properties on the right.
You will find a line called "Dataset id : ". Copy the number on the right 
##### Run in a terminal , line by line the following :


`ssh loki.crbm.cnrs.fr` \
`cd /data/MorphoDeep/morphodeep/morphodeep/Process/` \
`python3 Compute_Background_From_Omero.py -d id_dataset_omero -m FusedToBackground`

After the computation , you will find a new dataset inside the omero project , called Background_name_of_fusion_dataset

There is no troubleshooting for this section , if you have a problem , you need to find a team member.

When the background computation is done , and all the images are available on the data manager, you will have to download them on the computer that will compute the next steps. 
In order to do so , please download the following parameters file :  , in any folder. 

Please edit it : 
```
parameters["omero_config_file"] = None : replace None by the omero config you created before , if you didn't please refer to section "Data Manager Integration"
parameters["embryo_name"] = "" : write the name of the omero project of your dataset between the " " (should be the embryo name) 
# DATASET NAME ON OMERO
parameters["dataset_name"] = "" : write the name of the omero dataset of your dataset between the " " (should be Background_FUSE_01) 
# PATH OF THE OUTPUT FOLDER
parameters["output_folder"] = "" : write the path to the download folder. For backgrounds , shound be ( /path/to/embryo_name/BACKGROUND/<name of the omero dataset>/ )
```

Open a terminal where the download parameters file is , and start the download by running : 

`conda activate AstecManager` \
`python3.6 download_from_omero.py`

When the download has finished, you should fine the images in the folder corresponding to <parameters["output_folder"]> 

## Contours _(optional)_

This section need to have the background (above) finished to work. 
This code will automatically compute the contours images, that will be used by ASTEC later. Contour has been designed as an extra input data for the segmentation process , to prevent the missing cells at the external part of the embryo (which is the first source of errors in our data)
The contours are computed by created by smoothing and increasing the thickness of the edge between background and embryo.

Please download the following parameters file , and store it inside your embryo folder : link

Edit the file like this : 

```
parameters["embryo_name"] = "" : Name of your embryo folder
parameters["EXP_BACKGROUND"] = "Background_FUSE_01" : replace <Background_FUSE_01> with the name of the folder where you downloaded background images (if it's different)
parameters["omero_config_file"] = None : replace None by the omero config you created before , if you didn't please refer to section "Data Manager Integration" if you want to upload contours to the data manager automatically
parameters["user"] = "UI" : for every step , will be used to store an history of the data,<UI>  should be replaced by experimentator name and surname first letters
```

Open a terminal where the download parameters file is , and start the download by running : 

`conda activate AstecManager` \
`python3.6 compute_contours.py`

After running , the code will create this folder "/embryoname/CONTOUR/CONTOUR_RELEASE_3/"  , where the contour image are stored

There is no troubleshooting for this section , if you have a problem , you need to find a team member

## First time point segmentation 

The segmentation process for our data is based on the propagation. Using the previous time step segmentation , the algorithm compute new segmentations , and then detect the cell divisions ( or not ) to compute the lineage. 
In order to start the process , it is needed to have a first time point segmentation, that SHOULD be empty of any segmentation errors. 
We now have 2 systems to compute the first time point segmentation :  

### MARS 

MARS is the standard segmentation algorithm used for the first time point with our data.
To start MARS algorithm , please download the parameter file and store it in your embryo folder : link 

Edit it : 

```
parameters["embryo_name"] = "'name'": replace <name> with the name of your embryo folder
parameters["begin"]=1 : replace '1' with the first time point of the fusion sequence
parameters["end"]=1 :  replace '1' with the first time point of the fusion sequence (HAS TO BE EQUAL TO parameters["begin"])
parameters["resolution"] = 0.3 : Only change this if you are working in half resolution (it should be 0.6 with half resolution)
parameters["EXP_FUSE"] = "'01'" : Name of the fusion exp for the intensity images 
parameters["use_contour"] = True : Should be 'True' to use the contour for the segmentation of the first time point, 'False' otherwise 
parameters["user"]= "'UI'" : for every step , will be used to store an history of the data,<UI>  should be replaced by experimentator name and surname first letters

```

Open a terminal in your embryo folder , and start the MARS by running : 

`conda activate AstecManager` \
`python3.6 start_mars_test.py`

The code will generate 2 segmentations of the first time point, the difference between the being how the intensities of the input images are integrated together to get an enhanced images. 

The embryo folder hierarchy should look like this : 

``` 
experiment folder 
└───embryo specie
    │──embryo name
    │   │───SEG
    │   │    │─── SEG_mars_add
    │   │    │   │─── LOGS
    │   │    │   └─── embryo_name_mars_t000.nii
    │   │    │   
    │   │    │─── SEG_mars_max
    │   │    │   │─── LOGS
    │   │    │   └─── embryo_name_mars_t000.nii
    │   │───INTRAREG
    │   │    └─── ...
    │   │───RAWDATA
    │   │    └─── ...
    │   └───FUSE
    │       └─── ... 
```

To compare the two MARS segmentations generated by this step , follow the steps detailed in the [First time point verification section](#firstverif) for each segmentation.

### MorphoNet Cellpose integration 

MorphoNet application has acquired a new plugin , taking in input the intensity image (fusion) of a time point , and generating a segmentation using a deep learning model.

To install MorphoNet Standalone, please refer to the MorphoNet documentation for application by [clicking here](https://morphonet.org/help_standalone) 

Then add the intensity images to your MorphoNet local datasets following the documentation [here](https://morphonet.org/help_standalone#add_local) 

Use the MorphoNet curation module to generate a segmentation from your intensity images. To use the curation menu , please read the documentation [here](https://morphonet.org/help_app?menu=curations)

The documentation for CellPose plugin, used to generate the segmentations , can be found [here](https://morphonet.org/help_app?menu=curations#cellpose)

After generating the segmentation , you can curate all the errors using the plugins detailed [here](https://morphonet.org/help_curation) , or follow the curation example documentation [here](https://morphonet.org/help_curation)


<h3 id="firstverif"> First time point verification </h3>


(link to morphonet plot help)

(link to morphonet plot segmentation over raw images help)

- find the different errors 
- Choose the image with less undersegmentation / missing cells
### First time point curation 

(linking to the morphonet curation help )

### First time point storage 


## Data downscaling _(optional)_ : Fusions , Contours and First time point

The following steps of the pipeline can be really long (the segmentation can take 2 weeks depending on your data). 
We found a way to accelerate the computation by downscaling the fusion images by 2. This step reducing the image quality , we will keep this trick only for the exploration of the different parameters , not the final segmentation computation.

