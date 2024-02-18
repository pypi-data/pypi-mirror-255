
from os.path import exists, join
import json
from enum import Enum
from typing import Literal
from concurrent.futures import ThreadPoolExecutor
import logging

from .PyParams import Wolf_Param, key_Param
from .PyVertexvectors import Zones, vector, zone
from .PyPalette import wolfpalette
from .PyTranslate import _
from .wolfresults_2D import Wolfresults_2D, views_2D

class project_type(Enum):
    GENERIC = 0
    WOLF2D  = 1

class Project(Wolf_Param):
    """
    Projet WOLF

    Il s'agit d'une surcharge d'un objet Wolf_Param qui est organisé en groupes de paramètres
    Chaque paramètre peut être défini par une clé, une valeur et un commentaire (+ éventuellement une chaîne JSON)
    """
    def __init__(self, wdir='', parent=None, title="Default Title", w=500, h=800, ontop=False, to_read=True, filename='', withbuttons=True, DestroyAtClosing=True, toShow=True):
        super().__init__(parent, title, w, h, ontop, to_read, filename, withbuttons, DestroyAtClosing, toShow)
        self.wdir = wdir

class Wolf2D_Project(Project):
    """
    Projet d'analyse de simulations WOLF2D

    Ce projet contient a priori :
        - une liste de simulations  (groupe "wolf2d")
        - une liste de vecteurs/polylignes afin de restreindre la zone d'analyse et éviter
            autant que possible la superposition des modèles (groupe "vectors")
        - la liaison entre polyligne et modèle (groupe "vector_array_link")
        - des palettes (groupe "palette")
        - la liaison des palettes avec les modèles (groupe "palette-array")

    Chaque simulation est associée à une clé unique
    Chaque vecteur est associé à une clé unique
    Chaque palette est associée à une clé unique

    Les liaisons simulation-vecteur se font par (clé-valeur) = (sim-vector)
    Les liaisons simulation-palette se font par (clé-valeur) = (sim-palette)

    Exemple :

    wolf2d:
    Confluence Wayai - Forges Thiry_B	.\Q25\X1b - Hoegne - Tr 3 - Confluence Wayai - Forges Thiry\simul
    Confluence Wayai - Forges Thiry_A	.\Q25\X1a - Hoegne - Tr 3 - Confluence Wayai - Forges Thiry\simul
    vector:
    polyd5	..\Vecteurs\161 - Vesdre - Tr 3 - Chaudfontaine - Confluence Ourthe\cont_sauv.vec
    polyd4	..\Vecteurs\162 - Vesdre - Tr 3 - Prayon - Chaudfontaine\cont_sauv.vec
    vector_array_link:
    Confluence Wayai - Forges Thiry_B	polyX1
    Confluence Wayai - Forges Thiry_A	polyX1
    palette:
    Q25	q25_alea.pal
    Q50	q50_alea.pal
    Q100	q100_alea.pal
    palette-array:
    Confluence Wayai - Forges Thiry_B	Q25
    Confluence Wayai - Forges Thiry_A	Q25
    """

    def __init__(self, wdir='', parent=None, title="Default Title", w=500, h=800, ontop=False, to_read=True, filename='', withbuttons=True, DestroyAtClosing=True, toShow=False):
        super().__init__(wdir, parent, title, w, h, ontop, to_read, filename, withbuttons, DestroyAtClosing, toShow)

        self.mysims:dict[str,Wolfresults_2D]={}
        self.mycontours={}
        self.mycolormaps={}
        self.epsilon=5e-4

        self.poly = None
        self.poly_values = None

    def load_simulations(self, epsilon, verbose=False):
        """
        Load all simulations in current project
        """
        self.epsilon = epsilon
        sims = self.get_group('wolf2d')

        for key,val in sims.items():
            if verbose:
                print(key)

            cursim = self.mysims[key] = Wolfresults_2D(join(self.wdir, val[key_Param.VALUE]), eps=epsilon, idx=key)
            cursim.plotted=True

        self.set_vectors()
        self.set_colormap()

        for key,val in sims.items():
            cursim = self.mysims[key]
            cursim.read_oneresult()

    def update_simulations(self, epsilon, verbose=False):
        """
        update all simulations in current project
        """
        self.epsilon = epsilon

        for cursim in self.mysims.values():
            cursim.read_oneresult()

    def get_simulations(self) -> list:
        """
        Return a python list of simulations
        """
        return list(self.mysims.values())

    def set_vectors(self):
        """
        Lie les vecteurs d'un fichier projet et leur liaison potentielle avec les matrices
        """

        vec = self.get_group('vector')
        if vec is  None:
            return

        for curkey,curvec in vec.items():

            filename=''
            if exists(curvec[key_Param.VALUE]):
                filename = curvec
            elif exists(join(self.wdir,curvec[key_Param.VALUE])):
                filename = join(self.wdir,curvec[key_Param.VALUE])

            if filename!='':
                self.mycontours[curkey] = Zones(filename)

        links = self.get_group('vector_array_link')
        if links is not None:
            for curid, curname in links.items():

                locvec = None
                cursim = None

                if curname[key_Param.VALUE] in self.mycontours.keys():
                    locvec = self.mycontours[curname[key_Param.VALUE]]

                if curid in self.mysims.keys():
                    cursim = self.mysims[curid]

                if locvec is not None and cursim is not None:
                    cursim:Wolfresults_2D
                    cursim.linkedvec = locvec.myzones[0].myvectors[0]

    def set_colormap(self):
        """
        Lie les palettes d'un fichier projet et leur liaison potentielle avec les matrices
        """
        pals = self.get_group('palette')
        if pals is None:
            return

        for curid, curname in pals.items():
            filename=''
            if exists(curname[key_Param.VALUE]):
                filename = curname[key_Param.VALUE]
            elif exists(join(self.wdir, curname[key_Param.VALUE])):
                filename=join(self.wdir, curname[key_Param.VALUE])

            if filename!='':
                mypal = wolfpalette(None, '')
                mypal.readfile(filename)
                mypal.automatic = False

                self.mycolormaps[curid] = mypal

        palsarrays = self.get_group('palette-array')
        if palsarrays is not None:
            for curid, curname in palsarrays.items():
                if curname[key_Param.VALUE] in self.set_colormap.keys():
                    if curid in self.mysims.keys():
                        curarray = self.mysims[curid]
                        mypal = self.mycolormaps[curname[key_Param.VALUE]]
                        curarray.mypal = mypal
                        curarray.mypal.automatic = False

    def set_currentview(self, which):
        """
        Change le mode de vue dans une vue possible de "views_2D"
        """
        if which in views_2D:
            with ThreadPoolExecutor() as executor:
                for cursim in self.mysims.values():
                    executor.submit(cursim.set_currentview, which)

    def find_values_inside(self, zonepoly:zone):
        """
        Récupère les valeurs à l'intérieur d'une zone de polygones

        Retour :
         - dictionnaire dont la clé est l'index du polygone dans la zone
         - chaque entrée est un dictionnaire dont la clé 'values' contient une liste pour chaque matrice du projet
         - chaque élément de liste est un tuple contenant toutes les valeurs utiles
        """
        self.poly = zonepoly
        self.poly_values = zonepoly.get_all_values_linked_polygon(self.get_simulations())

    def get_values(self,which_type):

        if self.poly_values is None:
            raise Warning(_('Firstly call get_values_inside with a zone as argument -- Retry !'))

        simslist = list(self.mysims.keys())

        values = {}

        def fillin(pos1,pos2):
            for idx,curpoly in enumerate(self.poly_values.values()):
                curarrays = curpoly['values']

                create=False
                for curarray in curarrays:
                    if len(curarray)>0:
                        create=True
                if create:
                    locdict = values[idx]={}
                    for idarray, curarray in enumerate(curarrays):
                        if len(curarray)>0:
                            vallist=[curval[pos1][pos2] for curval in curarray]
                            locdict[simslist[idarray]] = vallist

        pos02 = [views_2D.WATERDEPTH,
               views_2D.QX,
               views_2D.QY,
               views_2D.UX,
               views_2D.UY,
               views_2D.UNORM,
               views_2D.FROUDE,
               views_2D.WATERLEVEL,
               views_2D.TOPOGRAPHY]

        pos12 = ['i','j','block']

        if which_type in pos02:
            fillin(0, pos02.index(which_type))
            return values
        elif which_type in pos12:
            fillin(1, pos02.index(which_type))
            return values
        else:
            return None

