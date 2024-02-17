from os import scandir, getcwd, makedirs
import os.path
from pathlib import Path
import numpy.ma as ma
import wx
from wx.lib.busy import BusyInfo

from .apps.splashscreen import WolfLauncher
from .wolf_array import WOLF_ARRAY_FULL_LOGICAL, WOLF_ARRAY_MB_SINGLE, WolfArray,getkeyblock, WolfArray_Sim2D
from .PyTranslate import _
from .PyDraw import WolfMapViewer,imagetexture
from .PyParams import Wolf_Param
from .PyVertexvectors import Grid
from .RatingCurve import SPWMIGaugingStations,SPWDCENNGaugingStations
from .PyGuiHydrology import GuiHydrology
from .Results2DGPU import wolfres2DGPU
from .hydrology.Catchment import Catchment
from .hydrology.forcedexchanges import forced_exchanges
from .mesh2d.wolf2dprev import *

try:
    from .hydrometry_hece.kiwis_hece import hydrometry_hece as hydrometry
except:
    logging.warning(_('Hydrometry HECE module not found - Load hydrometry instead of hydrometry_hece'))
    from .hydrometry.kiwis import hydrometry

from .PyConfig import WolfConfiguration, ConfigurationKeys
from .pylogging import create_wxlogwindow

# FIXME : Is it necessary to override wx.Frame ? WolfMapManager is a wx.Frame.
#         Is it sufficient to run a wx.App ?
class GenMapManager(wx.Frame):
    mapviewer:WolfMapViewer
    wx_exists:bool

    def __init__(self, *args, **kw):
        # `args` and `kwargs` represent parameters
        # that have to be passed to `wx.Frame.__init__`

        self.mapviewer = None
        self.wx_exists = wx.App.Get() is not None # test if wx App is running
        self.mylogs=None

        if self.wx_exists:

            if len(args) == 0:
                # FIXME This is hackish. the parent parameter should be passed explicitely.
                # I do it this way to not have to recheck the whole project

                # We're missing the parent parameter of wx.Frame.__init__
                # So we put a default.
                # (it appears that wx.Frame.__init__ will accept a call
                # without parent silently, leadings to issue in child
                # frames).
                # See https://gitlab.uliege.be/HECE/HECEPythaaon/-/issues/36
                args = (None,)

            self._configuration = WolfConfiguration()
            SPLASH_PARAM="splash"
            if kw.get(SPLASH_PARAM,True):
                # Make it a instance's variable so that
                # the garbage collector don't remove it
                # before us (WolfLauncher has no parent
                # so it dangles).
                self._MySplash = WolfLauncher(
                    play_sound=self._configuration[ConfigurationKeys.PLAY_WELCOME_SOUND])
                # Don't pollute the call to wf.Frame.__init__
                kw.pop(SPLASH_PARAM, None)

            super().__init__(*args)
            self.mylogs = create_wxlogwindow(_('Informations'))


    def setup_mapviewer(self, title, wolfparent):
        """
        Setup of a WolfMapViewer
        """
        self.mapviewer = WolfMapViewer(None,
                                       title=title,
                                       wolfparent= wolfparent,
                                       wxlogging=self.mylogs)
        self.mapviewer.add_grid()
        self.mapviewer.add_WMS()

    def get_mapviewer(self):
        # Retourne une instance WolfMapViewer
        return self.mapviewer

    def get_configuration(self):
        return self._configuration

    # def add_grid(self, tomapviewer:WolfMapViewer=None):
    #     """ Add a grid to the mapviewer """
    #     mygrid=Grid(1000.)

    #     if tomapviewer is None:
    #         tomapviewer = self.mapviewer
    #     tomapviewer.add_object('vector',newobj=mygrid,ToCheck=False,id='Grid')

    # def add_WMS(self, tomapviewer:WolfMapViewer=None):
    #     """ Add WMS layers to the mapviewer """
    #     if tomapviewer is None:
    #         tomapviewer = self.mapviewer

    #     xmin=0
    #     xmax=0
    #     ymin=0
    #     ymax=0
    #     orthos={'IMAGERIE':{'1971':'ORTHO_1971','1994-2000':'ORTHO_1994_2000',
    #                     '2006-2007':'ORTHO_2006_2007',
    #                     '2009-2010':'ORTHO_2009_2010',
    #                     '2012-2013':'ORTHO_2012_2013',
    #                     '2015':'ORTHO_2015','2016':'ORTHO_2016','2017':'ORTHO_2017',
    #                     '2018':'ORTHO_2018','2019':'ORTHO_2019','2020':'ORTHO_2020',
    #                     '2021':'ORTHO_2021'}}
    #     for idx,(k,item) in enumerate(orthos.items()):
    #         for kdx,(m,subitem) in enumerate(item.items()):
    #             tomapviewer.add_object(which='wmsback',
    #                                         newobj=imagetexture('PPNC',m,k,subitem,
    #                                                             tomapviewer,xmin,xmax,ymin,ymax,-99999,1024),
    #                                         ToCheck=False,id='PPNC '+m)

    #     tomapviewer.add_object(which='wmsback',
    #                               newobj=imagetexture('PPNC','Orthos France','OI.OrthoimageCoverage.HR','',
    #                                                   tomapviewer,xmin,xmax,ymin,ymax,-99999,1024,France=True,epsg='EPSG:27563'),
    #                                       ToCheck=False,id='Orthos France')

    #     forelist={'EAU':{'Aqualim':'RES_LIMNI_DGARNE','Alea':'ALEA_INOND','Lidaxes':'LIDAXES','Juillet 2021':'ZONES_INONDEES','Juillet 2021 IDW':'ZONES_INONDEES$IDW'},
    #                 'LIMITES':{'Secteurs Statistiques':'LIMITES_QS_STATBEL'},
    #                 'INSPIRE':{'Limites administratives':'AU_wms'},
    #                 'PLAN_REGLEMENT':{'Plan Percellaire':'CADMAP_2021_PARCELLES'}}

    #     for idx,(k,item) in enumerate(forelist.items()):
    #         for kdx,(m,subitem) in enumerate(item.items()):
    #             tomapviewer.add_object(which='wmsfore',
    #                         newobj=imagetexture('PPNC',m,k,subitem,
    #                         tomapviewer,xmin,xmax,ymin,ymax,-99999,1024),
    #                         ToCheck=False,id=m)

