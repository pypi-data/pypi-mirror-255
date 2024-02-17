import wx
from wx.dataview import TreeListCtrl, TreeListItem
from wx import dataview, StaticText, TextCtrl
from os.path import exists,join,splitext,dirname
from os import scandir, chdir, getcwd
import numpy as np
import subprocess
import logging
from enum import Enum
import numpy as np
from collections import namedtuple
from pathlib import Path
from osgeo import gdal
from typing import Union, Literal
import json
import pandas as pd
from datetime import datetime as dt
import matplotlib.pyplot as plt
import types

from ..PyTranslate import _
from ..wolfresults_2D import wolf2dprev,Wolfresults_2D
from ..wolf_array import WolfArray, header_wolf, WOLF_ARRAY_FULL_INTEGER
from .check_scenario import check_file_update, check_file_bc, import_files
from .update_void import create_new_file as update_void
from .imposebc_void import create_new_file as bc_void
from ..wolf_vrt import create_vrt_from_files_first_based, translate_vrt2tif
from ..PyDraw import WolfMapViewer
from ..PyHydrographs import Hydrograph
from .update_void import Update_Sim
from ..Results2DGPU import wolfres2DGPU

# try:
#     from ..wolfgpu.simple_simulation import SimpleSimulation, SimulationDuration, SimulationDurationType
# except:
#     try:
#         from wolfgpu.simple_simulation import SimpleSimulation, SimulationDuration, SimulationDurationType
#     except:
#         logging.error(_('WOLFGPU not installed !'))

try:
    from wolfgpu.simple_simulation import SimpleSimulation, SimulationDuration, SimulationDurationType
except:
    logging.error(_('WOLFGPU not installed !'))


def delete_folder(pth:Path):
    for sub in pth.iterdir():
        if sub.is_dir():
            delete_folder(sub)
        else:
            sub.unlink()
    pth.rmdir() # if you just want to delete the dir content but not the dir itself, remove this line

# extension des fichiers à vérifier
class GPU_2D_file_extensions(Enum):
    TIF  = '.tif'  # raster
    TIFF = '.tiff' # raster
    PY   = '.py'   # python script
    NPY  = '.npy'  # numpy array
    BIN  = '.bin'  # WOLF binary file
    JSON = '.json' # json file
    TXT  = '.txt'  # hydrographs

ALL_EXTENSIONS = [cur.value for cur in GPU_2D_file_extensions]

# Predefined keys
WOLF_UPDATE   = 'Wolf update'
WOLF_BC       = 'Wolf boundary conditions'
OTHER_SCRIPTS = 'Other scripts'
IS_SIMUL      = 'is_simul'
IS_SCENARIO   = 'is_scenario'
HAS_RESULTS   = 'has_results'
MISSING       = 'missing'
SUBDIRS       = 'subdirs'
DISCHARGES    = 'discharges'

# Définition d'un namedtuple pour représenter les fichiers d'une simulation GPU
_gpu_file = namedtuple('gpufile', ['name', 'type', 'extension'])

# Liste des fichiers à vérifier
class GPU_2D_file(Enum):
    PARAMETERS   = _gpu_file('parameters', str       , GPU_2D_file_extensions.JSON.value)
    BATHYMETRY   = _gpu_file('bathymetry', np.float32, GPU_2D_file_extensions.NPY.value)
    WATER_DEPTH  = _gpu_file('h'         , np.float32, GPU_2D_file_extensions.NPY.value)
    DISCHARGE_X  = _gpu_file('qx'        , np.float32, GPU_2D_file_extensions.NPY.value)
    DISCHARGE_Y  = _gpu_file('qy'        , np.float32, GPU_2D_file_extensions.NPY.value)
    MANNING      = _gpu_file('manning'   , np.float32, GPU_2D_file_extensions.NPY.value)
    COMPUTATION_MASK = _gpu_file('nap'   , np.uint8  , GPU_2D_file_extensions.NPY.value)
    INFILTRATION = _gpu_file('infiltration_zones', np.int32, GPU_2D_file_extensions.NPY.value)

# répertoire de sortie des simulations GPU
RESULT_DIR = 'simul_gpu_results'

