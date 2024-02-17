import numpy as np
import numpy.ma as ma
from os import path
from pathlib import Path
from scipy.sparse import csr_array
from multiprocessing import Pool
from typing import Union
from tqdm import tqdm
import logging

from .PyTranslate import _
from .wolf_array import WolfArray
from .wolfresults_2D import Wolfresults_2D, views_2D, getkeyblock, OneWolfResult
from .CpGrid import CpGrid
from .PyPalette import wolfpalette

try:
    from wolfgpu.results_store import ResultsStore, ResultType
except :
    logging.error(_("Unable to import wolfgpu.results_store.ResultsStore. Please install wolfgpu package or add a symlink to the wolfgpu package in the wolfhece directory"))
    # raise ImportError(_("Unable to import wolfgpu.results_store.ResultsStore. Please install wolfgpu package or add a symlink to the wolfgpu package in the wolfhece directory"))

def _load_res(x) -> tuple[csr_array, csr_array, csr_array]:
    store:ResultsStore
    i:int

    store, i = x
    _, _, _, _, wd_np, qx_np, qy_np = store.get_result(i+1)

    if isinstance(wd_np, csr_array) and isinstance(qx_np, csr_array) and isinstance(qy_np, csr_array):
        return wd_np, qx_np, qy_np
    else:
        return csr_array(wd_np), csr_array(qx_np), csr_array(qy_np)

def _load_res_h(x) -> tuple[csr_array, csr_array, csr_array]:
    store:ResultsStore
    i:int

    store, i = x
    wd_np = store.get_named_result('h',i+1)

    if isinstance(wd_np, csr_array):
        return wd_np
    else:
        return csr_array(wd_np)

class Cache_Results2DGPU():
    """
    Gestion en mémoire de plusieurs résultats GPU
    Stockage CSR afin d'économiser la mémoire (Scipy CSR)
    """

    def __init__(self, fname:str, start_idx:int, end_idx:int = -1, only_h=False) -> None:
        """
        Chargement de résultats sur base du répertoire de sauvegarde de la simulation GPU

        Lecture des résultats depuis start_idx jusque end_idx

        only_h force la lecture de la hauteur d'eau seulement, sinon (h,qx,qy)
        """

        self._results:Union[dict[str,tuple[csr_array, csr_array, csr_array]], dict[str,csr_array]] # typage

        # ResultsStore unique
        self._result_store = ResultsStore(Path(fname), mode='r')
        self._only_h = only_h

        if end_idx == -1:
            end_idx = self._result_store.nb_results

        if end_idx>start_idx:
            self.start_idx = int(max(start_idx,0))
            self.end_idx   = int(min(end_idx, self._result_store.nb_results))

            # Lecture en multiprocess des résultats
            if only_h:
                with Pool() as pool:
                    _results = pool.map(_load_res_h, [(self._result_store,i) for i in range(self.start_idx, self.end_idx)])
                    self._results = {i+1:res for i,res in enumerate(_results)}
            else:
                with Pool() as pool:
                    _results = pool.map(_load_res, [(self._result_store,i) for i in range(self.start_idx, self.end_idx)])
                    self._results = {i+1:res for i,res in enumerate(_results)}

    @property
    def only_h(self):
        return self._only_h

    def __getitem__(self,i:int):
        """Surcharge de l'opérateur []"""
        return self._results[i]

    def get_h(self, idx:int, dense:bool=True) -> Union[np.ndarray, csr_array]:
        """
        Retourne la matrice de hauteur d'eau de la position idx (0-based)
            - en CSR (Scipy CSR)
            - en dense (Numpy array)
        """
        if not self.only_h:
            return self._results[idx][0].toarray() if dense else self._results[idx][0]
        else:
            return self._results[idx].toarray() if dense else self._results[idx]

    def get_qx(self,idx:int, dense:bool=True) -> Union[np.ndarray, csr_array]:
        """
        Retourne la matrice de débit X d'eau de la position idx (0-based)
            - en CSR (Scipy CSR)
            - en dense (Numpy array)
        """

        if not self.only_h:
            return self._results[idx][1].toarray() if dense else self._results[idx][1]
        else:
            return None

    def get_qy(self,idx:int, dense:bool=True) -> Union[np.ndarray, csr_array]:
        """
        Retourne la matrice de débit Y d'eau de la position idx (0-based)
            - en CSR (Scipy CSR)
            - en dense (Numpy array)
        """

        if not self.only_h:
            return self._results[idx][2].toarray() if dense else self._results[idx][2]
        else:
            return None

    # def danger_map(self, start:int=0, end:int=-1, every:int=1) -> Union[WolfArray, tuple[WolfArray, WolfArray, WolfArray]]:
    #     """
    #     Create Danger Maps

    #     From start to end (index 0-based)
    #     Indexes are related to the self._results, not the absolute GPU results
    #     """

    #     # If __init__ with only_h==True, only wd is pre-loaded into memory
    #     # all_maps ==True is more than one Numpy array in self.results
    #     all_maps = not self.only_h

    #     # Number of  time steps
    #     number_of_time_steps = len(self._results)
    #     if end ==-1:
    #         end = number_of_time_steps

    #     # Init Danger Maps based on results type
    #     # GPU --> 1 block, Numpy array
    #     danger_map_matrix_h = self.get_h(0, dense=True)

    #     # set zeros
    #     danger_map_matrix_h[:,:] = 0.

    #     if all_maps:
    #         danger_map_matrix_v   = danger_map_matrix_h.copy()
    #         danger_map_matrix_mom = danger_map_matrix_h.copy()
    #         danger = [danger_map_matrix_h, danger_map_matrix_v, danger_map_matrix_mom]

    #     if all_maps:

    #         for time_step in tqdm(range(start, end, every)):

    #             wd = self.get_h(time_step, dense=True)
    #             qx = self.get_qx(time_step, dense=True)
    #             qy = self.get_qy(time_step, dense=True)

    #             v = np.zeros(wd.shape)
    #             mom = np.zeros(wd.shape)

    #             i,j = np.where(wd > 0.)
    #             v[i,j] = (qx[i,j]**2.+qy[i,j]**2.)**.5/wd[i,j]

    #             mom = v*wd

    #             comp = [wd, v, mom]

    #             # Comparison
    #             for curdanger, curcomp in zip(danger, comp):
    #                 i,j = np.where(curdanger < curcomp)
    #                 curdanger[i,j] = curcomp[i,j]

    #     else:
    #         for time_step in tqdm(range(start, end, every)):

    #             wd = self.get_h(time_step)
    #             i,j = np.where(danger_map_matrix_h < wd)
    #             danger_map_matrix_h[i,j] = wd[i,j]


    #     if all_maps:
    #         return (danger_map_matrix_h, danger_map_matrix_v, danger_map_matrix_mom)
    #     else:
    #         return danger_map_matrix_h


