from os.path import splitext, exists, join, isfile, basename
from os import listdir, scandir
import numpy as np
from shapely.geometry import LineString, MultiLineString,Point,MultiPoint,Polygon,JOIN_STYLE
from shapely.ops import nearest_points,substring, split
from typing import Literal, Union
import matplotlib.pyplot as plt
from enum import Enum
import logging

from .PyTranslate import _
from .PyVertexvectors import Zones, zone, vector, vectorproperties, getIfromRGB
from .drawing_obj import Element_To_Draw
from .PyTranslate import _
from .wolfresults_2D import views_2D
from .pybridges import stored_values_pos,stored_values_unk, parts_values, operators, stored_values_coords

class Extracting_Zones(Zones):

    def __init__(self, filename='', ox: float = 0, oy: float = 0, tx: float = 0, ty: float = 0, parent=None, is2D=True, idx: str = '', plotted: bool = True, mapviewer=None, need_for_wx: bool = False) -> None:
        super().__init__(filename, ox, oy, tx, ty, parent, is2D, idx, plotted, mapviewer, need_for_wx)
        self.parts = {}
        self.linked = {}

    def find_values_inside_parts(self, linked_arrays):
        """
        Récupère les valeurs à l'intérieur de la zone

        Retour :
         - dictionnaire dont la clé est le nom (ou l'index) du polygone dans la zone --> parties centrale, amont ou aval
         - chaque entrée est un dictionnaire dont la clé 'values' contient un dictionnaire pour chaque matrice du projet
         - chaque élément de ce sous-dictionnaire est un tuple contenant toutes les valeurs utiles

        ***
        ATTENTION : si linked_arrays est un dictionnaire, alors un niveau supérieur est ajouté sur base des clés de ce dictionnaire, dans ce cas, self.linked est un dict et non une liste
        ***

        """
        if isinstance(linked_arrays, dict):

            for curkey, curgroup in linked_arrays.items():
                self.linked[curkey] = [(curlink.idx, type(curlink)) for curlink in curgroup]

        elif isinstance(linked_arrays, list):

            self.linked = [(curlink.idx, type(curlink)) for curlink in linked_arrays]

        for curzone in self.myzones:

            if isinstance(linked_arrays, dict):
                locparts = self.parts[curzone.myname] = {}
                for curkey, curgroup in linked_arrays.items():
                    locparts[curkey] = curzone.get_all_values_linked_polygon(curgroup, key_idx_names='name', getxy=True)
            elif isinstance(linked_arrays, list):
                self.parts[curzone.myname]  = curzone.get_all_values_linked_polygon(linked_arrays, key_idx_names='name', getxy=True)

    def _get_heads(self,
                 which_vec:str,
                 which_group=None):
        """Compute Head"""
        head = {}

        z   = self.get_values(which_vec, stored_values_unk.WATERLEVEL, which_group)
        unorm   = self.get_values(which_vec, stored_values_unk.UNORM, which_group)

        for curkey, cur_z, curunorm,  in zip(z.keys(), z.values(), unorm.values()):
            head[curkey] = cur_z + np.power(curunorm,2)/(2*9.81)

        return head

    def get_values(self,
                   which_vec:str,
                   which_value:Union[stored_values_unk, stored_values_pos, stored_values_coords],
                   which_group=None) -> dict:
        """
        Get values for a specific part

        La donnée retournée est un dictionnaire --> dépend du typage de "self.linked" (cf "find_values_inside_parts)" pour plus d'infos)

        Soit il n'y a qu'un projet à traiter --> le dictionnaire reprend les différentes valeurs pour chaque matrice/simulation du projet
        Soit il y a plusiuers projets à traiter --> le dictionnaire contient autant d'entrées que de projet et chaque sous-dictionnaire reprend les différentes valeurs pour chaque matrice/simulation du projet
        """

        loc_parts_values = None

        if which_group is not None:
            for cur_parts in self.parts.values():
                if which_vec in cur_parts[which_group].keys():
                    loc_parts_values = cur_parts
                    break

        if loc_parts_values is None:
            return {}

        def fillin(pos1, pos2, part_values, part_names):
            locvalues={}

            curpoly = part_values[ which_vec ]
            curarrays = curpoly['values']

            create=False
            for curarray in curarrays.values():
                if isinstance(curarray, tuple):
                    # on a également repris les coordonnées
                    if len(curarray[0])>0:
                        create=True
                else:
                    if len(curarray)>0:
                        create=True

            if create:
                for idarray, curarray in enumerate(curarrays.values()):
                    if isinstance(curarray, tuple):
                        if pos1==-1:
                            if len(curarray[1])>0:
                                vallist = [curval[pos2] for curval in curarray[1]]
                                locvalues[part_names[idarray][0]] = vallist
                        else:
                            if len(curarray[0])>0:
                                vallist = [curval[pos1][pos2] for curval in curarray[0]]
                                locvalues[part_names[idarray][0]] = vallist
                    else:
                        if len(curarray)>0:
                            vallist = [curval[pos1][pos2] for curval in curarray]
                            locvalues[part_names[idarray][0]] = vallist

            return locvalues

        if isinstance(self.linked, dict):
            if which_group in loc_parts_values.keys():
                if which_value in stored_values_unk:
                    if which_value is stored_values_unk.HEAD:
                        values = self._get_heads(which_vec, which_group=which_group)
                    elif which_value in [stored_values_unk.DIFFERENCE_HEAD_UP_DOWN, stored_values_unk.DIFFERENCE_Z_UP_DOWN]:
                        raise Warning(_('Please use get_diff instead of get_values for differences'))
                    else:
                        values = fillin(0, which_value.value[0], loc_parts_values[which_group], self.linked[which_group])
                    return values
                elif which_value in stored_values_pos:
                    values = fillin(1, which_value.value[0], loc_parts_values[which_group], self.linked[which_group])
                    return values
                elif which_value in stored_values_coords:
                    values = fillin(-1, which_value.value[0], loc_parts_values[which_group], self.linked[which_group])
                    return values
                else:
                    return None
            else:
                values={}
                for (curkey, curgroup), curnames in zip(loc_parts_values.items(), self.linked.values()):
                    if which_value in stored_values_unk:
                        if which_value is stored_values_unk.HEAD:
                            values[curkey] = self._get_heads(which_vec, which_group=curgroup)
                        elif which_value in [stored_values_unk.DIFFERENCE_HEAD_UP_DOWN, stored_values_unk.DIFFERENCE_Z_UP_DOWN]:
                            raise Warning(_('Please use get_diff instead of get_values for differences'))
                        else:
                            values[curkey] = fillin(0, which_value.value[0], curgroup, curnames)
                    elif which_value in stored_values_pos:
                        values[curkey] = fillin(1, which_value.value[0], curgroup, curnames)
                    elif which_value in stored_values_coords:
                        values[curkey] = fillin(-1, which_value.value[0], curgroup, curnames)
                return values
        else:
            if which_value in stored_values_unk:
                if which_value is stored_values_unk.HEAD:
                    values = self._get_heads(which_vec)
                elif which_value in [stored_values_unk.DIFFERENCE_HEAD_UP_DOWN, stored_values_unk.DIFFERENCE_Z_UP_DOWN]:
                    raise Warning(_('Please use get_diff instead of get_values for differences'))
                else:
                    values = fillin(0, which_value.value[0], loc_parts_values, self.linked)
                return values
            elif which_value in stored_values_pos:
                values = fillin(1, which_value.value[0], loc_parts_values, self.linked)
                return values
            elif which_value in stored_values_coords:
                values = fillin(-1, which_value.value[0], loc_parts_values, self.linked)
                return values
            else:
                return None

    def get_values_op(self,
                      which_vec:str,
                      which_value:Union[stored_values_unk, stored_values_pos, stored_values_coords],
                      which_group=None,
                      operator:operators=operators.MEDIAN) -> dict:

        loc_parts_values = None

        if which_group is not None:
            for cur_parts in self.parts.values():
                if which_vec in cur_parts[which_group].keys():
                    loc_parts_values = cur_parts
                    break

        if loc_parts_values is None:
            return {}

        def extract_info(vals):
            vals_ret={}
            for curkey, curvals in vals.items():
                if curvals is not None:
                    if operator == operators.MEDIAN:
                        vals_ret[curkey] = np.median(curvals)
                    elif operator == operators.MIN:
                        vals_ret[curkey] = np.min(curvals)
                    elif operator == operators.MAX:
                        vals_ret[curkey] = np.max(curvals)
                    elif operator == operators.PERCENTILE95:
                        vals_ret[curkey] = np.percentile(curvals,95)
                    elif operator == operators.PERCENTILE5:
                        vals_ret[curkey] = np.percentile(curvals,5)
                    elif operator == operators.ALL:
                        vals_ret[curkey] =  (np.median(curvals), np.min(curvals), np.max(curvals), np.percentile(curvals,95), np.percentile(curvals,5))
            return vals_ret

        vals = self.get_values(which_vec, which_value, which_group)

        if isinstance(self.linked, dict):
            if which_group in loc_parts_values.keys():
                vals_ret = extract_info(vals)
            else:
                vals_ret={}
                for curkey, curvals in vals.items():
                    vals_ret[curkey] = extract_info(curvals)
        else:
            vals_ret = extract_info(vals)

        return vals_ret

