import os
import numpy as np
from nibabel import load as loadnii
from skimage.io import imread as imreadTIFF
import tifffile as tf
import time
def isfile(filename):
    if os.path.isfile(filename):
        return True
    elif os.path.isfile(filename+".gz"):
        return True
    elif os.path.isfile(filename+".zip"):
        return True
    return False


def imsave(filename, img, verbose=True,voxel_size=(1,1,1)):
    """Save a numpyarray as an image to filename.

    The filewriter is choosen according to the file extension.

    :Parameters:
     - `filename` (str)
     - `img` (|numpyarray|)
    """

    if verbose:
        print(" --> Save " + filename)
    if filename.find('.inr') > 0 or filename.find('.mha') > 0:
        from AstecManager.libs.ImageHandling import SpatialImage
        from AstecManager.libs.ImageHandling import imsave as imsaveINR
        return imsaveINR(filename, SpatialImage(img),voxel_size=voxel_size)
    elif filename.find('.nii') > 0:
        import nibabel as nib
        from nibabel import save as savenii
        new_img = nib.nifti1.Nifti1Image(img, None)
        new_img.header.set_zooms(voxel_size)
        im_nifti = savenii(new_img, filename)
        return im_nifti
    else:
        from skimage.io import imsave as imsaveTIFF
        if filename.endswith(".gz"):
            filename = filename.replace(".gz", "")
            im = imsaveTIFF(filename, img)
            os.system("cd " + os.path.dirname(filename) + ";gzip " + os.path.basename(filename))
            return im
    return None

def TIFFTryParseVoxelSize(filename):
    """Tries to parse voxel size from TIFF image. default return is (1,1,1)

    :Parameters:
     - `filename` (str)

    :Returns Type:
        |tuple|
    """

    vsx = 1
    vsy = 1
    vsz = 1
    with tf.TiffFile(filename) as tif:

        if len(tif.pages) > 0:
            page = tif.pages[0]
            for tag in page.tags:
                if tag.name == "XResolution":
                    if len(tag.value) >= 2:
                        vsx = round(tag.value[1] / tag.value[0], 5)
                if tag.name == "YResolution":
                    if len(tag.value) >= 2:
                        vsy = round(tag.value[1] / tag.value[0], 5)
                if tag.name == "ImageDescription":
                    subtags = tag.value.split("\n")
                    for t in subtags:
                        if "spacing" in t:
                            if len(t.split("=")) >= 2:
                                vsz = t.split("=")[1]
    vsize = (vsx, vsy, vsz)
    return vsize



def imread(filename, verbose=True,voxel_size=False):
    """Reads an image file completely into memory

    :Parameters:
     - `filename` (str)
     - `verbose` (bool)
     - `voxel_size` (bool)

    :Returns Type:
        |numpyarray|
    """
    if verbose:
        print(" --> Read " + filename)
    if not isfile(filename):
        if verbose:
            print("Miss "+filename)
        return None
    try:

        if filename.find("mha") > 0:
            from AstecManager.libs.ImageHandling import imread as imreadINR
            data, vsize = imreadINR(filename)
            if voxel_size:
                return np.array(data), vsize
            else:
                return np.array(data)
        elif filename.find('.inr') > 0:
            from AstecManager.libs.ImageHandling import imread as imreadINR
            data,vsize = imreadINR(filename)
            if voxel_size:
                return np.array(data),vsize
            else:
                return np.array(data)
        elif filename.find('.nii') > 0:
            im_nifti = loadnii(filename)
            if voxel_size:
                sx, sy, sz = im_nifti.header.get_zooms()
                vsize = (sx, sy, sz)
                data = np.array(im_nifti.dataobj).astype(np.dtype(str(im_nifti.get_data_dtype())))
                #data = np.swapaxes(data,0,2)
                return data,vsize
            else :
                data = np.array(im_nifti.dataobj).astype(np.dtype(str(im_nifti.get_data_dtype())))
                return data
        elif filename.find("h5") > 0:
            import h5py
            with h5py.File(filename, "r") as f:
                return np.array(f["Data"])
        else:

            imtiff = imreadTIFF(filename)
            imtiff = np.swapaxes(imtiff,0,2)
            if voxel_size:
                vsize = TIFFTryParseVoxelSize(filename)
                return imtiff,(float(vsize[0]), float(vsize[1]), float(vsize[2]))
            else:
                return imtiff
    except Exception as e:
        if verbose:
            print(" Error Reading " + filename)
            print(str(e))
            if filename.endswith("gz") or filename.endswith("zip"):
                temp_path = "TEMP" + str(time.time())
                while os.path.isdir(temp_path):  # JUST IN CASE OF TWISE THE SAME
                    temp_path = "TEMP" + str(time.time())
                os.system("mkdir -p " + temp_path)
                os.system("cp " + filename + " " + temp_path)
                filename = os.path.join(temp_path, os.path.basename(filename))
                os.system("gunzip " + filename)
                filename = filename.replace('.gz', '')
                if voxel_size:
                    arrayim,vsize = imread(filename,verbose,voxel_size)
                    if temp_path is not None:
                        os.system("rm -rf " + temp_path)
                    return arrayim,vsize
                else :
                    arrayim = imread(filename,verbose,voxel_size)
                    if temp_path is not None:
                        os.system("rm -rf " + temp_path)
                    return arrayim

            return None
        # quit()
    return None
class Cell:
    id = -1
    t = -1
    mothers = []
    daughters = []

    def __init__(self,id_cell,time_cell):
        self.id = id_cell
        self.t = time_cell
        self.mothers = []
        self.daughters = []

    def add_mother(self,cell):
        #print("mother len before : " + str(len(self.mothers)))
        #print("add mother for cell : "+str(self.t)+","+str(self.id)+" for mother : "+str(cell.t)+","+str(cell.id))
        if self.mothers is None:
            self.mothers = []
        if not cell in self.mothers:
            self.mothers.append(cell)
        #print("mother len after : " + str(len(self.mothers)))
        cell.add_daughter(self)


    def add_daughter(self,cell):
        #print("daughters len before : " + str(len(self.daughters)))
        #print("add daughter for cell : " + str(self.t) + "," + str(self.id) + " for mother : " + str(cell.t) + "," + str(cell.id))
        if self.daughters is None:
            self.daughters = []
        if not cell in self.daughters:
            self.daughters.append(cell)

def is_image(imagepath):
    """
        Returns true if file is a readable image or not

        Parameters
        --------
        path : basestring
            Path to file to test
        Returns
        --------
        boolean
            is file image or not
    """
    return os.path.isfile(imagepath) and (imagepath.endswith(".mha") or imagepath.endswith(".nii") or imagepath.endswith(".inr") or imagepath.endswith(".mha.gz") or imagepath.endswith(".nii.gz") or imagepath.endswith(".inr.gz"))

def get_id_t(idl):
    """ Return the cell t,id

            Parameters
            ----------
            idl : int
                Cell information id
            Returns
            -------
            t : int
                Cell time point
            id : int
                Cell id
    """
    t=int(int(idl)/(10**4))
    cell_id=int(idl)-int(t)*10**4
    return t,cell_id

def get_longid(t,idc):
    """ Return the cell information id

            Parameters
            ----------
            t : int
                Cell time point
            idc : int
                Cell id

            Returns
            -------
            id : int
                Cell information id format {ttt0iiii}
    """
    if t==0 or  t=="0":
        return idc
    return t*10**4+idc

