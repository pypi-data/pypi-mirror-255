from osgeo import ogr, gdal
import geopandas as gpd
from os.path import exists, join, dirname, basename
from os import getcwd, chdir
from typing import Union, Literal
import numpy as np

class Walous_data():

    def __init__(self,
                 dir_data:str = '',
                 fn:str = 'WAL_UTS__2018_L72',
                 bounds:Union[list[float, float, float, float],list[list[float, float], list[float, float]]] = None) -> None:

        self._dir = dir_data
        self._fn  = fn
        self._gdf = None
        if bounds is not None:
            self.read(True, bounds=bounds)

    def read(self,
             force:bool = False,
             bounds:Union[list[float, float, float, float],list[list[float, float], list[float, float]]] = None):
        """
        Read the file

        :param force : force to read even read was done before
        :param bounds : [xmin, ymin, xmax, ymax] or [[xmin, xmax], [ymin, ymax]]
        """

        if self._gdf is None or force:
            assert self._dir!="" and self._fn != ''

            if exists(join(self._dir, self._fn+'.shp')):
                if bounds is not None:
                    if len(bounds)==2:
                        xmin = bounds[0][0]
                        xmax = bounds[0][1]
                        ymin = bounds[1][0]
                        ymax = bounds[1][1]
                    else:
                        xmin = bounds[0]
                        xmax = bounds[2]
                        ymin = bounds[1]
                        ymax = bounds[3]

                    self._gdf = gpd.read_file(join(self._dir, self._fn+'.shp'), bbox=(xmin,ymin,xmax,ymax))
                else:
                    self._gdf = gpd.read_file(join(self._dir, self._fn+'.shp'))

                # self._gdf['MAJ_NIV2'] = np.asarray(self._gdf['MAJ_NIV2'], dtype=int)
                # self._gdf['MAJ_NIV3'] = np.asarray(self._gdf['MAJ_NIV3'], dtype=int) # ne fonctionne pas car le niveau 3 contient des lettres --> à généraliser
            else:
                self._gdf = None

    def write(self, fnout:str=''):

        if fnout=='':
            fnout = 'out_clip.shp'

        curdir = getcwd()
        detsdir = dirname(fnout)

        chdir(detsdir)

        self._gdf.to_file(basename(fnout))

        chdir(curdir)

    def to_file(self, fn):
        """
        link to write
        """
        self.write(fn)

    def rasterize(self,
                  bounds:Union[list[float, float, float, float],list[list[float, float], list[float, float]]] = None,
                  layer:Literal['MAJ_NIV1','MAJ_NIV2'] ='MAJ_NIV1',
                  mapping = None,
                  fn_out:str = 'out.tif',
                  pixel_size:float = 0.5,
                  NoData_value:float = -9999.,
                  num_type = gdal.GDT_Float32
                  ):

        """
        Rasterization of polygon data to tif
        """
        if bounds is None:
            return None

        if self._gdf is None:
            self.read(bounds=bounds)

        if self._gdf is None:
            return None

        if layer not in self._gdf.keys():
            return None

        self.write(fn_out + '.shp')
        self._gdf['Mapping'] = np.float32(self._gdf[layer])

        source_ds:ogr.DataSource
        source_layer:ogr.Layer

        source_ds = ogr.Open(self._gdf.to_json())

        # source_srs:ogr.
        source_layer = source_ds.GetLayer()
        source_srs = source_layer.GetSpatialRef()

        # Create the destination data source
        x_res = int((bounds[0][1] - bounds[0][0]) / pixel_size)
        y_res = int((bounds[1][1] - bounds[1][0]) / pixel_size)

        driver:gdal.Driver
        driver = gdal.GetDriverByName('GTiff')
        target_ds = driver.Create(fn_out, x_res, y_res, 1, num_type)

        target_ds:gdal.Dataset
        band:gdal.Band
        target_ds.SetGeoTransform((bounds[0][0], pixel_size, 0, bounds[1][1], 0, -pixel_size))
        band = target_ds.GetRasterBand(1)
        band.SetNoDataValue(NoData_value)

        target_ds.SetProjection(source_srs.ExportToWkt())

        # Rasterize
        gdal.RasterizeLayer(target_ds,
                            [1], source_layer,
                            options = ["ALL_TOUCHED=TRUE", "ATTRIBUTE=Mapping"])

        target_ds = None

        return fn_out