class Polygons_Analyze(Zones):
    """
    """

    def __init__(self, myfile='', ds:float=5., ox: float = 0, oy: float = 0, tx: float = 0, ty: float = 0, parent=None, is2D=True, wx_exists:bool = False):
        super().__init__(myfile, ox, oy, tx, ty, parent, is2D, wx_exists)

        self.myname = splitext(basename(myfile))[0]

        self.riverbed = self.get_zone(0).myvectors[1]
        self.riverbed.prepare_shapely()

        self.polygons_zone:zone
        self.polygons_zone = self.get_zone(-1)
        self.polygons_curvi = {}
        for curvert in self.polygons_zone.myvectors:
            self.polygons_curvi[curvert.myname] = curvert.myvertices[0].z

        for vec in self.polygons_zone.myvectors:
            vec.myprop.used=False # cache les polygones pour ne pas surcharger l'affichage éventuel

    def colorize(self):
        """Colorisation des polygones pour l'interface graphique"""
        self.centralpart.myprop.color = getIfromRGB((0,255,0))
        self.upstream.myprop.color = getIfromRGB((255,0,0))
        self.downstream.myprop.color = getIfromRGB((0,0,255))

    def highlighting(self, rgb=(255,0,0), linewidth=3):
        """
        Mise en évidence
        """
        self.centralpart.highlighting(rgb,linewidth)

    def withdrawal(self):
        """
        Mise en retrait
        """
        self.centralpart.withdrawal()

    def compute_distance(self, poly:LineString):
        """
        Compute the curvilinear distance along a support polyline
        """
        for curvert in self.polygons_zone.myvectors:
            centerx = np.sum(np.asarray([cur.x for cur in curvert.myvertices[:4]]))/4.
            centery = np.sum(np.asarray([cur.y for cur in curvert.myvertices[:4]]))/4.
            self.polygons_curvi[curvert.myname] = poly.project(Point([centerx,centery]))

    def find_values_inside_parts(self, linked_arrays):
        """
        Récupère les valeurs à l'intérieur :
         - des parties du pont (amont, centrale, aval)
         - de la discrétisation rivière en polygones

        Retour :
         - dictionnaire dont la clé est le nom (ou l'index) du polygone dans la zone --> parties centrale, amont ou aval
         - chaque entrée est un dictionnaire dont la clé 'values' contient un dictionnaire pour chaque matrice du projet
         - chaque élément de ce sous-dictionnaire est un tuple contenant toutes les valeurs utiles

        ***
        ATTENTION : si linked_arrays est un dictionnaire, alors un niveau supérieur est ajouté sur base des clés de ce dictionnaire, dans ce cas, self.linked est un dict et non une liste
        ***

        """

        self.linked={}
        for curkey, curgroup in linked_arrays.items():
            self.linked[curkey] = [(curlink.idx, type(curlink)) for curlink in curgroup]

        # récupération des valeurs danbs les polygones "rivière"
        curzone = self.polygons_zone
        if curzone is not None:
            if isinstance(linked_arrays, dict):
                self.river_values={}
                for curkey, curgroup in linked_arrays.items():
                    self.river_values[curkey] = curzone.get_all_values_linked_polygon(curgroup, key_idx_names='name')
            elif isinstance(linked_arrays, list):
                self.river_values = curzone.get_all_values_linked_polygon(linked_arrays, key_idx_names='name')

    def _get_river_heads(self,
                       which_group=None):
        """Compute Head"""
        head = {}

        z   = self.get_river_values(stored_values_unk.WATERLEVEL, which_group)
        unorm   = self.get_river_values(stored_values_unk.UNORM, which_group)

        for curkey, cur_z, curunorm  in zip(z.keys(), z.values(), unorm.values()):
            curdict = head[curkey] = {}

            for curgroup, zpoly, unormpoly in zip(cur_z.keys(), cur_z.values(), curunorm.values()):
                curdict[curgroup] = zpoly + np.power(unormpoly,2)/(2*9.81)

        return head

    def get_river_values(self,
                         which_value:Union[stored_values_unk,stored_values_pos],
                         which_group=None) -> dict:
        """
        Get values for the river polygons

        La donnée retournée est un dictionnaire --> dépend du typage de "self.linked" (cf "find_values_inside_parts)" pour plus d'infos)

        Soit il n'y a qu'un projet à traiter --> le dictionnaire contient une entrée pour chaque polygone et les différentes valeurs pour chaque matrice/simulation du projet dans chaque polygone
        Soit il y a plusiuers projets à traiter --> le dictionnaire contient autant d'entrées que de projet et chaque sous-dictionnaire reprend les différentes valeurs comme ci-dessus
        """

        if self.river_values is None:
            raise Warning(_('Firstly call find_values_inside_parts with linked_arrays as argument -- Retry !'))

        def fillin(pos1, pos2, river_values, part_names):
            locvalues={}

            for curkey, curpoly in river_values.items():
                curdict = locvalues[curkey]={}

                curarrays = curpoly['values']

                create=False
                for curarray in curarrays.values():
                    if len(curarray)>0:
                        create=True

                if create:
                    for idarray, curarray in enumerate(curarrays.values()):
                        if len(curarray)>0:
                            vallist = [curval[pos1][pos2] for curval in curarray]
                            curdict[part_names[idarray][0]] = vallist

            return locvalues

        if isinstance(self.linked, dict):
            if which_group in self.river_values.keys():
                if which_value in stored_values_unk:
                    if which_value is stored_values_unk.HEAD:
                        values = self._get_river_heads(which_group=which_group)
                    else:
                        values = fillin(0, which_value.value[0], self.river_values[which_group], self.linked[which_group])
                    return values
                elif which_value in stored_values_pos:
                    values = fillin(1, which_value.value[0], self.river_values[which_group], self.linked[which_group])
                    return values
                else:
                    return None
            else:
                values={}
                for (curkey, curgroup), curnames in zip(self.river_values.items(), self.linked.values()):
                    if which_value in stored_values_unk:
                        if which_value is stored_values_unk.HEAD:
                            values[curkey] = self._get_river_heads(which_group=curkey)
                        else:
                            values[curkey] = fillin(0, which_value.value[0], curgroup, curnames)
                    elif which_value in stored_values_pos:
                        values[curkey] = fillin(1, which_value.value[0], curgroup, curnames)
                return values
        else:
            if which_value in stored_values_unk:
                if which_value is stored_values_unk.HEAD:
                    values = self._get_river_heads()
                elif which_value in [stored_values_unk.DIFFERENCE_HEAD_UP_DOWN, stored_values_unk.DIFFERENCE_Z_UP_DOWN]:
                    raise Warning(_('Please use get_diff instead of get_values for differences'))
                else:
                    values = fillin(0, which_value.value[0], self.river_values, self.linked)
                return values
            elif which_value in stored_values_pos:
                values = fillin(1, which_value.value[0], self.river_values, self.linked)
                return values
            else:
                return None

    def get_river_values_op(self,
                            which_value:Union[stored_values_unk,stored_values_pos],
                            which_group=None,
                            operator:operators=operators.MEDIAN) -> dict:

        def extract_info(vals):
            vals_ret={}
            for curkeypoly, curpoly in vals.items():
                curdict = vals_ret[curkeypoly]={}
                for curkey, curvals in curpoly.items():
                    if curvals is not None:
                        if operator == operators.MEDIAN:
                            curdict[curkey] = np.median(curvals)
                        elif operator == operators.MIN:
                            curdict[curkey] = np.min(curvals)
                        elif operator == operators.MAX:
                            curdict[curkey] = np.max(curvals)
                        elif operator == operators.PERCENTILE95:
                            curdict[curkey] = np.percentile(curvals,95)
                        elif operator == operators.PERCENTILE5:
                            curdict[curkey] = np.percentile(curvals,5)
                        elif operator == operators.ALL:
                            curdict[curkey] =  (np.median(curvals), np.min(curvals), np.max(curvals), np.percentile(curvals,95), np.percentile(curvals,5))
            return vals_ret

        vals = self.get_river_values(which_value, which_group)

        if isinstance(self.linked, dict) and which_group is None:
            vals_ret={}
            for curkey, curvals in vals.items():
                vals_ret[curkey] = extract_info(curvals)
        else:
            vals_ret = extract_info(vals)

        return vals_ret

    def plot_unk(self,
                 figax = None,
                 which_value:Union[stored_values_unk,stored_values_pos]=stored_values_unk.WATERLEVEL,
                 which_group=None,
                 operator:operators=operators.MEDIAN,
                 options:dict=None,
                 label=True,
                 show=False):

        if figax is None:
            fig,ax = plt.subplots(1,1)
        else:
            fig,ax = figax

        curmark='None'
        curcol = 'black'
        curlw = 1
        curls = 'solid'
        if options is not None:
            if isinstance(options,dict):
                if 'marker' in options.keys():
                    curmark=options['marker']
                if 'color' in options.keys():
                    curcol=options['color']
                if 'linestyle' in options.keys():
                    curls=options['linestyle']
                if 'linewidth' in options.keys():
                    curlw=options['linewidth']

        myval = self.get_river_values_op(which_value, which_group, operator)

        if which_group is not None:
            curproj = self.river_values[which_group]
            firstpoly = curproj[list(curproj.keys())[0]]

            nb_mod = len(firstpoly['values'])
            for curmodkey, curmod in firstpoly['values'].items():

                labelstr=''
                if label: labelstr=curmodkey

                if nb_mod>1:
                    if which_value!= stored_values_unk.TOPOGRAPHY:
                        curcol = None

                s=[]
                val=[]

                for curkey, curval in myval.items():
                    if len(curval)>0 and curmodkey in curval.keys():
                            val.append(curval[curmodkey])
                            s.append(self.polygons_curvi[curkey])

                ax.plot(s, val, linewidth = curlw, linestyle=curls, marker=curmark, color=curcol, label=labelstr)
        else:

            for keyproj, curproj in self.river_values.items():
                firstpoly = curproj[list(curproj.keys())[0]]
                nb_mod = len(firstpoly['values'])

                for curmodkey, curmod in firstpoly['values'].items():

                    labelstr=''
                    if label: labelstr=curmodkey

                    if nb_mod>1:
                        if which_value!= stored_values_unk.TOPOGRAPHY:
                            curcol = None

                    s=[]
                    val=[]

                    for curkey, curval in myval[keyproj].items():
                        if len(curval)>0 and curmodkey in curval.keys():
                                val.append(curval[curmodkey])
                                s.append(self.polygons_curvi[curkey])

                    ax.plot(s, val, linewidth = curlw, linestyle=curls, marker=curmark, color=curcol, label=labelstr)
        if show:
            fig.show()

        return fig,ax

    def plot_waterline(self,
                       figax=None,
                       which_group=None,
                       operator:operators=operators.MEDIAN,
                       show=False):

        fig,ax = self.plot_unk(figax, stored_values_unk.TOPOGRAPHY, which_group, operator, options={'color':'black', 'linewidth':2}, label=False, show=False)
        figax=(fig,ax)
        self.plot_unk(figax, stored_values_unk.WATERLEVEL, which_group, operator, options={'color':'blue', 'linewidth':2}, label=True, show=False)

        ax.set_ylabel(_('Water leval [mDNG]'))
        ax.set_xlabel(_('Abscissa from upstream [m]'))
        fig.suptitle(self.myname + ' -- ' +_('Water surface profile'))

        if show:
            fig.show()

        return fig,ax

    def plot_bedelevation(self,
                       figax=None,
                       which_group=None,
                       operator:operators=operators.MEDIAN,
                       show=False):

        fig,ax = self.plot_unk(figax, stored_values_unk.TOPOGRAPHY, which_group, operator, options={'color':'black', 'linewidth':2}, label=False, show=False)

        ax.set_ylabel(_('Bed elevation [mDNG]'))
        ax.set_xlabel(_('Abscissa from upstream [m]'))

        if show:
            fig.show()

        return fig,ax

    def plot_stage(self,
                       figax=None,
                       which_group=None,
                       operator:operators=operators.MEDIAN,
                       show=False):

        fig,ax = self.plot_unk(figax, stored_values_unk.WATERLEVEL, which_group, operator, options={'color':'blue', 'linewidth':2}, show=False)

        ax.set_ylabel(_('Water stage [mDNG]'))
        ax.set_xlabel(_('Abscissa from upstream [m]'))

        if show:
            fig.show()

        return fig,ax

    def plot_waterhead(self,
                       figax=None,
                       which_group=None,
                       operator:operators=operators.MEDIAN,
                       show=False):

        fig,ax = self.plot_unk(figax, stored_values_unk.HEAD, which_group, operator, options={'color':'blue', 'linewidth':2}, show=False)

        ax.set_ylabel(_('Water head [m_water]'))
        ax.set_xlabel(_('Abscissa from upstream [m]'))
        fig.suptitle(self.myname + ' -- ' +_('Water head profile'))

        if show:
            fig.show()

        return fig,ax
