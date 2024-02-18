import os
import numpy as np
from AstecManager.libs.data import imread,imsave
from scipy import ndimage as nd
def fill_image(imagein, folderin):
    from skimage import morphology
    arraynp, vsize = imread(os.path.join(folderin, imagein), voxel_size=True)
    im_bin = (arraynp < 150)
    try :
        im_bin = morphology.remove_small_holes(im_bin)
    except :
        print("skimage morphology not found")
    return im_bin, vsize


def apply_morphological_changes(condition, type, structural_connectivity=3):
    # binary structure 6 connectivity  : nd.generate_binary_structure(3, 1)
    struct1 = nd.generate_binary_structure(3, structural_connectivity)
    if type == "twice-d":
        return np.logical_xor(nd.binary_dilation(condition, struct1, iterations=2),
                              nd.binary_dilation(condition, struct1, iterations=1))
    elif type == "noerod":
        return np.logical_xor(nd.binary_dilation(condition, struct1, iterations=1), condition)
    else:
        return np.logical_xor(condition,
                              nd.binary_dilation(condition, struct1, iterations=2))


def generate_contour(imagein, arraydata, voxelsize, folderout, type, sigma=1, connectivity=3,target_normalization_max=255):
    result = np.zeros(arraydata.shape, dtype=np.float64)
    im_cyto_erod = apply_morphological_changes(arraydata, type, structural_connectivity=connectivity)
    result[im_cyto_erod == True] = 1
    #imsave(os.path.join(folderout, imagein.replace("_background", "_result")), result, voxel_size=voxelsize)
    smoothed = nd.gaussian_filter(result, sigma=sigma)
    smoothed *= target_normalization_max
    del im_cyto_erod
    imsave(os.path.join(folderout, imagein.replace("_background", "_contour")), smoothed.astype(np.uint16), voxel_size=voxelsize)
    del result


def compute_contour(embryo_folder,backgroundinput,reducvoxelsize=0.6,target_normalization_max=255,correction_vsize=False,user="KB"):
    background_folders = os.path.join(embryo_folder, "BACKGROUND/")
    folder_raw = os.path.join(background_folders, backgroundinput)
    contour_suffix ="RELEASE_"+str(reducvoxelsize).split('.')[1]
    if not os.path.exists(folder_raw):
        print("Input images path does not exist")
        exit()
    if not os.path.exists(folder_raw):
        print("Input templates path does not exist")

    res = []
    for path in os.listdir(folder_raw):
        # check if current path is a file
        if os.path.isfile(os.path.join(folder_raw, path)) and ".mha" in path or ".nii" in path:
            res.append(path)


    res.sort()
    # Correction of networks voxel size errors
    if correction_vsize:
        print("Correction of the image voxel size")
        for image in res:
            print("     - " + str(image))
            os.system("conda run -n astec setVoxelSize " + str(os.path.join(folder_raw, image)) + " "+str(reducvoxelsize)+" "+str(reducvoxelsize)+" "+str(reducvoxelsize))

    folder_contour = os.path.join(embryo_folder, "CONTOUR/CONTOUR_"+str(contour_suffix)+"/")


    if not os.path.exists(folder_contour):
        os.makedirs(folder_contour)

    print("Filling and creating contour for normal size")
    for image in res:
        print("     -" + str(image))
        image_filled, voxelsize = fill_image(image, folder_raw)
        #imsave(os.path.join(folder_contour, image.replace("_background", "_filled")), image_filled.astype(np.uint16),
        #       voxel_size=voxelsize)
        generate_contour(image, image_filled, voxelsize, folder_contour, "normal", sigma=2, connectivity=1,target_normalization_max=target_normalization_max)
    return folder_contour