class wolfres2DGPU(Wolfresults_2D):
    """
    Gestion des résultats du code GPU 2D
    Surcharge de "Wolfresults_2D"
    """

    def __init__(self,
                 fname:str,
                 eps=0.,
                 idx: str = '',
                 plotted: bool = True,
                 mapviewer=None,
                 store = None):

        super().__init__(fname = str(Path(fname)), eps=eps, idx=idx, plotted=plotted, mapviewer=mapviewer, loader=self._loader)

        # MERGE Inheriting is a bad idea in general because it allows
        # classes to look inside others, and induces hard
        # coupling. It's better to connect with instances and use
        # their functions so that the provider can better enforce what
        # is available to class's users.

        if store is None:
            self._result_store = ResultsStore(sim_path = Path(fname), mode='r')
        else:
            self._result_store = store

        self._cache = None

    def setup_cache(self, start_idx:int, end_idx:int = -1, only_h:bool = False):
        """
        Setup cache from start_idx result to end_idx result

        if only_h is True, only waterdepth is loaded into memory
        """
        self._cache = Cache_Results2DGPU(self.filename, start_idx, end_idx, only_h= only_h)

    def clear_cache(self):
        """
        Clear cache
        """
        self._cache = None

    def _loader(self, fname:str):
        # 2D GPU

        self.filename = fname
        sim_path = Path(fname).parent

        nb_blocks = 1
        self.myblocks = {}
        curblock = OneWolfResult(0, parent=self)
        self.myblocks[getkeyblock(0)] = curblock

        if path.exists(path.join(sim_path, 'simul.top')):

            curblock.top = WolfArray(path.join(sim_path, 'simul.top'), nullvalue=99999.)
            curblock.waterdepth = WolfArray(path.join(sim_path, 'simul.hbin'))
            curblock.qx = WolfArray(path.join(sim_path, 'simul.qxbin'))
            curblock.qy = WolfArray(path.join(sim_path, 'simul.qybin'))
            curblock.rough_n = WolfArray(path.join(sim_path, 'simul.frot'))

        elif path.exists(path.join(sim_path, 'bathymetry.npy')):
            curblock.top = WolfArray(path.join(sim_path, 'bathymetry.npy'), nullvalue=99999.)
            curblock.waterdepth = WolfArray(path.join(sim_path, 'h.npy'))
            curblock.qx = WolfArray(path.join(sim_path, 'qx.npy'))
            curblock.qy = WolfArray(path.join(sim_path, 'qy.npy'))
            curblock.rough_n = WolfArray(path.join(sim_path, 'manning.npy'))

            if path.exists(path.join(sim_path, 'parameters.json')):

                import json
                with open(path.join(sim_path, 'parameters.json'), 'r') as fp:

                    params = json.load(fp)

                    try:
                        curblock.top.dx = params["parameters"]["dx"]
                        curblock.top.dy = params["parameters"]["dy"]
                    except:
                        logging.error(_('No spatial resolution (dx,dy) in parameters.json -- Results will not be shown in viewer'))

                    try:
                        curblock.top.origx = params["parameters"]["base_coord_x"]
                        curblock.top.origy = params["parameters"]["base_coord_y"]
                    except:
                        logging.error(_('No spatial position (base_coord_x,base_coord_y) in parameters.json -- Results will not be spatially based'))

        self.loaded_rough = True

        self.head_blocks[getkeyblock(0)] = curblock.top.get_header()

        to_check =[curblock.waterdepth, curblock.qx, curblock.qy, curblock.rough_n]
        check = False
        for curarray in to_check:
            check |= curarray.dx != curblock.top.dx
            check |= curarray.dy != curblock.top.dy
            check |= curarray.origx != curblock.top.origx
            check |= curarray.origy != curblock.top.origy
            check |= curarray.translx != curblock.top.translx
            check |= curarray.transly != curblock.top.transly

        if check:
            if path.exists(path.join(sim_path, 'simul.top')):
                logging.error(_("Inconsistent header file in .top, .qxbin, .qybin or .frot files"))
                logging.error(_("Forcing information into memory from the .top file -- May corrupt spatial positionning -- Please check your data !"))

            for curarray in to_check:
                curarray.dx    = curblock.top.dx
                curarray.dy    = curblock.top.dy
                curarray.origx = curblock.top.origx
                curarray.origy = curblock.top.origy
                curarray.translx = curblock.top.translx
                curarray.transly = curblock.top.transly

        if path.exists(path.join(sim_path, 'simul.trl')):
            with open(path.join(sim_path, 'simul.trl')) as f:
                trl=f.read().splitlines()
                self.translx=float(trl[1])
                self.transly=float(trl[2])

        curblock.set_current(views_2D.WATERDEPTH)

        self.myparam = None
        self.mymnap = None
        self.myblocfile = None

    def get_nbresults(self, force_update_timessteps=True):
        """
        Récupération du nombre de résultats

        Lecture du fichier de tracking afin de permettre une mise à jour en cours de calcul
        """
        self._result_store.reload()
        if force_update_timessteps:
            self.get_times_steps()

        self._nb_results = self._result_store.nb_results
        return self._result_store.nb_results

    def read_oneresult(self, which:int=-1):
        """
        Lecture d'un pas de sauvegarde

        which: result number to read; 0-based; -1 == last one
        """

        which = self._sanitize_result_step(which)

        # stored result files are 1-based -> which+1
        if self._cache is not None:
            if (which >= self._cache.start_idx and which < self._cache.end_idx) and (not self._cache.only_h):
                wd_np = self._cache.get_h(which+1, True)
                qx_np = self._cache.get_qx(which+1, True)
                qy_np = self._cache.get_qy(which+1, True)
            else:
                _, _, _, _, wd_np, qx_np, qy_np = self._result_store.get_result(which+1)
        else:
            _, _, _, _, wd_np, qx_np, qy_np = self._result_store.get_result(which+1)

        curblock = self.myblocks[getkeyblock(1,False)]
        if self.epsilon > 0.:
            curblock.waterdepth.array=ma.masked_less_equal(wd_np.astype(np.float32).T, self.epsilon)
        else:
            curblock.waterdepth.array=ma.masked_equal(wd_np.astype(np.float32).T, 0.)

        curblock.qx.array=ma.masked_where(curblock.waterdepth.array.mask,qx_np.astype(np.float32).T)
        curblock.qy.array=ma.masked_where(curblock.waterdepth.array.mask,qy_np.astype(np.float32).T)

        curblock.waterdepth.count()
        curblock.qx.count()
        curblock.qy.count()

        curblock.waterdepth.set_nullvalue_in_mask()
        curblock.qx.set_nullvalue_in_mask()
        curblock.qy.set_nullvalue_in_mask()

        self.current_result = which
        self.loaded=True

    def _update_result_view(self):
        """
        Procédure interne de mise à jour du pas

        Etapes partagées par read_next et read_previous
        """
        self.current_result = self._sanitize_result_step(self.current_result)
        self.read_oneresult(self.current_result)

    def read_next(self):
        """
        Lecture du pas suivant
        """
        self.current_result+=1
        self._update_result_view()

    def get_times_steps(self):
        """
        Récupération des temps réels et les pas de calcul de chaque résultat sur disque
        """
        self.times = [time[ResultType.T.value] for time in self._result_store._sim_times]
        self.timesteps = [time[ResultType.STEP_NUM.value] for time in self._result_store._sim_times]

        return self.times, self.timesteps

    def read_previous(self):
        """
        Lecture du pas suivant
        """
        self.current_result -= 1
        self._update_result_view()

    def get_cached_h(self, idx):
        """ Return cached water depth according to WOLF convention """

        if self._cache is not None:
            return self._cache.get_h(idx+1, True).T
        else:
            return None

    def get_cached_qx(self, idx):
        """ Return cached specific discharge along X according to WOLF convention """

        if self._cache is not None:
            return self._cache.get_qx(idx+1, True).T
        else:
            return None

    def get_cached_qy(self, idx):
        """ Return cached specific discharge along Y according to WOLF convention """

        if self._cache is not None:
            return self._cache.get_qy(idx+1, True).T
        else:
            return None