class MapManager(GenMapManager):
    def __init__(self,*args, **kw):
        super().__init__(*args, **kw)

        self.setup_mapviewer(title = 'Wolf - main data manager', wolfparent=self)

        dir_hydro = path.join(getcwd(),'data\\hydrometry')
        if not exists(dir_hydro):
            makedirs(dir_hydro, exist_ok=True)

        self.SPWhydrometry=hydrometry(dir=dir_hydro)

        self.mapviewer.add_object(which='other',
                                  newobj=self.SPWhydrometry,
                                  ToCheck=False,
                                  id='SPW hydrometry')

class GPU2DModel(GenMapManager):

    mydir:str
    files_results_array:dict
    mybed:WolfArray

    def __init__(self,dir:str='', *args, **kw):
        super(GPU2DModel, self).__init__(*args, **kw)

        self.setup_mapviewer(title='Wolf GPU 2D')

        if dir=='':
            idir=wx.DirDialog(None,"Choose Directory")
            if idir.ShowModal() == wx.ID_CANCEL:
                return
            self.mydir =idir.GetPath()
        else:
            self.mydir=path.normpath(dir)

        ext=['.top','.frott','.cls_pos','.cls_Z','.hbin','.zbin','.srcq']
        for myext in ext:
            if path.exists(self.mydir+'//simul'+myext):

                self.mapviewer.add_object(which='array',
                                          filename=self.mydir+'//simul'+myext,
                                          id=myext,
                                          ToCheck=False)

        self.mybed=WolfArray(self.mydir +'//simul.top')
        self.result = wolfres2DGPU(self.mydir,self.mybed,parent=self)

        self.mapviewer.add_object(which='array',
                                  newobj=self.result,
                                  id='res1',
                                  ToCheck=False)

        """self.files_results_array={}
        self.files_results_array['H']=[]
        idx=101
        while path.exists(self.mydir+'//out'+str(idx)+'r.bin'):
            self.files_results_array['H'].append(['out'+str(idx)+'r.bin','step '+str(idx)])
            idx+=1

        for curfile in self.files_results_array['H']:
            curext=curfile[0]
            curidx=curfile[1]
            self.allviews.add_object(which='array',filename=self.mydir+'//'+curext,id=curidx,ToCheck=False)
        """

        self.mapviewer.findminmax(True)
        self.mapviewer.Autoscale(False)

class HydrologyModel(GenMapManager):

    mydir:str
    mydircharact:str
    mydirwhole:str
    files_hydrology_array:dict
    files_hydrology_vectors:dict
    mainparams:Wolf_Param
    basinparams:Wolf_Param
    SPWstations:SPWMIGaugingStations
    DCENNstations:SPWDCENNGaugingStations
    mycatchment:Catchment
    myexchanges:forced_exchanges

    def __init__(self,dir:str='', splash=True, *args, **kw):

        self.wx_exists = wx.App.Get() is not None # test if wx App is running

        if self.wx_exists:
            super(HydrologyModel, self).__init__(splash=splash, *args, **kw)
        else:
            if "splash" in kw and kw["splash"]:
                raise Exception("You can't have the splash screen outside a GUI")


        self.SPWstations=SPWMIGaugingStations()
        self.DCENNstations=SPWDCENNGaugingStations()

        if dir=='':
            idir=wx.DirDialog(None,"Choose Directory")
            if idir.ShowModal() == wx.ID_CANCEL:
                return
            self.mydir =idir.GetPath()
        else:
            self.mydir=path.normpath(dir)

        self.mydircharact=path.join(self.mydir,'Characteristic_maps\\Drainage_basin')
        self.mydirwhole=path.join(self.mydir,'Whole_basin\\')

        self.mycatchment = Catchment('Mysim',self.mydir,False,True)
        self.myexchanges = forced_exchanges(self.mydir)

        self.mapviewer=GuiHydrology(title='Model : '+self.mydir)

        self.files_hydrology_array={'Characteristic_maps':[
            ('.b','Raw elevation [m]'),
            ('corr.b','Corrected elevation [m]'),
            #('diff.b','Corrections (corr-raw) [m]'),
            ('.nap','Mask [-]'),
            ('.sub','SubBasin index [-]'),
            ('.cnv','Accumulation [km²]'),
            ('.time','Total time [s]'),
            ('.coeff','RunOff coeff [-]'),
            ('.slope','Slope [-]'),
            ('.reachs','Reach index [-]'),
            ('.strahler','Strahler index [-]'),
            ('.reachlevel','Reach accumulation [-]'),
            ('.landuse1','Woodlands [m²]'),
            ('.landuse2','Pastures [m²]'),
            ('.landuse3','Cultivated [m²]'),
            ('.landuse4','Pavements [m²]'),
            ('.landuse5','Water [m²]'),
            ('.landuse6','River [m²]'),
            ('.landuse_limited_area','LandUse Verif'),
            ('.principal_landuse_cropped','Principal landuse [-]'),
            ('_encode.sub','Coded index SubB [-]')]}


        self.files_hydrology_vectors={'Characteristic_maps':[('.delimit.vec','Watershed')],
                                    'Whole_basin':[('Rain_basin_geom.vec','Rain geom'),
                                                    ('Evap_basin_geom.vec','Evapotranspiration geom')]}

        for curfile in self.files_hydrology_array['Characteristic_maps']:
            curext=curfile[0]
            curidx=curfile[1]
            self.mapviewer.add_object(which='array',filename=self.mydircharact+curext,id=curidx,ToCheck=False)

        for curfile in self.files_hydrology_vectors['Characteristic_maps']:
            curext=curfile[0]
            curidx=curfile[1]
            self.mapviewer.add_object(which='vector',filename=self.mydircharact+curext,id=curidx,ToCheck=False)

        for curfile in self.files_hydrology_vectors['Whole_basin']:
            curext=curfile[0]
            curidx=curfile[1]
            if path.exists(self.mydirwhole+curext):
                self.mapviewer.add_object(which='vector',filename=self.mydirwhole+curext,id=curidx,ToCheck=False)

        self.mapviewer.add_object(which='vector',newobj=self.myexchanges.mysegs,id='Forced exchanges',ToCheck=False)
        self.mapviewer.add_object(which='cloud',newobj=self.mycatchment.subBasinCloud,id='Local outlets',ToCheck=False)
        self.mapviewer.add_object(which='cloud',newobj=self.myexchanges.mycloudup,id='Up nodes',ToCheck=False)
        self.mapviewer.add_object(which='cloud',newobj=self.myexchanges.myclouddown,id='Down nodes',ToCheck=False)

        self.mapviewer.add_object(which='other',newobj=self.SPWstations,ToCheck=False,id='SPW-MI stations')
        self.mapviewer.add_object(which='other',newobj=self.DCENNstations,ToCheck=False,id='SPW-DCENN stations')

        self.mapviewer.add_grid()
        self.mapviewer.add_WMS()

        self.mapviewer.findminmax(True)
        self.mapviewer.Autoscale(False)

        #Fichiers de paramètres
        self.mainparams=Wolf_Param(self.mapviewer,filename=self.mydir+'\\Main_model.param',title="Model parameters",DestroyAtClosing=False)
        self.basinparams=Wolf_Param(self.mapviewer,filename=self.mydircharact+'.param',title="Basin parameters",DestroyAtClosing=False)
        self.mainparams.Hide()
        self.basinparams.Hide()