class MultiProjects():
    """Manager of multiple project files"""
    def __init__(self, wdir='') -> None:

        self.projects:dict(str, Wolf2D_Project)={}
        self.wdir=wdir

    def add(self, project:Project, key=str, whichtype=project_type.GENERIC):
        """
        Add project to dict
        """
        if isinstance(project,str):
            if exists(project):
                pass
            elif exists(join(self.wdir,project)):
                project = join(self.wdir,project)

            if whichtype == project_type.GENERIC:
                project = Project(wdir=self.wdir, to_read=True, filename=project)
            elif whichtype == project_type.WOLF2D:
                project = Wolf2D_Project(wdir=self.wdir, to_read=True, filename=project)

        self.projects[key]=project

    def get_project(self, key) -> Project:
        """
        Récupération d'un projet sur base du nom ou d'une position
        """
        if isinstance(key,int):
            if key >=0 and key <len(self.projects):
                return self.projects[self.projects.keys()[key]]

        elif isinstance(key,str):
            if key in self.projects.keys():
                return self.projects[key]

        return None

    def read(self, filepath:str):
        """
        Read from file
        """
        if exists(filepath):
            with open(filepath,'r') as f:
                self.projects = json.load(f)

    def save(self, filepath:str):
        """
        Write to file
        """
        with open(filepath,'w') as f:
            json.dump(self.projects,f)

    def load_simulations(self, epsilon, verbose=False):
        """
        Load all simulations in projects
        """
        for keyp,valp in self.projects.items():
            print(keyp)
            valp.load_simulations(epsilon, verbose)

    def update_simulations(self, epsilon, verbose=False):
        """
        Update all simulations in projects
        """
        for keyp,valp in self.projects.items():
            print(keyp)
            valp.update_simulations(epsilon, verbose)

    def get_simulations_list(self, which_project=None) -> list:
        """
        Return a python list of simulations
        """
        if which_project is None:
            allsims=[]
            for curproj in self.projects.values():
                if isinstance(curproj, Wolf2D_Project):
                    allsims+=curproj.get_simulations()
            return allsims

        elif which_project in self.projects.keys():
            curproj = self.projects[which_project]
            if isinstance(curproj, Wolf2D_Project):
                return curproj.get_simulations()

        return None

    def get_simulations_dict(self, which_project=None) -> dict:
        """
        Return a python dict of simulations
        """
        if which_project is None:
            allsims={}
            for curkey, curproj in self.projects.items():
                if isinstance(curproj, Wolf2D_Project):
                    allsims[curkey] = curproj.get_simulations()
            return allsims

        elif which_project in self.projects.keys():
            curproj = self.projects[which_project]
            if isinstance(curproj, Wolf2D_Project):
                return {which_project: curproj.get_simulations()}

        return None

    def set_currentview(self, which):
        for curproj in self.projects.values():
            if isinstance(curproj, Wolf2D_Project):
                curproj.set_currentview(which)

    def find_values_inside(self, zonepoly:zone, which_project=None):
        """
        Récupère les valeurs à l'intérieur d'une zone de polygones
        """

        if which_project is None:
            for curkey,curproj in self.projects.items():
                if isinstance(curproj, Wolf2D_Project):
                    curproj.find_values_inside(zonepoly)

        elif which_project in self.projects.keys():
            curproj = self.projects[which_project]
            if isinstance(curproj, Wolf2D_Project):
                curproj.find_values_inside(zonepoly)

    def get_values(self, which_type, which_project= None):

        valdict = {}

        if which_project is None:
            for curkey,curproj in self.projects.items():
                if isinstance(curproj, Wolf2D_Project):
                    valdict[curkey] = curproj.get_values(which_type)

        elif which_project in self.projects.keys():
            curproj = self.projects[which_project]
            if isinstance(curproj, Wolf2D_Project):
                valdict[which_project] = curproj.get_values(which_type)

        return valdict