import os
import glob
from osgeo import osr, gdal
import logging
from pathlib import Path

def create_vrt(wdir:str, fout:str='out.vrt', format:str='tif'):
    """
    Agglomération de tous les fichiers .tif dans un layer virtuel .vrt
    """
    curdir = os.getcwd()
    os.chdir(wdir)

    if not fout.endswith('.vrt'):
        fout+='.vrt'

    myvrt = gdal.BuildVRT(os.path.join(wdir,fout) , glob.glob(os.path.join(wdir,'*.'+format)))
    myvrt = None

    os.chdir(curdir)

def _get_relative_path(path:Path, base:Path):
    """
    Get relative path from base to path
    """
    if base in path.parents:
        return path.relative_to(base)
    elif path.parent in base.parents:
        pos=''
        for curpos in range(len(base.relative_to(path.parent).parents)):
            pos += '../'
        return Path(pos+path.name)

def create_vrt_from_files(files:list[Path]=[], fout:Path='assembly.vrt'):
    """
    Agglomération de tous les fichiers énumérés dans files dans un layer virtuel .vrt
    """
    if isinstance(fout, str):
        fout = Path(fout)

    # retain current working directory
    oldcwd = os.getcwd()
    # change working directory to the parent of the output file
    os.chdir(fout.parent)
    # work with relative paths
    myvrt = gdal.BuildVRT(str(fout.with_suffix('.vrt').name) , [str(_get_relative_path(file, fout.parent)) for file in files])
    # close the dataset -- force to write on disk
    myvrt = None
    # restore working directory
    os.chdir(oldcwd)

def create_vrt_from_files_first_based(files:list[Path]=[], fout:Path='assembly.vrt'):
    """
    Agglomération de tous les fichiers énumérés dans files dans un layer virtuel .vrt

    Restreint l'emprise et force la résolution sur le premier fichier listé
    """
    if isinstance(fout, str):
        fout = Path(fout)

    first = files[0]
    raster:gdal.Dataset
    raster = gdal.Open(str(first))
    geotr = raster.GetGeoTransform()

    # Dimensions
    nbx = raster.RasterXSize
    nby = raster.RasterYSize

    xmin = geotr[0]
    xmax = geotr[0]+geotr[1]*float(nbx)

    if geotr[5]>0:
        ymin = geotr[3]
        ymax = geotr[3]+geotr[5]*float(nby)
    else:
        ymin = geotr[3]+geotr[5]*float(nby)
        ymax = geotr[3]

    options = gdal.BuildVRTOptions(resolution='user',
                                   xRes=abs(geotr[1]),
                                   yRes=abs(geotr[5]),
                                   outputBounds=[xmin,ymin,xmax,ymax],
                                   resampleAlg='bilinear',
                                   srcNodata=99999.)

    # retain current working directory
    oldcwd = os.getcwd()
    # change working directory to the parent of the output file
    os.chdir(fout.parent.absolute())

    # work with relative paths
    myvrt = gdal.BuildVRT(str(fout.with_suffix('.vrt').name) , [str(_get_relative_path(file, fout.parent)) for file in files], options=options)
    # close the dataset -- force to write on disk
    myvrt = None
    # restore working directory
    os.chdir(oldcwd)

def translate_vrt2tif(fn:str, fout:str=None):
    """
    Translate vrt file to tif file

    Args:
        fn (str): '.vrt' file to translate
        fout (str, optional): '.tif' file out. Defaults to None --> fn+'.tif'
    """
    if isinstance(fn,Path):
        fn = str(fn)
    if isinstance(fout,Path):
        fout = str(fout)

    if os.path.exists(fn):

        if not fn.endswith('.vrt'):
            logging.warning('Bad file -- not .vrt extension !')
            return

        if fout is None:
            fout = fn +'.tif'

        if not fout.endswith('.tif'):
            fout+='.tif'

        options = gdal.TranslateOptions(format='GTiff', creationOptions=['COMPRESS=LZW', 'TILED=YES', 'BIGTIFF=YES'])
        gdal.Translate(fout, fn, options=options)

    else:
        logging.warning('The file does not exist !')

def crop_vrt(fn:str, crop:list, fout:str=None):
    """
    Crop vrt file

    Args:
        fn (str): '.vrt' file to crop
        crop (list): Bounds [[xmin, xmax], [ymin,ymax]] aka [[xLL, xUR], [yLL,yUR]]
        fout (str, optional): '.tif' file out. Defaults to None --> fn+'_crop.tif'
    """
    if os.path.exists(fn):

        if not fn.endswith('.vrt'):
            logging.warning('Bad file -- not .vrt extension !')
            return

        [xmin, xmax], [ymin, ymax] = crop

        if fout is None:
            fout = fn +'_crop.tif'

        if not fout.endswith('.tif'):
            fout+='.tif'

        gdal.Translate(fout, fn, projWin=[xmin, ymax, xmax, ymin])

    else:
        logging.warning('The file does not exist !')


if __name__=='__main__':

    dir = r'D:\OneDrive\OneDrive - Universite de Liege\Crues\2021-07 Vesdre\CSC - Convention - ARNE\Data\2023\GeoTif\encours\MNT_Bati+Muret'
    file_vrt = r'AllData_MNT_BatiMuret_50cm.vrt'

    create_vrt(dir, fout=file_vrt)
    crop_vrt(os.path.join(dir, file_vrt), [[251000,253400],[135500,141300]], os.path.join(dir, 'Theux-Pepinster.tif'))