class Wolf2DModel(GenMapManager):

    mydir:str
    # A path to the beacon file (not just the filename)
    filenamegen:str
    files_others:dict
    files_fine_array:dict
    files_MB_array:dict
    files_vectors:dict
    mainparams:Wolf_Param

    # When updating these, pay attention to the fact they are heavliy intertwined.
    # - Boundary conditions coordinates must coincide with cell borders

    myparam: prev_parameters_simul # Parameters of the simulation
    mynap: np.ndarray # Active cells in the simulation (-1 == active; 0 == inactive)
    napbin: WolfArray_Sim2D
    mysuxy: prev_suxsuy # Coordinates of cells border acting as limits of simulation
    xyfile: xy_file
    myinfil: prev_infiltration # Infiltration

    top: WolfArray_Sim2D # Sim2D will wire their masks onto self.napbin.array.mask
    frot: WolfArray_Sim2D
    hbin: WolfArray_Sim2D
    qxbin: WolfArray_Sim2D
    qybin: WolfArray_Sim2D
    zbin: WolfArray_Sim2D
    topinifine: WolfArray_Sim2D

    hbinb: WolfArrayMB # Initial condition: water height (multibloc)
    qxbinb: WolfArrayMB # Initial condition: discharge horizontal (multibloc)
    qybinb: WolfArrayMB # Initial condition: discharge vertical (multibloc)
    topini: WolfArrayMB # Bathymetry (multibloc)

    # A WolfArrayMB with several Zones that makes its contour
    # The MNAP is the multiblock NAP.  It's a big array covering the
    # all the arrays of each block. It is used as a NAP but also as an
    # index from one block's border to another block's border (so it's
    # not filled with zero and ones only but also with block-indices)
    # The MNAP array is a *result* array.
    mymnap: WolfArrayMNAP
    myblocfile: bloc_file

    xyzones: Zones # A link to self.xyfile.myzones FIXME replace that with a property
    curmask: np.ndarray # A link to self.napbin.array.mask
    fines_array: list[WolfArray_Sim2D] # list containing: napbin, top, frot, inf, hbin, qxbin, qybin

    SPWstations:SPWMIGaugingStations
    DCENNstations:SPWDCENNGaugingStations

    def _from_params(self, base_file, myparam: prev_parameters_simul):
        """ This is a __init__ helper. This will be used in the constructor
        to create a mono-block model from scratch (i.e. not reading from disk;
        providing base matrices).

        @base_file Directroy where the model should reside.
        @myparam The parameters to build the model with.
        """
        assert os.path.isdir(Path(base_file).parent), \
            f"When creating from parameters you must give a path containing the generic final name, prepended by a an existing directory (you gave a directory: {base_file} which doesn't exist)"

        self.mydir = Path(base_file).parent.as_posix()
        self.filenamegen = Path(base_file).name

        if len(myparam.my_param_blocks) == 0:
            myparam.my_param_blocks.append(prev_parameters_blocks())

        self.myparam = myparam
        self.myparam.parent = self

        self.mynap= np.ones([self.myparam.nxfin, self.myparam.nyfin], order='F')

        self.mysuxy = prev_suxsuy(self)
        self.xyfile = xy_file(self)
        self.xyzones = self.xyfile.myzones
        self.myinfil=prev_infiltration(self)
        self.myblocfile=bloc_file(self)

        general = zone(name='General',parent=self.myblocfile.my_vec_blocks)
        # FIXME Line None should be removed but then it fails on some ellipsis later on.
        external_border = bloc_external_border(is2D=True, name='external border', lines=None)  ##< vecteur du contour externe
        general.add_vector(external_border)
        self.myblocfile.my_vec_blocks.add_zone(general)

        myextents = zone(name='Blocks extents',parent=self.myblocfile.my_vec_blocks)
        self.myblocfile.my_vec_blocks.add_zone(myextents)
        self.myblocfile.interior = True


        header = self.get_header()

        self.napbin = WolfArray_Sim2D(whichtype=WOLF_ARRAY_FULL_LOGICAL,
                                      preload=True,
                                      srcheader=header,
                                      masksrc=None)

        # FIXME NAPBIN is special, it is np.int16
        # should it be handled by `whichtype ???`
        # masksrc = None avoid snake eating his own tail
        d = np.zeros_like(self.napbin.array.data, dtype=np.int16)
        self.napbin.array = ma.MaskedArray(d, np.zeros_like(d,dtype=bool))

        # Warning! Without hardening, a write to a masked array
        # will *clear* the mask. But then one is facing another issue.
        # If one wants to write into the array, it has to unmask it. But
        # if the mask is shared, then that will unmask every arrays that
        # share the mask.
        self.napbin.array.harden_mask()
        self.napbin.filename = self.filenamegen+'.napbin'
        self.curmask = self.napbin.array.mask

        def wire_wolf_array(filename,
                            whichtype=WOLF_ARRAY_FULL_SINGLE,
                            preload=False,
                            srcheader=header,
                            masksrc=self.curmask,
                            nullvalue=-99999):

            wa = WolfArray_Sim2D(
                fname = filename,
                whichtype=whichtype,
                preload=preload,
                masksrc=masksrc,
                srcheader=srcheader,
                nullvalue=nullvalue)

            # Warning! This is the only way I have found working to
            # share a mask between several arrays. So, to do that
            # one must pass the mask in the constructor call.
            # (replacing the mask with wa.array.mask == ... won't
            # do !).
            # Other issue: hardening the mask really means: "harden the
            # mask applied to this array". So if one hardens the mask
            # for one array, it will not protect the other arrays
            # sharing the mask. So hardening must be done on all arrays.
            wa.array = ma.MaskedArray(
                np.ones((wa.nbx, wa.nby), order='F', dtype=np.float32)*float(wa.nullvalue),
                mask = masksrc)
            wa.array.harden_mask() # See note about sharing hardened masks
            return wa

        self.top = wire_wolf_array(self.filenamegen+'.top')
        self.topinifine = wire_wolf_array(self.filenamegen+'.topinifine')
        self.frot = wire_wolf_array(self.filenamegen+'.frot')
        self.hbin = wire_wolf_array(self.filenamegen+'.hbin')
        self.qxbin = wire_wolf_array(self.filenamegen+'.qxbin')
        self.qybin = wire_wolf_array(self.filenamegen+'.qybin')
        self.zbin = wire_wolf_array(self.filenamegen+'.zbin')

        # FIXME Why is inf not a WolfArray_Sim2D like the others ?
        self.inf = self.myinfil.myarray
        self.myinfil.masksrc=self.curmask
        self.myinfil.myarray.add_ops_sel()


    # def _init_multibloc(self, mapviewer=None):
    #     # FIXME MultiBlock come after processing by WolfCli
    #     # This code is not yet tested

    #     self.mymnap= WolfArrayMNAP()
    #     self.mymnap.mapviewer=mapviewer
    #     self.mymnap.add_ops_sel()

    #     self.hbinb = WolfArrayMB(whichtype=WOLF_ARRAY_MB_SINGLE,preload=False,mapviewer=mapviewer)
    #     self.hbinb.filename = self.filenamegen+'.hbinb'
    #     # get_header_MB will pick its information from the mnap array.
    #     self.hbinb.set_header(self.get_header_MB())

    #     self.qxbinb = WolfArrayMB( whichtype=WOLF_ARRAY_MB_SINGLE,preload=False,mapviewer=mapviewer)
    #     self.qxbinb.filename = self.filenamegen+'.qxbinb'
    #     self.qxbinb.set_header(self.get_header_MB())

    #     self.qybinb = WolfArrayMB(whichtype=WOLF_ARRAY_MB_SINGLE,preload=False,mapviewer=mapviewer)
    #     self.qybinb.filename = self.filenamegen+'.qybinb'
    #     self.qybinb.set_header(self.get_header_MB())

    #     self.topini = WolfArrayMB(whichtype=WOLF_ARRAY_MB_SINGLE,preload=False,mapviewer=mapviewer)
    #     self.topini.filename = self.filenamegen+'.topini'
    #     self.topini.set_header(self.get_header_MB())


    def __init__(self, *args, dir:str='', from_params: Union[None,prev_parameters_simul]=None,  **kw):
        """ @dir: directory containing the simulation, the
                  base file name (e.g. "simul") will be autodetected.
                  If you create a model from scracth, then you must provide
                  the base file name as well (e.g. "d:/mywolfsim/sim")

            self.wx_exists : If True, then this model will connect itself to the GUI.
                      If False, the model will stand alone (so you can use it outside
                      of the GUI).
        """

        super(Wolf2DModel, self).__init__(*args, **kw)

        self.SPWstations=SPWMIGaugingStations()
        self.DCENNstations=SPWDCENNGaugingStations()

        if from_params is not None:
            self._from_params(base_file=dir, myparam=from_params)
            return

        if dir != '':
            # Either a directory or a file "/_/_/_/dir/simul" for example.

            assert os.path.exists(dir) or os.path.dirname(dir), f"'{dir}' does nto exists"
            #assert os.path.isdir(dir), f"'{dir}' is not a directory"

        if dir=='':
            if self.wx_exists:
                idir=wx.DirDialog(None,"Choose Directory")
                if idir.ShowModal() == wx.ID_CANCEL:
                    self.setup_mapviewer(title='Blank 2D model',wolfparent=self)
                    self.mapviewer.findminmax(True)
                    self.mapviewer.Autoscale(False)
                    self.mapviewer.menu_sim2D()
                    return
            else:
                return

            self.mydir =idir.GetPath()
        else:
            self.mydir=path.normpath(dir)

        if self.wx_exists:
            wait_dlg, wait_cursor = BusyInfo(_('Opening 2D model')), wx.BusyCursor()
            self.setup_mapviewer(title='2D model : '+self.mydir, wolfparent=self)

        try:
            if os.path.exists(self.mydir) and os.path.isfile(self.mydir): # Either a file or doesn't exist
                assert not Path(self.mydir).suffix, \
                    "A generic file path should have no extension," \
                    f" we have {self.mydir}"
                self.filenamegen=self.mydir
                self.mydir = str(Path(self.mydir).parent)
            else:
                # FIXME This is a big problem: we can't decide
                # if self.mydir is intended to be a directory
                # or a path to the generic file. Morevoer the
                # MNAP code confuses the generic name and the
                # .MNAP name when checking if it can load an array.
                if not os.path.exists(self.mydir):
                    self.mydir = os.path.dirname(self.mydir)

                self.filenamegen=""
                second_choice = None
                #recherche du nom générique --> sans extension
                scandir_obj = scandir(self.mydir)
                for curfile in scandir_obj:
                    if curfile.is_file():
                        ext=path.splitext(curfile)
                        if len(ext[1])==0:
                            self.filenamegen = path.join(self.mydir,curfile.name)
                            break
                        elif ext[1] == ".sux":
                            # Some extension present, we choose .sux because
                            # it works, see comment below.
                            second_choice = ext[0]
                scandir_obj.close()

                if self.filenamegen=='':
                    if second_choice:
                        # If the beacon file has not been found, we take
                        # a suitable default.
                        # This is needed when one reads a simulation that
                        # has just been created with the VB application.
                        # In that case, there's no beacon file.
                        self.filenamegen = second_choice
                    else:
                        logging.info(_(f"The provided directory doesn't seem to be a Wolf simulation"))


            logging.info(_(f'Generic file is : {self.filenamegen}'))
            logging.info(_('Creating GUI'))

            self.files_others={'Generic file':[
                ('','First parametric file - historical'),
                ('.par','Parametric file - multiblocks')],
                            'Charachteristics':[
                ('.fil','Infiltration hydrographs [m³/s]'),
                ('.mnap','Resulting mesh [-]'),
                ('.trl','Translation to real world [m]')
                ]}

            self.files_vectors={'Block file':[
                ('.bloc','Blocks geometry')],
                                'Borders':[
                ('.sux','X borders'),
                ('.suy','Y borders')],
                                'Contour':[
                ('.xy','General perimeter')
            ]}

            self.files_MB_array={'Initial Conditions':[
                ('.topini','Bed elevation [m]',WOLF_ARRAY_MB_SINGLE),
                ('.hbinb','Water depth [m]',WOLF_ARRAY_MB_SINGLE),
                ('.qxbinb','Discharge X [m²/s]',WOLF_ARRAY_MB_SINGLE),
                ('.qybinb','Discharge Y [m²/s]',WOLF_ARRAY_MB_SINGLE),
                ('.frotini','Roughness coeff',WOLF_ARRAY_MB_SINGLE)
            ]}

            self.files_fine_array={'Characteristics':[
                ('.napbin','Mask [-]',WOLF_ARRAY_FULL_LOGICAL),
                ('.top','Bed Elevation [m]',WOLF_ARRAY_FULL_SINGLE),
                ('.topini_fine','Bed Elevation - computed [m]',WOLF_ARRAY_FULL_SINGLE),
                ('.frot','Roughness coefficient [law dependent]',WOLF_ARRAY_FULL_SINGLE),
                ('.inf','Infiltration zone [-]',WOLF_ARRAY_FULL_SINGLE),
                ('.hbin','Initial water depth [m]',WOLF_ARRAY_FULL_SINGLE),
                ('.qxbin','Initial discharge along X [m^2/s]',WOLF_ARRAY_FULL_SINGLE),
                ('.qybin','Initial discharge along Y [m^2/s]',WOLF_ARRAY_FULL_SINGLE)
            ]}

            self.fines_array=[]

            logging.info(_('Importing global parameters'))
            self.myparam=prev_parameters_simul(self)
            self.myparam.read_file()

            logging.info(_('Reading mask'))
            self.mynap = self.read_fine_nap()

            logging.info(_('Reading sux-suy'))
            self.mysuxy = prev_suxsuy(self)
            self.mysuxy.read_file()

            logging.info(_('Reading xy'))
            self.xyfile = xy_file(self)
            self.xyzones = self.xyfile.myzones

            logging.info(_('Reading infiltration'))
            self.myinfil=prev_infiltration(self)
            try:
                self.myinfil.read_file()
                self.myinfil.read_array()
            except Exception as ex:
                logging.error(_("Error while reading infinltration file (.INF, .FIL) -- Check you files -- Continuing but without infiltration or Bad positioning"))
                self.myinfil=prev_infiltration(self)

            logging.info(_('Reading blocks'))
            self.myblocfile=bloc_file(self)
            self.myblocfile.read_file()

            logging.info(_('Reading MNAP'))
            self.mymnap= WolfArrayMNAP(self.filenamegen)

            # self.cont_sauv:Zones
            # self.filaire:Zones

            logging.info(_('Treating arrays'))

            #fine resolution
            self.napbin = WolfArray_Sim2D(fname=self.filenamegen+'.napbin',
                                          whichtype=WOLF_ARRAY_FULL_LOGICAL,
                                          preload=True,
                                          mapviewer=self.mapviewer,
                                          srcheader=self.get_header())

            self.curmask = self.napbin.array.mask


            self.top = WolfArray_Sim2D(fname=self.filenamegen+'.top',
                                       whichtype=WOLF_ARRAY_FULL_SINGLE,
                                       preload=False,
                                       mapviewer=self.mapviewer,
                                       masksrc=self.curmask,
                                       srcheader=self.get_header())


            self.topinifine = WolfArray_Sim2D(fname=self.filenamegen+'.topini_fine',
                                              whichtype=WOLF_ARRAY_FULL_SINGLE,
                                              preload=False,
                                              mapviewer=self.mapviewer,
                                              masksrc=self.curmask,
                                              srcheader=self.get_header())


            self.frot = WolfArray_Sim2D(fname=self.filenamegen+'.frot',
                                        whichtype=WOLF_ARRAY_FULL_SINGLE,
                                        preload=False,
                                        mapviewer=self.mapviewer,
                                        masksrc=self.curmask,
                                        srcheader=self.get_header())


            self.inf = self.myinfil.myarray
            self.myinfil.myarray.mapviewer=self.mapviewer
            self.myinfil.masksrc=self.curmask
            self.myinfil.myarray.add_ops_sel()

            self.hbin = WolfArray_Sim2D(fname=self.filenamegen+'.hbin',
                                        whichtype=WOLF_ARRAY_FULL_SINGLE,
                                        preload=False,
                                        mapviewer=self.mapviewer,
                                        masksrc=self.curmask,
                                        srcheader=self.get_header())


            self.qxbin = WolfArray_Sim2D(fname=self.filenamegen+'.qxbin',
                                         whichtype=WOLF_ARRAY_FULL_SINGLE,
                                         preload=False,
                                         mapviewer=self.mapviewer,
                                         masksrc=self.curmask,
                                         srcheader=self.get_header())


            self.qybin = WolfArray_Sim2D(fname=self.filenamegen+'.qybin',
                                         whichtype=WOLF_ARRAY_FULL_SINGLE,
                                         preload=False,
                                         mapviewer=self.mapviewer,
                                         masksrc=self.curmask,
                                         srcheader=self.get_header())


            #altitude de surface libre --> si le fichier n'existe pas, la matrice est créée sur base de l'addition de la topo et de la hauteur
            #  cf surcharge de la lecture dans WolfArray_Sim2D
            self.zbin = WolfArray_Sim2D(fname=self.filenamegen+'.zbin',
                                        whichtype=WOLF_ARRAY_FULL_SINGLE,
                                        preload=False,
                                        mapviewer=self.mapviewer,
                                        masksrc=self.curmask,
                                        srcheader=self.get_header())


            self.fines_array.append(self.napbin)
            self.fines_array.append(self.top)
            self.fines_array.append(self.frot)
            self.fines_array.append(self.inf)
            self.fines_array.append(self.hbin)
            self.fines_array.append(self.qxbin)
            self.fines_array.append(self.qybin)

            #MB resolution
            self.hbinb = WolfArrayMB(fname=self.filenamegen+'.hbinb',
                                     whichtype=WOLF_ARRAY_MB_SINGLE,
                                     preload=True,
                                     mapviewer=self.mapviewer)

            self.hbinb.set_header(self.get_header_MB())

            self.qxbinb = WolfArrayMB(fname=self.filenamegen+'.qxbinb',
                                      whichtype=WOLF_ARRAY_MB_SINGLE,
                                      preload=False,
                                      mapviewer=self.mapviewer)

            self.qxbinb.set_header(self.get_header_MB())

            self.qybinb = WolfArrayMB(fname=self.filenamegen+'.qybinb',
                                      whichtype=WOLF_ARRAY_MB_SINGLE,
                                      preload=False,
                                      mapviewer=self.mapviewer)

            self.qybinb.set_header(self.get_header_MB())

            self.topini = WolfArrayMB(fname=self.filenamegen+'.topini',
                                      whichtype=WOLF_ARRAY_MB_SINGLE,
                                      preload=True,
                                      mapviewer=self.mapviewer)

            self.topini.set_header(self.get_header_MB())
            self.zbinb = self.topini + self.hbinb
            self.zbinb.loaded=True



            if self.wx_exists:
                logging.info(_('Adding arrays to GUI'))

                self.mymnap.mapviewer=self.mapviewer
                self.mymnap.add_ops_sel()

                self.mapviewer.add_object(which='array',newobj=self.napbin,id='mask - fine',ToCheck=True)
                self.mapviewer.add_object(which='array',newobj=self.top,id='bed elevation - fine',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.topinifine,id='bed elevation - computed',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.frot,id='manning roughness - fine',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.inf,id='infiltration',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.mymnap,id='mnap',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.hbin,id='H - IC',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.qxbin,id='QX - IC',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.qybin,id='QY - IC',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.zbin,id='Water level - IC',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.qxbinb,id='QX - IC - MB',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.qybinb,id='QY - IC - MB',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.topini,id='bed elevation - MB',ToCheck=False)
                self.mapviewer.add_object(which='array',newobj=self.zbinb,id='water level - IC - MB',ToCheck=False)

                #vectors
                logging.info(_('Adding vectors to GUI'))
                self.mapviewer.add_object(which='array',newobj=self.hbinb,id='H - IC - MB',ToCheck=False)
                self.mapviewer.add_object(which='vector',newobj=self.xyzones,id='XY',ToCheck=True)
                self.mapviewer.add_object(which='vector',newobj=self.mysuxy.myborders,id='Borders',ToCheck=False)
                self.mapviewer.add_object(which='vector',newobj=self.myblocfile.my_vec_blocks,id='Blocks',ToCheck=False)

                self.mapviewer.add_object(which='other',newobj=self.SPWstations,ToCheck=False,id='SPW-MI stations')
                self.mapviewer.add_object(which='other',newobj=self.DCENNstations,ToCheck=False,id='SPW-DCENN stations')

                logging.info(_('Zooming'))
                self.mapviewer.findminmax(True)
                self.mapviewer.Autoscale(False)

                self.mysuxy.myborders.prep_listogl()
                self.myblocfile.my_vec_blocks.prep_listogl()

                #Fichiers de paramètres
                # self.mainparams=Wolf_Param(self.allviews,filename=self.mydir+'\\Main_model.param',title="Model parameters",DestroyAtClosing=False)
                # self.mainparams.Hide()

                logging.info(_('Adapting menu'))
                self.mapviewer.menu_sim2D()

                logging.info(_('Verifying files'))

            self.verify_files()

        except Exception as ex:
            logging.error(str(ex), exc_info=True)
        finally:
            if self.wx_exists:
                del wait_cursor
                del wait_dlg


    def verify_files(self):
        """
        Vérification de la présence des en-têtes dans les différents fichiers
        """

        fhead = self.get_header()
        mbhead = self.get_header_MB()

        fine = self.files_fine_array['Characteristics']
        for curextent,text,wolftype in fine:
            fname = self.filenamegen + curextent
            if exists(fname):
                fname += '.txt'
                fhead.write_txt_header(fname,wolftype)

        mb = self.files_MB_array['Initial Conditions']
        for curextent,text,wolftype in mb:
            fname = self.filenamegen + curextent
            if exists(fname):
                fname += '.txt'
                mbhead.write_txt_header(fname,wolftype)

        fname = self.filenamegen + '.lst'
        if not exists(fname):
            with open(fname,'w') as f:
                f.write('0\n')

    def mimic_mask(self,source:WolfArray_Sim2D):

        logging.info(_('Copying mask to all arrays'))
        self.curmask = source.array.mask

        for curarray in self.fines_array:
            curarray:WolfArray_Sim2D
            if curarray is not source and curarray.loaded:
                curarray.copy_mask_log(self.curmask)

        logging.info(_('Updating mask array and .nap file'))
        self.napbin.array.data[np.where(np.logical_not(self.curmask))] = -1
        self.napbin.write_all()

    def extend_bed_elevation(self):
        """
        Extension du modèle topographique
        """
        if not self.wx_exists:
            raise Warning('Must be operated by GUI --> Nothing will be done !! or generalize the source code :-) ')

        dlg = wx.MessageDialog(self,_('Do you want to autocomplete elevation from external file?'),style=wx.YES_NO|wx.YES_DEFAULT)
        ret=dlg.ShowModal()
        dlg.Destroy()

        if ret == wx.ID_NO:
            logging.info(_('Nothing to do !'))
            return

        if not self.top.loaded:
            self.top.check_plot()
            self.top.copy_mask_log(self.curmask)
            self.top.loaded=True

        filterArray = "bin (*.bin)|*.bin|all (*.*)|*.*"
        fdlg = wx.FileDialog(self, "Choose file", wildcard=filterArray, style=wx.FD_OPEN)
        if fdlg.ShowModal() != wx.ID_OK:
            fdlg.Destroy()
            return

        filename = fdlg.GetPath()
        fdlg.Destroy()

        logging.info(_('Importing data from file'))
        newtop = WolfArray(fname=filename,mapviewer=self.mapviewer)

        logging.info(_('Finding nodes -- plotting disabled for speed'))
        self.top.mngselection.hideselection = True
        self.top.mngselection.condition_select(2,0., usemask=True)

        if len(self.top.mngselection.myselection)>0:
            newtop.mngselection.myselection = self.top.mngselection.myselection
            newtop.mngselection.hideselection = True
            newtop.mngselection.update_nb_nodes_sections()

            logging.info(_('Copying values'))
            z = newtop.mngselection.get_values_sel()
            logging.info(_('Pasting values'))
            self.top.set_values_sel(self.top.mngselection.myselection, z, False)

        self.top.mngselection.hideselection = False
        self.top.mngselection.myselection=[]
        self.top.copy_mask_log(self.curmask)
        self.top.reset_plot()

        logging.info('')
        logging.info(_('Do not forget to save your changes to files !'))
        logging.info('')

    def extend_freesurface_elevation(self,selection:list):
        """
        Extension des Conditions Initiales
        """

        logging.info(_('Loading necessary values'))
        listarrays=[self.top,self.hbin,self.zbin]
        for curarray in listarrays:
            if not curarray.loaded:
                logging.info('  ' + curarray.idx)
                curarray.check_plot()
                curarray.copy_mask_log(self.curmask)
                curarray.loaded=True
                curarray.mngselection.hideselection = True

        logging.info(_('Hiding positive values'))
        self.hbin.mngselection.myselection = selection.copy()
        self.hbin.mngselection.condition_select(4,0., usemask=True)
        nullvalues = self.hbin.mngselection.myselection.copy()

        nb = len(nullvalues)
        if nb==0:
            logging.info(_('Nothing to do -- exit !'))
            return

        logging.info('  ' + str(len(nullvalues)) + _(' to interpolate'))

        logging.info(_('Hiding null values'))
        self.hbin.mngselection.myselection = selection.copy()
        self.hbin.mngselection.condition_select(2,0., usemask=True)
        nb = len(self.hbin.mngselection.myselection)

        logging.info('  ' + str(nb) + _(' source nodes'))
        if nb<2:
            logging.info(_('Not enough source nodes -- exit !'))
            return

        logging.info(_('Copying selection to zbin'))
        self.zbin.mngselection.myselection = self.hbin.mngselection.myselection.copy()
        z = self.zbin.mngselection.get_values_sel()
        xy = np.asarray(self.zbin.mngselection.myselection)

        logging.info(_('Interpolating free surface'))
        self.zbin.mngselection.myselection = nullvalues.copy()
        self.zbin.interpolate_on_cloud(xy,z,'nearest')

        logging.info(_('Filtering negative values'))
        self.hbin.array = self.zbin.array - self.top.array
        self.hbin.array[np.where(self.hbin.array<0.)]=0.

        self.zbin.array = self.hbin.array+self.top.array

        logging.info(_('Refreshing mask and plot'))
        for curarray in listarrays:
            curarray.copy_mask_log(self.curmask)
            curarray.mngselection.myselection=[]
            curarray.mngselection.hideselection=False
            curarray.reset_plot()

        logging.info('')
        logging.info(_('Do not forget to save your changes to files !'))
        logging.info('')

    def extend_roughness(self,selection:list):
        """
        Extension du frottement
        """
        if not self.wx_exists:
            raise Warning('Must be operated by GUI --> Nothing will be done !! or generalize the source code :-) ')

        # La sélection contient tous les points utiles
        sel=selection.copy()

        dlg = wx.TextEntryDialog(None,_('Which value should be replace by nearest one?'),_('Value'),value='0.04')
        ret = dlg.ShowModal()

        if ret == wx.ID_CANCEL:
            dlg.Destroy()
            return

        oldval = float(dlg.GetValue())
        eps = oldval/1000.
        dlg.Destroy()

        logging.info(_('Loading necessary values'))
        listarrays=[self.frot]
        for curarray in listarrays:
            if not curarray.loaded:
                logging.info('  ' + curarray.idx)
                curarray.check_plot()
                curarray.copy_mask_log(self.curmask)
                curarray.loaded=True
                curarray.mngselection.hideselection = True

        logging.info(_('Selecting old values'))
        self.frot.mngselection.hideselection = True
        self.frot.mngselection.myselection = sel.copy()

        # On cherche les points à interpoler --> on resélectionne les mailles en dehors de l'intervalle
        # La double sélection supprime la maille de la zone déjà sélectionnée
        self.frot.mngselection.condition_select('<>',oldval-eps,oldval+eps, usemask=True)
        nullvalues = self.frot.mngselection.myselection.copy()

        nb = len(nullvalues)
        if nb==0:
            logging.info(_('Nothing to do -- exit !'))
            return

        logging.info('  ' + str(len(nullvalues)) + _(' to interpolate'))

        logging.info(_('Hiding old values'))
        self.frot.mngselection.myselection = sel.copy()

        # On cherche les points depuis où interpoler --> on resélectionne les mailles dans l'intervalle
        # La double sélection supprime la maille de la zone déjà sélectionnée
        self.frot.mngselection.condition_select('>=<=',oldval-eps,oldval+eps, usemask=True)
        nb = len(self.frot.mngselection.myselection)

        logging.info('  ' + str(nb) + _(' source nodes'))
        if nb<2:
            logging.info(_('Not enough source nodes -- exit !'))
            return

        logging.info(_('Interpolating NN'))
        # Récupération des z et xy des mailles actuellement sélectionnées
        z = self.frot.mngselection.get_values_sel()
        xy = np.asarray(self.frot.mngselection.myselection)
        # Recopiage des mailles à interpoler depuis le stockage temporaire
        self.frot.mngselection.myselection = nullvalues
        # Interpolation par voisin le plus proche
        self.frot.interpolate_on_cloud(xy,z,'nearest')

        logging.info(_('Refreshing mask and plot'))
        for curarray in listarrays:
            curarray.copy_mask_log(self.curmask)
            curarray.mngselection.myselection=[]
            curarray.mngselection.hideselection = False
            curarray.mngselection.update_nb_nodes_sections()
            curarray.reset_plot()

        logging.info('')
        logging.info(_('Do not forget to save your changes to files !'))
        logging.info('')

    def set_type_ic(self,which=2,dialog=True):

        if (not self.wx_exists) and dialog:
            raise Warning('Must be operated by GUI --> Nothing will be done !! or generalize the source code :-) ')

        if dialog and self.wx_exists:
            dlg = wx.SingleChoiceDialog(None,_('How do you want to read initial conditions ?'),_('Reading mode'),choices=[_('Text'),_('Binary mono-block'),_('Binary multi-blocks')])
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                dlg.Destroy()
                return

            which = dlg.GetSelection()+1
            dlg.Destroy()

        if which<1 or which>3:
            return

        self.myparam.ntyperead = which
        self.myparam.write_file()

    def replace_external_contour(self,newvec:vector,interior):

        logging.info(_('Copying extrenal contour'))

        logging.info(_('   ... in .bloc'))
        ext_zone:zone
        ext_zone = self.myblocfile.my_vec_blocks.myzones[0]
        ext_zone.myvectors[0] = newvec

        logging.info(_('   ... in xy --> Fortran will update this file after internal meshing process'))
        self.xyzones.myzones[0].myvectors[0] = newvec

        self.myblocfile.my_vec_blocks.reset_listogl()
        self.myblocfile.my_vec_blocks.prep_listogl()

        logging.info(_('Updating .bloc file'))
        self.myblocfile.interior=interior
        self.myblocfile.my_vec_blocks.find_minmax(True)
        self.myblocfile.update_nbmax()
        self.myblocfile.write_file()

    def write_bloc_file(self):

        logging.info(_('Updating .bloc file'))
        self.myblocfile.my_vec_blocks.find_minmax(True)
        self.myblocfile.write_file()

    def get_header_MB(self,abs=False):
        """#> Renvoit un header avec les infos multi-blocs"""
        myheader:header_wolf
        myheader = self.mymnap.get_header(abs=abs)
        for curblock in self.mymnap.myblocks.values():
            myheader.head_blocks[getkeyblock(curblock.blockindex)] = curblock.get_header(abs=abs)
        return  myheader

    def get_header(self,abs=True):
        """#> Renvoit un header de matrice "fine" non MB"""

        curhead = header_wolf()

        curhead.nbx = self.myparam.nxfin
        curhead.nby = self.myparam.nyfin

        curhead.dx = self.myparam.dxfin
        curhead.dy = self.myparam.dyfin

        curhead.origx = self.myparam.xminfin
        curhead.origy = self.myparam.yminfin

        curhead.translx = self.myparam.translx
        curhead.transly = self.myparam.transly

        return curhead

    def read_fine_array(self,which=''):
        """Lecture d'une matrice fine"""

        myarray =WolfArray()
        myarray.set_header(self.get_header())
        myarray.filename = self.filenamegen+which
        myarray.read_data()

        return myarray

    def read_MB_array(self,which=''):
        """Lecture d'une matrice MB"""

        myarray =WolfArrayMB()
        myarray.set_header(self.get_header_MB())
        myarray.filename = self.filenamegen+which
        myarray.read_data()

        return myarray

    def read_fine_nap(self) -> np.ndarray:
        """Lecture de la matrice nap sur le maillage fin"""
        nbx=self.myparam.nxfin
        nby=self.myparam.nyfin

        with open(self.filenamegen +'.napbin', 'rb') as f:
            mynap = np.frombuffer(f.read(nbx*nby*2), dtype=np.int16).copy()
            mynap=np.abs(mynap)

        return mynap.reshape([nbx,nby], order='F')

    def transfer_ic(self,vector):
        """
        Transfert de conditions initiales
        """
        if not self.wx_exists:
            raise Warning('Must be operated by GUI --> Nothing will be done !! or generalize the source code :-) ')

        dlg = wx.DirDialog(None,_('Choose directory containing destination model'),style=wx.DD_DIR_MUST_EXIST)
        ret = dlg.ShowModal()

        if ret==wx.ID_CANCEL:
            dlg.Destroy()
            return

        dstdir = dlg.GetPath()
        dlg.Destroy()

        logging.info(_('Reading destination model'))
        dstmodel = Wolf2DModel(dir=dstdir,splash=False)

        logging.info(_('Reading data sources'))
        srcarrays=[self.top,self.hbin,self.qxbin,self.qybin]
        for loc in srcarrays:
            if not loc.loaded:
                loc.read_data()
                loc.copy_mask_log(self.curmask)

        logging.info(_('Reading data destination'))
        destarrays=[dstmodel.top,dstmodel.hbin,dstmodel.qxbin,dstmodel.qybin]
        for loc in destarrays:
            if not loc.loaded:
                loc.read_data()
                loc.copy_mask_log(dstmodel.curmask)

        logging.info(_('Copying data'))
        for src,dst in zip(srcarrays,destarrays):
            logging.info('  '+src.idx)

            vals,xy = src.get_values_insidepoly(vector,getxy=True)
            dst.set_values_sel(xy,vals)

        logging.info(_('Writing data on disk'))
        for loc in destarrays:
            loc.write_all()

        logging.info(_('Finished !'))

        pass