class Hydrograph_scenario():
    """ Hydrograph for a scenario """
    def __init__(self, fname:Path, sep:str = '\t', decimal='.') -> None:

        self._data = pd.read_csv(fname, sep=sep, decimal=decimal, header=0, index_col=0)
        self._filename = fname
        self._name = str(fname.with_suffix('').name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    def plot(self, figax = None):

        if figax is None:
            fig, ax = plt.subplots()
        else:
            fig,ax = figax

        self._data.plot(ax=ax, drawstyle="steps-post")

        return fig,ax

class Config_Manager_2D_GPU:
    """
    Gestionnaire de configurations 2D - code GPU
    """

    def __init__(self, workingdir:str = '', mapviewer:WolfMapViewer = None) -> None:
        """
        Recherche de toutes les modélisation dans un répertoire et ses sous-répertoires
        """
        self.wx_exists = wx.App.Get() is not None

        self.workingdir = ''
        self.wolfcli    = ''

        if workingdir == '':
            if self.wx_exists:
                dlg = wx.DirDialog(None,_('Choose directory to scan'), style = wx.FD_OPEN)
                ret = dlg.ShowModal()
                if ret != wx.ID_OK:
                    dlg.Destroy()
                    return
                workingdir = dlg.GetPath()
                dlg.Destroy()
            else:
                logging.error(_('No working directory provided !'))
                return

        if not exists(workingdir):
            logging.error(_('Directory does not exist !'))
            return

        self.workingdir = Path(workingdir)
        self.mapviewer  = mapviewer

        self._txtctrl = None
        self._ui  = None

        self.load_data()

    def load_data(self):
        """ Chargement/Rechargement des données """
        self.configs = {}
        self.scan_wdir()
        self.find_files()

        if self._ui is not None:
            # la fenêtre est déjà ouverte
            self._ui.refill_data(self.configs)
        else:
            if self.wx_exists:
                self._ui = UI_Manager_2D_GPU(self.configs, parent=self)


    @property
    def txtctrl(self):
        if self._ui is None:
            return None
        return self._ui._txtctrl

    # Scanning directories
    # --------------------
    def _scan_dir(self, wd:Path, curdict:dict):
        """ Scan récursif d'un répertoire de base et création de sous-dictionnaires """
        for curel in scandir(wd):
            if curel.is_dir():
                newel = curdict[Path(curel)]={}
                self._scan_dir(curel, newel)

    def scan_wdir(self):
        """
        Récupération de tous les répertoires et sous-répertoires
        et placement dans le dictionnaire self.configs
        """
        if self.workingdir.name =='':
            logging.warning(_('Nothing to do !'))
            return

        self._scan_dir(self.workingdir, self.configs)

    # Get properties
    # --------------

    def get_header(self) -> header_wolf:
        """ Get header from .tif file """

        if len(self.configs[GPU_2D_file_extensions.TIF.value])==0:
            return header_wolf()

        curtif = self.configs[GPU_2D_file_extensions.TIF.value][0]

        return self._get_header(curtif)

    def _get_header(self, filearray:Path) -> header_wolf:
        """ Get header from .tif file """

        if not filearray.exists():
            return header_wolf()

        header = header_wolf()

        if filearray.suffix == GPU_2D_file_extensions.TIF.value:

            raster:gdal.Dataset
            raster = gdal.Open(str(filearray))
            geotr = raster.GetGeoTransform()

            # Dimensions
            nbx = raster.RasterXSize
            nby = raster.RasterYSize

            dx = abs(geotr[1])
            dy = abs(geotr[5])
            origx = geotr[0]

            if geotr[5]<0.:
                origy = geotr[3]+geotr[5]*float(nby)
            else:
                origy = geotr[3]

        elif filearray.suffix == GPU_2D_file_extensions.NPY.value:
            with open(filearray, 'rb') as f:
                major, minor = np.lib.format.read_magic(f)
                shape, fortran, dtype = np.lib.format.read_array_header_1_0(f)
                nbx, nby = shape

                dx, dy, origx, origy = (1., 1., 0., 0.)

                # Il y de fortes chances que cette matrice numpy provienne d'une modélisation GPU
                #  et donc que les coordonnées et la résolution soient disponibles dans un fichier parameters.json
                if (filearray.parent / 'parameters.json').exists():
                    with open(filearray.parent / 'parameters.json', 'r') as f:
                        params = json.load(f)

                    if 'parameters' in params.keys():
                        if "dx" in params['parameters'].keys() :
                            dx = float(params['parameters']["dx"])
                        if "dy" in params['parameters'].keys() :
                            dy = float(params['parameters']["dy"])
                        if "base_coord_x" in params['parameters'].keys() :
                            origx = float(params['parameters']["base_coord_x"])
                        if "base_coord_y" in params['parameters'].keys() :
                            origy = float(params['parameters']["base_coord_y"])

        elif filearray.suffix == GPU_2D_file_extensions.BIN.value:

            header.read_txt_header(str(filearray))
            return header

        header.dx = dx
        header.dy = dy
        header.origx = origx
        header.origy = origy
        header.nbx = nbx
        header.nby = nby

        return header

    def get_all_numpy(self) -> list[Path]:
        """ Get all numpy files """

        all_numpy = []

        for key, curdict in self._flat_configs:
            if GPU_2D_file_extensions.NPY.value in curdict.keys():
                if len(curdict[GPU_2D_file_extensions.NPY.value])>0:
                    all_numpy += curdict[GPU_2D_file_extensions.NPY.value]

        return all_numpy

    def get_all_sims(self) -> list[Path]:
        """ Get all simulation files """

        all_sims = []

        for key, curdict in self._flat_configs:
            if IS_SIMUL in curdict.keys():
                if curdict[IS_SIMUL]:
                    all_sims.append(curdict['path'])

        return all_sims

    def _flatten_configs(self) -> list[dict]:
        """ flatten configs """

        def _flatten(curdict:dict, ret:list):
            """ flatten a dict """
            for key, val in curdict.items():
                if isinstance(val, dict):
                    ret.append((key, val))
                    _flatten(val, ret)

        self._flat_configs = []
        _flatten(self.configs, self._flat_configs)


    def check_consistency(self) -> str:
        """
        Check consistency of all files

        All numpy files must have the same shape as the tif file in thr root directory
        All hydrographs must have the same number of columns
        """

        numpyfiles = self.get_all_numpy()

        log = ''
        for curnpy in numpyfiles:
            arr = np.load(curnpy)
            if arr.shape != (self._header.nbx, self._header.nby):
                loclog = _('Bad shape for {} !'.format(curnpy))
                log += loclog + '\n'
                logging.warning(loclog)

        hydro = self.get_hydrographs()
        nb = hydro[0].data.shape[1]
        for curhydro in hydro:
            if curhydro.data.shape[1] != nb:
                loclog = _('Bad number of columns for {} !'.format(curhydro[0]._filename))
                log += loclog + '\n'
                logging.warning(loclog)

        return log

    # Analyze files
    # -------------

    def _find_files_subdirs(self, wd:Path, curdict:dict):
        """ Recherche des fichiers de simulation/scenario dans un répertoire """

        # create list for all extensions
        self._prefill_dict(curdict)
        curdict['path'] = wd

        # scan each file

        for curel in scandir(wd):
            if curel.is_file():
                if not curel.name.startswith('__'):
                    parts=splitext(curel)

                    if len(parts)==2:
                        ext = parts[1]
                        if ext in ALL_EXTENSIONS:
                            locpath = Path(curel.path)
                            if ext == GPU_2D_file_extensions.PY.value:
                                # test if it is a WOLF update file
                                if check_file_update(locpath):
                                    curdict[ext][WOLF_UPDATE].append(locpath)
                                elif check_file_bc(locpath):
                                    curdict[ext][WOLF_BC].append(locpath)
                                else:
                                    curdict[ext][OTHER_SCRIPTS].append(locpath)

                            else:
                                # ajout du fichier dans la liste
                                curdict[ext].append(locpath)

            elif curel.is_dir():
                if curel.name.startswith('__'):
                  pass
                elif curel.name == RESULT_DIR:
                    curdict[HAS_RESULTS] = True
                else:
                    curdict[SUBDIRS].append(Path(curel.name))

        # test if it is a simulation
        self._test_is_simul(curdict)

        # test if it is a scenario
        self._test_is_scenario(curdict)

    def _recursive_find_files(self, wd:Path, curdict:dict):
        """ Recherche récursive des fichiers de simulation/scenario dans les répertoires dont la structure a été traduite en dictionnaire """
        if len(curdict.keys())>0:
            for k in curdict.keys():
                self._recursive_find_files(k, curdict[k])

        if not '__' in wd.name:
            self._find_files_subdirs(wd, curdict)

    def _prefill_dict(self, curdict:dict):
        """ Création des listes pour toutes les extensions """
        for ext in ALL_EXTENSIONS:
            if ext == GPU_2D_file_extensions.PY.value:
                curdict[ext] = {}
                curdict[ext][WOLF_UPDATE] = []
                curdict[ext][WOLF_BC] = []
                curdict[ext][OTHER_SCRIPTS] = []
            else:
                curdict[ext] = []

        curdict[IS_SIMUL]    = False
        curdict[IS_SCENARIO] = False
        curdict[HAS_RESULTS] = False
        curdict[MISSING]     = []
        curdict[SUBDIRS]     = []
        curdict['path']      = None

    def _test_is_simul(self, curdict:dict):
        """ Teste si le répertoire contient des fichiers de simulation """

        ok = True

        # présence du fichier de paramètres
        if GPU_2D_file_extensions.JSON.value in curdict.keys():
            ok &= (GPU_2D_file.PARAMETERS.value.name+GPU_2D_file.PARAMETERS.value.extension).lower() in [cur.name.lower() for cur in curdict[GPU_2D_file_extensions.JSON.value]]
        else:
            curdict['missing'].append(GPU_2D_file_extensions.JSON.value)
            ok = False

        # Présence des fichiers de calcul
        if GPU_2D_file_extensions.NPY.value in curdict.keys():
            for curfile in GPU_2D_file:
                if curfile.value.extension == GPU_2D_file_extensions.NPY.value:
                    ok &= (curfile.value.name + curfile.value.extension).lower() in [cur.name.lower() for cur in curdict[GPU_2D_file_extensions.NPY.value]]
        else:
            curdict['missing'].append(GPU_2D_file_extensions.NPY.value)
            ok = False

        curdict['is_simul'] = ok

    def _test_is_scenario(self, curdict:dict):

        curdict['is_scenario'] = len(curdict[GPU_2D_file_extensions.TIF.value])>0 or \
                                 len(curdict[GPU_2D_file_extensions.TIFF.value])>0 or \
                                 len(curdict[GPU_2D_file_extensions.PY.value])>0

    def find_files(self):
        """
        Recehrche des fichiers de simulation/scenario dans les répertoires dont la structure a été traduite en dictionnaire
        """
        if self.workingdir.name =='':
            logging.warning(_('Nothing to do !'))
            return

        self._recursive_find_files(self.workingdir, self.configs)
        self._flatten_configs()

        # initialisation du header
        self._header = self.get_header()

    # Assembly
    # --------
    def get_tree(self, from_path:Path) -> list[Path]:
        """
        Get tree from a path

        Fnd all directories from the current path to the working directory
        """

        curtree = [from_path]

        while str(from_path) != str(self.workingdir):
            from_path = from_path.parent
            curtree.insert(0, from_path)

        return curtree

    def get_dicts(self, from_tree:list[Path]) -> list[dict]:
        """ Get dicts from a tree """

        curdict = [self.configs]

        for curpath in from_tree[1:]:
            curdict.append(curdict[-1][curpath])

        return curdict

    def _select_tif_partname(self, curdict:dict, tifstr:Literal['bath', 'mann']):
        """ Select tif files with a 'str' in their name """

        tif_list = [curtif for curtif in curdict[GPU_2D_file_extensions.TIF.value] if tifstr in curtif.name]

        return tif_list


    def create_vrt(self, from_path:Path):
        """ Create a vrt file from a path """

        curtree = self.get_tree(from_path)
        curdicts = self.get_dicts(curtree)

        # tous les fichiers tif -> list of lists
        all_tif_bath = [self._select_tif_partname(curdict, 'bath') for curdict in curdicts]
        all_tif_mann = [self._select_tif_partname(curdict, 'mann') for curdict in curdicts]
        all_tif_infil = [self._select_tif_partname(curdict, 'infil') for curdict in curdicts]

        # flatten list os lists
        all_tif_bath = [curel for curlist in all_tif_bath if len(curlist)>0 for curel in curlist]
        all_tif_mann = [curel for curlist in all_tif_mann if len(curlist)>0 for curel in curlist]
        all_tif_infil = [curel for curlist in all_tif_infil if len(curlist)>0 for curel in curlist]

        # création du fichier vrt
        create_vrt_from_files_first_based(all_tif_bath, from_path / '__bath_assembly.vrt')
        create_vrt_from_files_first_based(all_tif_mann, from_path / '__mann_assembly.vrt')
        if len(all_tif_infil)>0:
            create_vrt_from_files_first_based(all_tif_infil, from_path / '__infil_assembly.vrt')

    def translate_vrt2tif(self, from_path:Path):
        """ Translate vrt to tif """
        vrtin = ['__bath_assembly.vrt', '__mann_assembly.vrt', '__infil_assembly.vrt']
        fout  = ['__bathymetry.tif'   , '__manning.tif', '__infiltration.tif']

        for curin, curout in zip(vrtin, fout):
            if (from_path / curin).exists():
                translate_vrt2tif(from_path / curin, from_path / curout)

    def _import_scripts_topo_manning(self, from_path:Path) -> list[types.ModuleType]:
        """ find all scripts from/up a path """

        curtree = self.get_tree(from_path)
        curdicts = self.get_dicts(curtree)

        # tous les fichiers .py -> list of lists
        all_py = [curpy for curdict in curdicts for curpy in curdict[GPU_2D_file_extensions.PY.value][WOLF_UPDATE]]

        # import des modules
        imported_modules = import_files(all_py)

        return imported_modules


    def _apply_scripts_update_topo_maning_inf(self,
                                              modules:list[types.ModuleType],
                                              array_bat:WolfArray,
                                              array_mann:WolfArray,
                                              array_inf:WolfArray):
        """ Apply all scripts from a list of modules """

        for curmod in modules:
            instmod = curmod.Update_Sim_Scenario()
            instmod.update_topobathy(array_bat)
            instmod.update_manning(array_mann)
            instmod.update_infiltration(array_inf)

    def _import_scripts_bc(self, from_path:Path) -> list[types.ModuleType]:
        """ find all scripts from/up a path """

        curtree = self.get_tree(from_path)
        curdicts = self.get_dicts(curtree)

        # tous les fichiers .py -> list of lists
        all_py = [curpy for curdict in curdicts for curpy in curdict[GPU_2D_file_extensions.PY.value][WOLF_BC]]

        # import des modules
        imported_modules = import_files(all_py)

        return imported_modules


    def _apply_scripts_bc(self, modules:list[types.ModuleType], sim:SimpleSimulation):
        """ Apply all scripts from a list of modules """

        for curmod in modules:

            curmod.Impose_BC_Scenario().impose_bc(sim)


    def load_hydrograph(self, path:Path, toplot=True) -> tuple[Hydrograph_scenario, plt.Figure, plt.Axes]:
        """ Load hydrograph from a path """
        hydro = Hydrograph_scenario(path)
        fig,ax = None, None
        if toplot:
            fig,ax = hydro.plot()
            fig.show()

        return hydro, fig, ax

    def get_hydrographs(self) -> list[Hydrograph]:
        """ Get all hydrographs"""

        all_hydro = []

        low_keys = [Path(curkey).name.lower() for curkey in self.configs.keys()]
        if DISCHARGES in low_keys:
            curkey = [curkey for curkey in self.configs.keys()][low_keys.index(DISCHARGES)]
            list_hydro = self.configs[curkey][GPU_2D_file_extensions.TXT.value]

            for curq in list_hydro:
                all_hydro.append(self.load_hydrograph(curq, toplot=False)[0])

        return all_hydro

    def get_names_hydrographs(self) -> list[str]:

        all_hydros = self.get_hydrographs()
        names = [curhydro.name for curhydro in all_hydros]

        return names

    def create_void_infil(self):
        """  create void infiltration_zones file """

        if (self.workingdir / 'bathymetry.tif').exists():
            locheader = self.get_header()
            infilzones = WolfArray(srcheader=locheader, whichtype= WOLF_ARRAY_FULL_INTEGER)
            infilzones.array.data[:,:] = 0
            infilzones.nullvalue = -1
            infilzones.write_all(str(self.workingdir / 'infiltration.tif'))

            if (self.workingdir / 'infiltration.tif').exists():
                logging.info(_('infiltration.tif created and set to -1 ! -- Please edit it !'))
            else:
                logging.error(_("infiltration.tif not created ! --  Does 'bathymetry.tif' or any '.tif' file exist in the root directory ?"))
        else:
            logging.error(_("No 'bathymetry.tif' file found in the root directory !"))

    def create_simulation(self, dir:Path, idx_hydros:list[int] = [-1], delete_existing:bool = False) -> list[Path]:
        """ Create a simulation from different hydrographs """

        if isinstance(dir, str):
            dir = Path(dir)

        # test if dir is in the tree
        dirs_key  = [key for key, curdict in self._flat_configs]
        dirs_dict = [curdict for key, curdict in self._flat_configs]

        if not dir in dirs_key:
            logging.error(_('Directory {} not found ! - Aborting !'.format(dir)))
            return

        # dictionnaire associé au scénario du répertoire
        scen_dict = dirs_dict[dirs_key.index(dir)]

        # search for hydrographs
        hydros = self.get_hydrographs()
        names  = self.get_names_hydrographs()
        if idx_hydros == [-1]:
            idx_hydros = list(range(len(hydros)))

        maxhydro = max(idx_hydros)
        minhydro = min(idx_hydros)

        if maxhydro >= len(hydros):
            logging.error(_('Index {} too high ! - Aborting !'.format(maxhydro)))
            return
        if minhydro < 0:
            logging.error(_('Index {} too low ! - Aborting !'.format(minhydro)))
            return

        # select hydrographs
        used_hydros = [hydros[curidx] for curidx in idx_hydros]
        used_names  = [names[curidx] for curidx in idx_hydros]

        if len(used_hydros)==0:
            logging.error(_('No hydrograph selected ! - Aborting !'))
            return

        # create subdirectories for each hydrograph
        used_dirs = [Path(dir / ('simulations/sim_' + curname)) for curname in used_names]
        for curdir in used_dirs:
            if curdir.exists():
                if delete_existing:
                    logging.info(_('Directory {} already exists ! -- Deleting it !'.format(curdir)))
                    try:
                        delete_folder(curdir)
                    except:
                        logging.error(_('Directory {} not deleted !'.format(curdir)))
                else:
                    logging.info(_('Directory {} already exists ! -- Using it'.format(curdir)))
            else:
                logging.info(_('Creating directory {} !'.format(curdir)))
                curdir.mkdir(parents=True)

        # Assembly of bathymetry, manning and infiltration if exists
        self.create_vrt(dir)
        self.translate_vrt2tif(dir)

        quit = False
        if not (dir / '__bathymetry.tif').exists():
            logging.error(_('No __bathymetry.tif found !'))
            quit = True
        if not (dir / '__manning.tif').exists():
            logging.error(_('No __manning.tif found !'))
            quit = True

        if quit:
            logging.error(_('Bas assembly operation -- Simulation creation aborted !'))
            return

        bat = WolfArray(str(dir / '__bathymetry.tif'))
        man = WolfArray(str(dir / '__manning.tif'))

        # check for infiltration
        if exists(dir / '__infiltration.tif'):
            infiltration = WolfArray(str(dir / '__infiltration.tif'))
            if infiltration.wolftype != WOLF_ARRAY_FULL_INTEGER:
                logging.error(_('Infiltration .tif must be a full integer array ! -- The array will be ignored !'))
                infiltration = WolfArray(srcheader=bat.get_header(), whichtype= WOLF_ARRAY_FULL_INTEGER)
                infiltration.array.data[:,:] = 0
        else:
            infiltration = WolfArray(srcheader=bat.get_header(), whichtype= WOLF_ARRAY_FULL_INTEGER)
            infiltration.array.data[:,:] = 0

        # applying Python scrpitps on ARRAYS
        self._apply_scripts_update_topo_maning_inf(self._import_scripts_topo_manning(dir), bat, man, infiltration)

        # save arrays on disk
        bat.write_all(str(dir / '__bathymetry_after_scripts.tif'))
        man.write_all(str(dir / '__manning_after_scripts.tif'))
        infiltration.write_all(str(dir / '__infiltration_after_scripts.tif'))

        # create simulation
        allsims = []
        for curdir, curhydro in zip(used_dirs, used_hydros):

            # instanciation de la simulation
            cursim = SimpleSimulation(self._header.nbx, self._header.nby)

            # paramétrage spatial
            cursim.param_dx = self._header.dx
            cursim.param_dy = self._header.dy
            cursim.param_base_coord_ll_x = self._header.origx
            cursim.param_base_coord_ll_y = self._header.origy

            # paramétrage hydraulique/numérique
            cursim.param_courant = .4
            cursim.param_runge_kutta = .5

            # associating arrays to simulation
            cursim.bathymetry = bat.array.data
            cursim.manning    = man.array.data
            cursim.nap        = np.zeros((self._header.nbx, self._header.nby), dtype=np.uint8)
            cursim.nap[cursim.bathymetry != 99999.] = 1
            cursim.h          = np.zeros((self._header.nbx, self._header.nby), dtype=np.float32)
            cursim.qx         = np.zeros((self._header.nbx, self._header.nby), dtype=np.float32)
            cursim.qy         = np.zeros((self._header.nbx, self._header.nby), dtype=np.float32)

            cursim.infiltration_zones = np.asarray(infiltration.array.data, dtype=np.int32)

            # add hydrograph
            for idx, curline in curhydro.data.iterrows():
                cursim.add_infiltration(float(idx), [float(cur) for cur in curline.values])
            if curhydro.data.index[-1] == 0:
                cursim.param_duration = SimulationDuration(SimulationDurationType.SECONDS, float(86400))
                cursim.add_infiltration(float(86400), [float(cur) for cur in curline.values])
            elif curhydro.data.index[-1]==999999.:
                cursim.param_duration = SimulationDuration(SimulationDurationType.SECONDS, float(86400))
            else:
                cursim.param_duration = SimulationDuration(SimulationDurationType.SECONDS, float(curhydro.data.index[-1]))

            # check for infiltration zones vs hydrograph
            hydro = cursim.infiltrations_chronology
            nb_zones = len(hydro[0][1])
            if infiltration.array.data.max() != nb_zones:
                logging.error(_('You must have {} Infiltration zones but {} are defined!'.format(nb_zones, infiltration.array.data.max())))
                return

            # default reporting period
            cursim._param_report_period = SimulationDuration.from_seconds(3600)

            # applying Python scrpitps on SIMULATION --> Boundary conditions
            self._apply_scripts_bc(self._import_scripts_bc(dir), cursim)

            # cursim.h[cursim.infiltration_zones > 0] = .5

            # save simulation
            cursim.save(curdir)

            logging.info(cursim.check_errors())
            logging.info(_('Simulation {} created !'.format(curdir)))


            with open(curdir / 'quickrun.py', 'w', encoding='utf-8') as f:
                f.write("from pathlib import Path\n")
                f.write("from wolfgpu.simple_simulation import SimpleSimulation\n")
                f.write("from wolfgpu.SimulationRunner import SimulationRunner\n")
                f.write("from wolfgpu.glsimulation import ResultsStore\n\n")
                f.write("def main():\n")
                f.write("\tsim = SimpleSimulation.load(Path(__file__).parent)\n")
                f.write("\tresult_store:ResultsStore = SimulationRunner.quick_run(sim, Path(__file__).parent)")
                f.write("\n\nif __name__ == '__main__':\n")
                f.write("\tmain()\n")

            allsims.append(curdir / 'quickrun.py')


        logging.info(_('Simulation creation finished !'))
        logging.warning(_('Do not forget to update/set the boundary conditions if not set by scripts !'))

        return allsims

    def create_batch(self, path:Path, allsims:list[Path]) -> str:
        """ Create a batch file """

        if len(allsims) == 0:
            return

        batch = ''
        batch += str(allsims[0].drive) + '\n'
        for cursim in allsims:
            cursim:Path
            batch += 'cd {}\n'.format(str(cursim.parent))
            batch += 'python ' + str(cursim.name) + '\n'

        with open(path, 'w', encoding='utf-8') as f:
            f.write(batch)

        return batch

    def run_batch(self, batch:Path):
        """ run a batch file in a subprocess """
        if not batch.exists():
            logging.error(_('Batch file {} does not exist !'.format(batch)))
            return
        if not batch.is_file():
            logging.error(_('Batch file {} is not a file !'.format(batch)))
            return
        if batch.suffix != '.bat':
            logging.error(_('Batch file {} is not a .bat file !'.format(batch)))
            return

        import subprocess
        # Execute the batch file in a separate process
        subprocess.Popen(str(batch), shell=True)



class UI_Manager_2D_GPU():

    def __init__(self, data:dict, parent:Config_Manager_2D_GPU) -> None:
        self._parent = parent
        self._batch = None
        self.create_UI()
        # Fill tree with data
        self._append_configs2tree(data, self._root)

        self._txtctrl.Clear()
        self._txtctrl.write(str(self._parent._header))

    def refill_data(self, data:dict):
        """ Fill tree with data """

        # la fenêtre est déjà ouverte
        self._treelist.DeleteAllItems()
        self._txtctrl.SetBackgroundColour(wx.WHITE)
        self._txtctrl.SetForegroundColour(wx.BLACK)
        self._txtctrl.Clear()

        # Fill tree with data
        self._append_configs2tree(data, self._root)

    def create_UI(self):
        """
        Création de l'interface graphique

        Partie latérale gauche - arbre des simulations
        Partie latérale droite - boutons d'actions
        Partie inférieure - affichage des informations

        """

        # frame creation
        self._frame = wx.Frame(None, wx.ID_ANY, _('Scenario WOLF2D_GPU'), size=(800,800))

        # sizers creation -- frame's structure
        sizer_updown = wx.BoxSizer(wx.VERTICAL)
        sizer_horizontal = wx.BoxSizer(wx.HORIZONTAL)
        sizer_buttons = wx.BoxSizer(wx.VERTICAL)

        # # Liste des chemins d'accès aux icônes
        # icon_paths = []
        # icon_path = Path(__file__).parent / '..\\icons'
        # for curicon in scandir(icon_path):
        #     if curicon.is_file():
        #         icon_paths.append(Path(curicon))

        # # Création de l'objet wx.ImageList
        # image_list = wx.ImageList()

        # # Chargement des icônes dans l'image list
        # for path in icon_paths:
        #     icon = wx.Icon(str(path), wx.BITMAP_TYPE_PNG)
        #     image_list.Add(icon)

        # tree creation
        self._treelist = TreeListCtrl(self._frame,
                                      style=dataview.TL_CHECKBOX|
                                      wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_HAS_BUTTONS)

        # self._treelist.AssignImageList(image_list)

        # tree actions
        self._treelist.Bind(dataview.EVT_TREELIST_ITEM_CHECKED, self.OnCheckItem)            # check/uncheck
        self._treelist.Bind(dataview.EVT_TREELIST_ITEM_ACTIVATED, self.OnActivateTreeElem)   # double click

        # tree root
        self._root = self._treelist.GetRootItem()
        self._selected_item = None
        self._treelist.AppendColumn(_('2D GPU Models'))

        # multilines text control for information
        self._txtctrl = TextCtrl(self._frame, style=wx.TE_MULTILINE|wx.TE_BESTWRAP|wx.TE_RICH)

        # Action buttons
        # --------------
        self._reload = wx.Button(self._frame,label = _('Reload/Update structure'))
        self._reload.Bind(wx.EVT_BUTTON,self.onupdate_structure)

        self._create_void_infil = wx.Button(self._frame,label = _('Create .tif infiltration zones'))
        self._create_void_infil.Bind(wx.EVT_BUTTON,self.oncreate_void_infil)

        self._create_void_scripts = wx.Button(self._frame,label = _('Create void scripts'))
        self._create_void_scripts.Bind(wx.EVT_BUTTON,self.oncreate_void_scripts)

        self._create_vrt = wx.Button(self._frame,label = _('Assembly .vrt to current level'))
        self._create_vrt.Bind(wx.EVT_BUTTON,self.oncreatevrt)

        self._translate_vrt = wx.Button(self._frame,label = _('Translate .vrt to .tif'))
        self._translate_vrt.Bind(wx.EVT_BUTTON,self.ontranslatevrt2tif)

        self.checkconsistency = wx.Button(self._frame,label = _('Check consistency'))
        self.checkconsistency.Bind(wx.EVT_BUTTON,self.oncheck_consistency)

        self.createsim = wx.Button(self._frame,label = _('Create simulation(s)'))
        self.createsim.Bind(wx.EVT_BUTTON,self.oncreate_simulation)

        self.runbatch = wx.Button(self._frame,label = _('Run batch file !'))
        self.runbatch.Bind(wx.EVT_BUTTON,self.onrun_batch)

        self.listsims = wx.Button(self._frame,label = _('List simulation(s)'))
        self.listsims.Bind(wx.EVT_BUTTON,self.onlist_simulation)

        # Positions
        # ---------

        # buttons -> sizer
        sizer_buttons.Add(self._reload,1,wx.EXPAND)
        sizer_buttons.Add(self._create_void_infil,1,wx.EXPAND)
        sizer_buttons.Add(self._create_void_scripts,1,wx.EXPAND)
        sizer_buttons.Add(self._create_vrt,1,wx.EXPAND)
        sizer_buttons.Add(self._translate_vrt,1,wx.EXPAND)
        sizer_buttons.Add(self.checkconsistency,1,wx.EXPAND)
        sizer_buttons.Add(self.listsims,1,wx.EXPAND)
        sizer_buttons.Add(self.createsim,1,wx.EXPAND)
        sizer_buttons.Add(self.runbatch,1,wx.EXPAND)

        # tree, buttons -> horizontal sizer
        sizer_horizontal.Add(self._treelist,1,wx.EXPAND)
        sizer_horizontal.Add(sizer_buttons,1,wx.EXPAND)

        # txt_ctrl, (tree, buttons) -> updown sizer
        sizer_updown.Add(sizer_horizontal,1,wx.EXPAND)
        sizer_updown.Add(self._txtctrl,1,wx.EXPAND)

        # link sizer to frame
        self._frame.SetSizer(sizer_updown)

        # Layout
        self._frame.Layout()

        # Set the position to the center of the screen
        self._frame.Centre(wx.BOTH)

        # Show
        self._frame.Show()

    def onupdate_structure(self,e:wx.MouseEvent):
        """ Mise à jour de la structure """

        self._parent.load_data()

    def oncreate_void_infil(self, e:wx.MouseEvent):
        """ Création d'un fichier d'infiltration vide """
        self._parent.create_void_infil()
        self._parent.load_data()

    def oncreate_void_scripts(self,e:wx.MouseEvent):
        """ Création d'un script vide """

        def_dir = str(self._parent.workingdir)
        if isinstance(self._selected_item, Path):
            def_dir = str(self._selected_item.parent)

        dlg = wx.DirDialog(None, _('Choose a scenario directory'), style = wx.DD_DIR_MUST_EXIST, defaultPath=def_dir) #, wildcard = 'Python script (*.py)|*.py')
        ret = dlg.ShowModal()
        if ret != wx.ID_OK:
            dlg.Destroy()
            return

        wdir = dlg.GetPath()
        dlg.Destroy()

        file_update = Path(wdir) / 'update_top_mann_scen.py'

        if file_update.exists():
            dlg = wx.MessageDialog(None, _('File {} already exists ! \n Overwrite ?'.format(file_update)), _('Warning'), wx.YES_NO)
            ret = dlg.ShowModal()

            if ret != wx.ID_YES:
                dlg.Destroy()
                dlg = wx.FileDialog(None, _('Choose a new file name'), style = wx.FD_SAVE, defaultDir=wdir, defaultFile='_'+str(file_update.name), wildcard = 'Python script (*.py)|*.py')
                ret = dlg.ShowModal()
                if ret != wx.ID_OK:
                    dlg.Destroy()
                    return
                file_update = Path(dlg.GetPath())
                dlg.Destroy()

        update_void(file_update)

        file_bc = Path(wdir) / 'impose_bc_scen.py'
        if file_bc.exists():
            dlg = wx.MessageDialog(None, _('File {} already exists ! \n Overwrite ?'.format(file_bc)), _('Warning'), wx.YES_NO)
            ret = dlg.ShowModal()

            if ret != wx.ID_YES:
                dlg.Destroy()
                dlg = wx.FileDialog(None, _('Choose a new file name'), style = wx.FD_SAVE, defaultDir=wdir, defaultFile='_'+str(file_bc.name), wildcard = 'Python script (*.py)|*.py')
                ret = dlg.ShowModal()
                if ret != wx.ID_OK:
                    dlg.Destroy()
                    return
                file_update = Path(dlg.GetPath())
                dlg.Destroy()

        bc_void(file_bc)

        self._parent.load_data()

    def oncreatevrt(self,e:wx.MouseEvent):
        """ Création d'un fichier vrt """
        mydata = self._treelist.GetItemData(self._selected_item)

        # création du fichier vrt
        self._parent.create_vrt(mydata['path'])

    def ontranslatevrt2tif(self,e:wx.MouseEvent):
        """ Traduction d'un fichier vrt en tif """
        mydata = self._treelist.GetItemData(self._selected_item)

        # création du fichier vrt
        self._parent.translate_vrt2tif(mydata['path'])

    def oncheck_consistency(self,e:wx.MouseEvent):
        """ Vérification de la cohérence des fichiers """
        self._txtctrl.Clear()

        log = self._parent.check_consistency()
        if log =='':
            self._txtctrl.WriteText(_("All is fine !"))
        else:
            self._txtctrl.WriteText(log)

    def choice_hydrograph(self) -> list[int]:

        names = self._parent.get_names_hydrographs()
        dlg = wx.MultiChoiceDialog(None, _('Choose hydrograph'), _('Hydrographs'), names)
        ret = dlg.ShowModal()
        if ret != wx.ID_OK:
            dlg.Destroy()
            return None

        idx = dlg.GetSelections()
        dlg.Destroy()

        return idx

    def oncreate_simulation(self,e:wx.MouseEvent):
        """ Creation d'une simulation """

        hydro = self.choice_hydrograph()
        if hydro is None:
            return

        if len(hydro)==0:
            return

        # Recherche du répertoire de base à ouvrir
        #  utilisatation du répertoire sélectionné ou du répertoire parent/source
        #  si aucun élément sélectionné ou si l'élément sélectionné n'est pas un dictionnaire
        if self._selected_item is None or self._selected_item == self._treelist.GetRootItem():
            logging.info(_('No item selected ! -- using root item'))
            mydata = self._parent.configs
        else:
            mydata = self._treelist.GetItemData(self._selected_item)

            if isinstance(mydata, dict):
                pass
            else:
                logging.info(_('The current activated item is not a dictionnary ! -- using root item'))
                mydata = self._parent.configs

        dlg = wx.DirDialog(None, _('Choose a scenario directory'), style = wx.DD_DIR_MUST_EXIST, defaultPath=str(mydata['path']))
        ret = dlg.ShowModal()
        if ret != wx.ID_OK:
            dlg.Destroy()
            return
        path = dlg.GetPath()
        dlg.Destroy()

        dlg = wx.MessageDialog(None, _('Do you want to delete existing simulations ?'), _('Warning'), wx.YES_NO)
        ret = dlg.ShowModal()
        destroy_if_exists = ret == wx.ID_YES
        dlg.Destroy()

        allsims = self._parent.create_simulation(Path(path), hydro, destroy_if_exists)

        self._parent.load_data()

        if allsims is None:
            logging.error(_('No simulation created !'))
            return

        if len(allsims)>0:

            self._txtctrl.write(_('You have created {} simulations\n\n'.format(len(allsims))))
            for cursim in allsims:
                self._txtctrl.write(str(cursim) + '\n')

            dlg = wx.MessageDialog(None, _('Do you want to create a batch file ?'), _('Warning'), wx.YES_NO)
            ret = dlg.ShowModal()
            create_batch = ret == wx.ID_YES
            dlg.Destroy()

            if create_batch:
                dlg = wx.FileDialog(None, _('Choose a batch file name'), style = wx.FD_SAVE, defaultDir=str(path), defaultFile='quickruns.bat', wildcard = 'Batch file (*.bat)|*.bat')
                ret = dlg.ShowModal()
                if ret != wx.ID_OK:
                    dlg.Destroy()
                    return
                batch = Path(dlg.GetPath())
                dlg.Destroy()

                self._batch = batch
                batch = self._parent.create_batch(Path(batch), allsims)

                self._txtctrl.write('\n\n')
                self._txtctrl.write(_('You can run the simulations with the following commands / batch file :\n\n'))

                self._txtctrl.write(batch)

    def onrun_batch(self,e:wx.MouseEvent):
        """ run batch file """
        if self._batch is None:
            return

        self._parent.run_batch(self._batch)

    def onlist_simulation(self,e:wx.MouseEvent):
        """ List all simulations """

        all_sims = self._parent.get_all_sims()

        self._txtctrl.Clear()
        self._txtctrl.write(_('You have {} simulations\n\n'.format(len(all_sims))))
        self._txtctrl.write(_('List of simulations\n\n'))
        for cursim in all_sims:
            self._txtctrl.write(str(cursim) + '\n')


    def get_sims_only(self, force=False):

        """ Get pathes to all or selected simulations """

        sims=[]

        curitem:TreeListItem
        curitem = self._treelist.GetFirstItem()

        while curitem.IsOk():

            mydata  = self._treelist.GetItemData(curitem)
            checked = self._treelist.GetCheckedState(curitem) == wx.CHK_CHECKED

            if isinstance(mydata, dict):
                if mydata[IS_SIMUL]:
                    if checked or force:
                        sims += [mydata]

            curitem = self._treelist.GetNextItem(curitem)
            # curitem = self._treelist.GetItemParent(curitem)

        return sims

    def OnCheckItem(self,e):
        """ All levels under the item are checked/unchecked"""

        myitem = e.GetItem()

        ctrl = wx.GetKeyState(wx.WXK_CONTROL)

        myparent:TreeListItem
        myparent = self._treelist.GetItemParent(myitem)
        mydata = self._treelist.GetItemData(myitem)
        check = self._treelist.GetCheckedState(myitem)

        # self._resursive_checkitem(myitem, check)
        self._treelist.CheckItemRecursively(myitem, check)

    # def _resursive_checkitem(self, myitem, check):
    #     """ Recursive check/uncheck of all items under the current item"""

    #     child:TreeListItem
    #     child = self._treelist.GetFirstChild(myitem)

    #     while child.IsOk():
    #         subchild:TreeListItem
    #         subchild = self._treelist.GetFirstChild(child)
    #         if subchild.IsOk():
    #             self._resursive_checkitem(child,check)

    #         self._treelist.CheckItem(child,check)
    #         child = self._treelist.GetNextSibling(child)

    def OnActivateTreeElem(self, e):
        """
        If you double click on a tree element
        """

        myitem:TreeListItem
        myitem = e.GetItem()

        self._selected_item = myitem

        # State of the CTRL key
        # - True if pressed
        #  - False if not pressed
        ctrl = wx.GetKeyState(wx.WXK_CONTROL)

        # Upstream tree element
        myparent = self._treelist.GetItemParent(myitem)

        # State of the item - Checked or not
        check = self._treelist.GetCheckedState(myitem)

        # Data associated with the item
        mydata = self._treelist.GetItemData(myitem)

        self._txtctrl.Clear()
        self._txtctrl.SetBackgroundColour(wx.WHITE)
        self._txtctrl.SetForegroundColour(wx.BLACK)

        if isinstance(mydata, dict):
            self._txtctrl.write(_('Yous have selected : {}'.format(str(mydata['path']))))

            if mydata[IS_SIMUL]:
                self._txtctrl.write(_('GPU SIMULATION'))

                if ctrl:
                    # CTRL pressed
                    # - Open the simulation in the viewer
                    addedsim = wolfres2DGPU(str(mydata['path'] / 'simul_gpu_results'), eps=1e-5, idx=str(mydata['path'].name), mapviewer=self._parent.mapviewer)
                    self._parent.mapviewer.add_object('res2d_gpu', newobj=addedsim, id=str(mydata['path'].name))
                else:
                    self._txtctrl.write(_('\n\n CTRL+ double click to open the simulation in the UI'))

        elif isinstance(mydata, list):

            def allfiles(curlist):
                """ Get all files from a list of files """
                allfiles = '\n'
                for curfile in curlist:
                    allfiles+= curfile.name +'\n'
                return allfiles

            self._txtctrl.write(_('Yous have selected a list : {}'.format(allfiles(mydata))))

        elif isinstance(mydata, Path):
            self._txtctrl.write(_('Yous have selected : {} \n\n'.format(str(mydata))))

            if mydata.name.endswith(GPU_2D_file_extensions.PY.value):
                # script Python
                self._txtctrl.write(_('\n\n CTRL+ double click to open the script in the viewer (not an editor !)'))

                # Name of the item and its parent
                nameparent = self._treelist.GetItemText(myparent).lower()
                nameitem   = self._treelist.GetItemText(myitem).lower()

                if nameparent ==  WOLF_UPDATE.lower() or nameparent == OTHER_SCRIPTS.lower() or nameparent == WOLF_BC.lower() :
                    # script

                    if ctrl :
                        # CTRL pressed
                        # - Open the script in the editor
                        self._open_script(mydata, nameparent in [WOLF_UPDATE.lower(), WOLF_BC.lower()])

            elif mydata.name.endswith(GPU_2D_file_extensions.JSON.value):
                # fichier de paramètres
                if ctrl :
                    # script
                    with open(mydata, 'r', encoding='utf-8') as file:
                        txt = json.load(file)
                        self._txtctrl.write(str(txt))
                else:
                    self._txtctrl.write(_('\n\n CTRL+ double click to open the json file in the viewer (not an editor !)'))

            elif mydata.name.endswith(GPU_2D_file_extensions.TIF.value) or mydata.name.endswith(GPU_2D_file_extensions.NPY.value) or mydata.name.endswith(GPU_2D_file_extensions.BIN.value):
                # proposition de chargement dans l'UI  (pas de message si CTRL+double click)

                self._txtctrl.write(str(self._parent._get_header(mydata)))

                if self._parent.mapviewer is not None:
                    if not ctrl:
                        dlg = wx.MessageDialog(None, _('Do you want to load the file in the mapviewer ?'), _('Load file'), wx.YES_NO)
                        ret = dlg.ShowModal()
                        dlg.Destroy()
                        if ret != wx.ID_YES:
                            return

                    myarray = WolfArray(str(mydata), srcheader=self._parent._header, nullvalue=99999., idx=str(mydata.name))

                    self._parent.mapviewer.add_object('array', newobj=myarray, id=str(mydata.name))

            elif mydata.name.endswith(GPU_2D_file_extensions.TXT.value):
                # Chragement d'un hydrogramme
                try:
                    hydro, fig, ax = self._parent.load_hydrograph(mydata, ctrl)
                    if hydro._data.empty:
                        with open(mydata, 'r', encoding='utf-8') as file:
                            txt = file.read()
                            self._txtctrl.write(txt)
                    else:
                        self._txtctrl.write(_('There are {} columns\n\n'.format(len(hydro._data.columns))))
                        for idx, curcol in enumerate(hydro._data.columns):
                            self._txtctrl.write('    - {} has index \t{} \tin the infiltration array'.format(curcol, idx+1) + '\n')
                        self._txtctrl.write('\n\n')

                        self._txtctrl.write(_('Time'))
                        for curcol in hydro._data.columns:
                            self._txtctrl.write('\t'+curcol)
                        self._txtctrl.write('\n')

                        for idx, curline in hydro._data.iterrows():
                            self._txtctrl.write(str(idx))
                            for curval in curline.values:
                                self._txtctrl.write('\t' + str(curval))
                            self._txtctrl.write('\n')

                except:
                    with open(mydata, 'r', encoding='utf-8') as file:
                        txt = file.read()
                        self._txtctrl.write(txt)


    def clear_text(self):
        """ Reset txt control"""

        self._txtctrl.Clear()
        self._txtctrl.SetBackgroundColour(wx.WHITE)
        self._txtctrl.SetForegroundColour(wx.BLACK)

    def _open_script(self, mydata:Path, wolf:bool=False):
        """ Open the script in the editor """
        if mydata.exists():
            with open(mydata, 'r', encoding='utf-8') as file:
                txt = file.read()
                self.clear_text()

                if wolf:
                    self._txtctrl.SetBackgroundColour(wx.Colour(28,142,62))
                    self._txtctrl.SetForegroundColour(wx.WHITE)

                    self._txtctrl.WriteText('WOLF update or BC file\n------------------\n\n')
                    # self._txtctrl.SetForegroundColour(wx.BLACK)
                else:
                    self._txtctrl.SetBackgroundColour(wx.RED)
                    self._txtctrl.SetForegroundColour(wx.WHITE)
                    self._txtctrl.WriteText(' **NOT** WOLF update or BC file\n-----------------------------\n\n')
                    # self._txtctrl.SetForegroundColour(wx.BLACK)

                self._txtctrl.WriteText(txt)

                self._frame.Layout()

    def _append_configs2tree(self, curdict:dict, root:TreeListItem):
        """ Ajout des éléments du dictionnaire dans l'arbre sur base de la racine fournie """

        for idx, (k,v) in enumerate(curdict.items()):

            if isinstance(v, dict):

                if isinstance(k,Path):
                    # on ne garde que le nom du chemin complet
                    kstr = k.name
                else:
                    kstr = str(k)

                if kstr != SUBDIRS and '__' not in kstr:

                    create = True
                    if kstr == GPU_2D_file_extensions.PY.value:
                        # Pas d'ajout de noeud à l'arbre si pas de fichiers .py
                        create = len(v[WOLF_UPDATE])>0 or len(v[OTHER_SCRIPTS])>0 or len(v[WOLF_BC])>0

                    if create:
                        newroot = self._treelist.AppendItem(root, kstr, data = v)
                        self._append_configs2tree(v, newroot)

            elif isinstance(v, list):

                if isinstance(k,Path):
                    # on ne garde que le nom du chemin complet
                    k=k.name
                else:
                    kstr = str(k)

                if len(v)>0:
                    if (kstr in ALL_EXTENSIONS or kstr == WOLF_UPDATE or kstr == OTHER_SCRIPTS or kstr == WOLF_BC) and (kstr != SUBDIRS):
                        newroot = self._treelist.AppendItem(root, k, data = v)

                        for curfile in v:
                            self._treelist.AppendItem(newroot, curfile.name, data = curfile)
