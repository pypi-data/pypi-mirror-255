import re
import sys

try:
    from OpenGL.GL import *
except:
    msg=_('Error importing OpenGL library')
    msg+=_('   Python version : ' + sys.version)
    msg+=_('   Please check your version of opengl32.dll -- conflict may exist between different files present on your desktop')
    raise Exception(msg)

import numpy as np
import shutil
from os.path import exists
import matplotlib.pyplot as plt
import matplotlib.path as mpltPath
import wx
import logging
from enum import Enum

from ..wolf_array import WOLF_ARRAY_FULL_INTEGER, WOLF_ARRAY_FULL_SINGLE, WolfArray, WolfArrayMB, WolfArrayMNAP, \
    header_wolf,WolfArray_Sim2D
from ..PyVertexvectors import *
from ..PyVertex import getIfromRGB
from ..PyTranslate import _
from ..CpGrid import CpGrid
from ..GraphNotebook import PlotPanel
from ..PyParams import Wolf_Param, new_json
from .cst_2D_boundary_conditions import BCType_2D, Direction

PREV_INFILTRATION_NULL = 0  ##< PAS D'INFILTRATION
PREV_INFILTRATION_SIMPLE = 1  ##< INFILTRATION SIMPLE (RÉPARTITION UNIFORME DU DÉBIT INJECTÉ PAR FICHIER .INF)
PREV_INFILTRATION_MOD_MOMENTUM = 2  ##< INFILTRATION AVEC MODIFICATION DE LA QT DE MVT (RÉPARTITION NON UNIFORME DU DÉBIT INJECTÉ PAR FICHIER .INF)
PREV_INFILTRATION_MOD_MOMENTUM_IMPOSED = 4  ##< INFILTRATION AVEC MODIFICATION IMPOSÉE DE LA QT DE MVT (RÉPARTITION NON UNIFORME DU DÉBIT INJECTÉ PAR FICHIER .INF)
PREV_INFILTRATION_VAR_SIMPLE = -1  ##< INFILTRATION VARIABLE (RÉPARTITION UNIFORME DU DÉBIT INJECTÉ CALCULÉ SUR BASE DE L'ÉTAT HYDRODYNAMIQUE INSTANTANÉ)
PREV_INFILTRATION_VAR_MOD_MOMENTUM = -2  ##< INFILTRATION VARIABLE AVEC MOD QT MVT (RÉPARTITION NON UNIFORME DU DÉBIT INJECTÉ CALCULÉ SUR BASE DE L'ÉTAT HYDRODYNAMIQUE INSTANTANÉ)
PREV_INFILTRATION_VAR_LINKED_ZONES = -3  ##< INFILTRATION/EXFILTRATION "INTERNE" VARIABLE (RÉPARTITION UNIFORME DU DÉBIT SUR BASE DE DEUX ZONES D'INFILTRATION)

##
PREV_READ_TXT = 1
PREV_READ_FINE = 2
PREV_READ_MB = 3



class prev_parameters_blocks:
    """ #> Paramètres de calcul propres aux blocs
    @author Pierre Archambeau
     """

    def __init__(self, lines=None) -> None:

        self.computed = True
        self.name = '""'

        self.infiltration = False  ##< infiltration de débit ou non
        self.infiltration_sed = False  ##< infiltration de débit solide ou non
        self.reclineaire = False  # #< reconstruction linéaire ou non
        self.reclinfront = False  # #< reconstruction linéaire ou non sur les bords frontière
        self.optmaillage = False  # #< optimisation du maillage de calcul
        self.incli_axes = False  # #< inclinaison d'axes
        self.turbulence = False  # #< calcul de termes turbulents ou pas
        self.vam5 = False  # #< calcul des équations de moment ou pas
        self.profil_equil = False  # #< calcul d'un profil d'équilibre sédimentaire ou pas
        self.transport_solide = False  # #< equations additionnelles de transport solide ou pas
        self.frot_jacobien = False  # #< evaluation semi-implicite par inversion d'une matrice 3*3 du frottement
        self.carte_de_risque = False  # #< ecriture d'une carte de risque ou pas
        self.carte_de_risque_max = False  # #< ecriture d'une carte de risque étendue ou pas
        self.carte_de_risque_qv = False  # #< ecriture d'une carte de risque vmax et qmax si vitesse
        self.ponts = False  # #< présence ou non de ponts
        self.irv = False  # #< présence ou non d'in coef d'inégale répartition de vitesse distribué
        self.first_resu_bloc = False  # #< premier résu du bloc écrit ou pas (csr)
        self.surf_mod = False  # #< modification des surfaces de frottement ou pas
        self.contour_mob = False  # #< contour mobile dans le bloc ou pas
        self.contour = False  # #< contour fixe dans le bloc ou pas
        self.contour_fixe = False  # #< contour fixe dans le bloc ou pas pour gestion données topo
        self.topo_inst = False  # #< topo variable dans le temps
        self.report_cl_bloc = False  # #< report de conditions limites dans un bloc
        self.effacement_bloc = False  # #< effacement de mailles (bâtiments) dans le bloc ou pas
        self.nforcing = 0  ##< forcing ou pas
        self.nturb = 0  # #< nbre d'inconnues pour le calcul de la turbulence
        self.ncurv = 0  # #< nbre d'inconnues pour le calcul des coor curvilignes
        self.npor = 0  ##< nbre d'inconnues pour le calcul de la porosité
        self.nsed = 0  ##< calcul de bilan sédim dans le bloc (1) ou pas (0)
        self.nsusp = 0  # #< calcul de bilan supension dans le bloc (1) ou pas (0)
        self.ntyprec = 0  ##< =0 si rec constante, 1 si rec linéaire
        self.ntyprecfront = 2  ##< =0 si rec cst, 1 si rec lin non limitée, 2 si rec lin limitée des bords frontière
        self.ntyprecbord = 0  ##< type de reconstruction des bords libres (0 = cst, 1 = lin limitée (non implémenté), 2 = lin non limitée)
        self.nvoislimit = 5  ##< nbre de voisins pour la limitation
        self.nrechzh = 0  ##< =0 si limitation de h, 1 si limitation de h+z
        self.ntraitefront = 1  ##< type de traitement des frontières (1 = rien, 0 = moyenne et décentrement unique)
        self.ntypflux = 1  ##< type de spliting (1 = spliting maison, le reste n'est pas encore implémenté)
        self.nbvar = 4  # #< nbre d'inconnues du calcul
        self.nbequ = 3  # #< nbre d'equations à résoudre
        self.nconflit = 0  ##< gestion des conflits (0), ou juste en centré (1) ou pas (2)
        self.ncouvdecouv = 1  ##< gestion des éléments couvrants-découvrants ou non
        self.ntypetopo = 1  # #< type d'agglomération de la topo (1=moy, 2=max, 3=min)
        self.ninfil = 0  ##< infiltration avec modif eq qté mvt (=2), infiltration simple (=1) ou non (=0)
        self.ntypfil = 0  ##< infiltration modifiée (=2) ou non (=1)
        self.nincli_axes = 0  ##< type d'inclinaison d'axe (0 si pas d'inclinaison)
        self.iegal = 0  # #< =1 si égalisation d'altitude
        self.istat = 0  # #< arrêt stationnaire
        self.nvartop = 0  ##< topo variable ou non
        self.ntype_turb = 0  ##< type de modèle de turbulence (1 = prandtl, ...)
        self.ntype_sedim = 0  ##< type de modèle sédimentaire (1 = charriage, 2 = charriage + suspension)
        self.ntype_charriage = 0  ##< différentes loi de transport par charriage
        self.npos_flux_loi_sedim = 0  ##< loi de capacité de transport par charriage
        self.dim_bil_fvs = 0  ##< dimension de la matrice bilan_fvs
        self.dim_bil_turb = 0  ##< dimension de la matrice bilan_turb
        self.dim_bil_vam5 = 0  ##< dimension de la matrice bilan_vam5
        self.dim_bil_sedim = 0  # #< dimension de la matrice bilan_sedim
        self.dim_bil_suspension = 0  ##< dimension de la matrice bilan_suspension
        self.nbflux = 0  ##< nombre de routines de flux à appeler pour le bloc
        self.nasseche = 0  ##< traitement des assèchements ou pas
        self.limite_erosion = 0  # #< gestion des zones non érodables ou pas
        self.ntypfrot = 0
        # relatif au vdebug(3): type de calcul du frottement
        #< 	=-2 bathurst
        #< 	=-1 chézy
        #< 	=0	manning "classique"
        #< 	=1	manning + bords frottants "brufau - garcia navarro"
        #< 	=2	manning + surfaces frottantes réelles
        #< 	=3	manning + surfaces frottantes réelles + bords frottants "brufau - garcia navarro"
        #< 	=4	manning + bords frottant "hach"
        #< 	=5	manning + surf frottantes réelles + bords frottant "hach"
        #< 	=6	manning + surfaces frottantes réelles correctes en 2d
        #< 	=7	manning + surf frottantes réelles correctes en 2d + bords frottant "hach"
        self.nirv = 0  ##< inégale répartition de vitesse
        self.nqbgravite = 0  ##<  1: active les débits solides dus à la gravité

        self.froudemax = 20.  # #< froude max pour limitation des résultats
        self.frotimpl = 1.  # #< frottement implicite (1) ou pas (0)
        self.frotimpl2 = 0.  # #< coeff du pondération du frotement implicite
        self.hfilref = 0.  # #< hauteur de référence pour infiltration modifiée
        self.alti = 0.  # #< altitude de surface libre à laquelle égaliser
        self.epsstat = 0.  # #< epsilon à vérifier pour l'arrêt stationnaire
        self.vresi = 0.  # #< résidu basé sur la variation moyenne des vitesses dans le domaine de calcul
        self.vresi2 = 0.  # #< résidu basé sur la variation max de hauteur d'eau dans le domaine de calcul
        self.vresi3 = 0.  # #< résidu basé sur la variation moy de hauteur d'eau dans le domaine de calcul
        self.epsstabfond = 0.  # #< epsilon à vérifier pour la stabilisation du fond
        self.vresifond = 0.  # #< résidu basé sur la variation de la topo de fond
        self.epssedim = 0.  ##< epsilon sur h pour recalculer le fond
        self.imult = 0.  # #< indicateur des équations résolues (1 = éq en h et q, 0 = éq en h et u)
        self.imult2 = 0.  # #< indicateur des équations résolues (1 = éq sp, 0 = autres)
        self.un_moins_poros = 0.  # #< )
        self.facteur_cst1 = 0.  #
        self.facteur_cst2 = 0.  #
        self.expos1 = 0.  #
        self.expos2 = 0.  #
        self.s_moins_un = 0.  # #< )
        self.vthetacr = 0.  # #< ) paramètres sédimentaires
        self.d_moyen = 0.  # #< )
        self.d_90 = 0.  # #< )
        self.gammacr = 0.  # #< )
        self.gammanat = 0.  # #< )
        self.param_pente_reduite = 0.  # #< )
        self.tps_consolidation = 0.  # #< )	paramètres fluide frictionnel
        self.r_u0 = 0.  # #< )
        self.vit_infil_x = 0.  # #< )
        self.vit_infil_y = 0.  # #< )
        self.cmu = 0.  # #< )
        self.cnu = 0.  # #< )paramètres du modèle k-e pour la turbulenceread(nl,*)
        self.c1e = 0.  # #< )
        self.c2e = 0.  # #< )
        self.c3e = 0.  # #< )
        self.cd1 = 0.  # #< )
        self.cd2 = 0.  # #< )
        self.clk = 0.  # #< )
        self.cle = 0.  # #< )
        self.sigmak = 0.  # #< )
        self.sigmae = 0.  # #< )
        self.cdk = 0.  # #< paramètre du modèle k pour la turbulence
        self.vminediv = 0.  # #< valeur min de k pour la division
        self.vminkdiv = 0.  # #< valeur min de e pour la division
        self.vnu_eau = 0.  #
        self.inv_vnu_eau = 0.  # #< 1 / viscosité cinématique de l'eau
        self.vmaxvnut = 0.  # #< viscosité turbulente max

        self._def_gen_par = self._get_gen_par()
        self._def_debug_par = self._get_debug_par()

        ##> paramètres de debug - pointeur dans la version précédente
        self.vdebug = []  # #< vecteur des 60 paramètres debug par bloc (stockage en real*8)

        if type(lines) is list:
            ##reconstruction et limitation
            self.ntyprec = int(lines[0])  # =0 si rec constante, 1 si rec linéaire
            self.ntyprecfront = int(lines[1])  # =0 si rec cst, 1 si rec lin non limitée, 2 si rec lin limitée des bords frontière
            self.ntyprecbord = int(lines[2])  # type de reconstruction des bords libres (0 = cst, 1 = lin limitée (non implémenté), 2 = lin non limitée)
            self.nvoislimit = int(lines[3])  # nbre de voisins pour la limitation
            self.nrechzh = int(lines[4])  # =0 si limitation de h, 1 si limitation de h+z
            self.ntraitefront = int(lines[5])  # type de traitement des frontières (1 = rien, 0 = moyenne et décentrement unique)
            self.ntypflux = int(lines[6])  # type de spliting :
            # paramètres de calcul
            self.nbvar = int(lines[7])  # nbre d'inconnues du calcul
            self.nbequ = int(lines[8])  # nbre d'equations à résoudre
            self.froudemax = float(lines[9])  # froude max pour limitation des résultats
            self.nirv = int(lines[10])  # inégale répartition de vitesse
            # options
            self.nconflit = int(lines[11])  # gestion des conflits (0), ou juste en centré (1) ou pas (2)
            self.ncouvdecouv = int(lines[12])  # gestion des éléments couvrants-découvrants ou non
            self.ntypetopo = int(lines[13])  # type d'agglomération de la topo (max, min ou moy)
            self.frotimpl = float(lines[14])  # frottement : 0 = expl, 1 = impl simple,[-1,0[ = impl complet pondéré par ||
            self.ninfil = int(lines[15])  # infiltration avec mod qté mvt (=2), classique (=1) ou non (=0)
            self.hfilref = float(lines[16])  # hauteur de référence pour infiltration modifiée
            self.nincli_axes = int(lines[17])  # type d'inclinaison d'axe : 0 si pas d'inclinaison
            self.iegal = int(lines[18])  # =1 si égalisation d'altitude
            self.alti = float(lines[19])  # altitude de surface libre à laquelle égaliser
            self.istat = int(lines[20])  # arrêt stationnaire (=1 si critère sur v, =2 si sur h)
            self.epsstat = float(lines[21])  # epsilon à vérifier pour l'arrêt stationnaire
            self.nvartop = int(lines[22])  # topo variable ou non

        self.gui_block_param = None

    def _get_debug_par(self) -> list:
        return []

    def _get_gen_par(self) -> list:
        return [self.ntyprec,
                self.ntyprecfront,
                self.ntyprecbord,
                self.nvoislimit,
                self.nrechzh,
                self.ntraitefront,
                self.ntypflux,
                self.nbvar,
                self.nbequ,
                self.froudemax,
                self.nirv,
                self.nconflit,
                self.ncouvdecouv,
                self.ntypetopo,
                self.frotimpl,
                self.ninfil,
                self.hfilref,
                self.nincli_axes,
                self.iegal,
                self.alti,
                self.istat,
                self.epsstat,
                self.nvartop]

    def _set_gen_par(self, values):
        assert len(values)==22, "Bad length of values"
        self.ntyprec = values[0]
        self.ntyprecfront= values[1]
        self.ntyprecbord= values[2]
        self.nvoislimit= values[3]
        self.nrechzh= values[4]
        self.ntraitefront= values[5]
        self.ntypflux= values[6]
        self.nbvar= values[7]
        self.nbequ= values[8]
        self.froudemax= values[9]
        self.nirv= values[10]
        self.nconflit= values[11]
        self.ncouvdecouv= values[12]
        self.ntypetopo= values[13]
        self.frotimpl= values[14]
        self.ninfil= values[15]
        self.hfilref= values[16]
        self.nincli_axes= values[17]
        self.iegal= values[18]
        self.alti= values[19]
        self.istat= values[20]
        self.epsstat= values[21]
        self.nvarto= values[22]

    def write_file(self,f):
        ##reconstruction et limitation
        f.write('{:g}\n'.format(self.ntyprec))
        f.write('{:g}\n'.format(self.ntyprecfront))
        f.write('{:g}\n'.format(self.ntyprecbord))
        f.write('{:g}\n'.format(self.nvoislimit))
        f.write('{:g}\n'.format(self.nrechzh))
        f.write('{:g}\n'.format(self.ntraitefront))
        f.write('{:g}\n'.format(self.ntypflux))
        # paramètres de calcul
        f.write('{:g}\n'.format(self.nbvar))
        f.write('{:g}\n'.format(self.nbequ))
        f.write('{:g}\n'.format(self.froudemax))
        f.write('{:g}\n'.format(self.nirv))
        # options
        f.write('{:g}\n'.format(self.nconflit))
        f.write('{:g}\n'.format(self.ncouvdecouv))
        f.write('{:g}\n'.format(self.ntypetopo))
        # options
        f.write('{:g}\n'.format(self.frotimpl))
        #			 [-1,0[ = impl complet pondéré par ||
        f.write('{:g}\n'.format(self.ninfil))
        f.write('{:g}\n'.format(self.hfilref))
        f.write('{:g}\n'.format(self.nincli_axes))
        f.write('{:g}\n'.format(self.iegal))
        f.write('{:g}\n'.format(self.alti))
        f.write('{:g}\n'.format(self.istat))
        f.write('{:g}\n'.format(self.epsstat))
        f.write('{:g}\n'.format(self.nvartop))

    def write_debug(self,f):
        for curdebug in self.vdebug:
            f.write('{:g}\n'.format(curdebug))

    def set_param_from_gui(self):

        if self.gui_block_param is None:
            self._set_gen_par([self.gui_block_param[(self.groups[i], self.names[i])] for i in range(23)])


    def get_params(self) -> Wolf_Param:
        self.gui_block_param = Wolf_Param(parent=None,
                                 title=self.name + _(' Parameters'),
                                 to_read=False,
                                 withbuttons=True,
                                 DestroyAtClosing=True,
                                 toShow=True)

        self.gui_block_param.callback = self.set_param_from_gui
        self.gui_block_param.callbackdestroy = self.set_param_from_gui

        myparams = self.gui_block_param

        self.groups=[]
        self.names=[]

        active_vals = self._get_gen_par()
        # 1
        self.groups.append(_('Reconstruction'))
        self.names.append(_('Reconstruction method'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[0],
                          type='Integer',
                          comment=_('Variable\'s reconstruction method to the borders (integer) - default = {}'.format(self._get_gen_par[0])),
                          jsonstr=new_json({_('Constant'):0,
                                            _('Linear'):1}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[0]

        # 2
        self.groups.append(_('Reconstruction'))
        self.names.append(_('Interblocks reconstruction method'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[1],
                          type='Integer',
                          comment=_('Variable\'s reconstruction method to the borders at the interblock (integer) - default = {}'.format(self._get_gen_par[1])),
                          jsonstr=new_json({_('Constant'):0,
                                            _('Non limited linear'):1,
                                            _('Limited linear'):2}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[1]

        # 3
        self.groups.append(_('Reconstruction'))
        self.names.append(_('Free border reconstruction method'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[2],
                          type='Integer',
                          comment=_('Variable\'s reconstruction method to the free borders (integer) - default = {}'.format(self._get_gen_par[2])),
                          jsonstr=new_json({_('Constant'):0,
                                            _('Non limited linear'):2}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[2]

        # 4
        self.groups.append(_('Reconstruction'))
        self.names.append(_('Number of neighbors'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[3],
                          type='Integer',
                          comment=_('Number of neighbors to take into account during limitation (integer) - default = {}'.format(self._get_gen_par[3])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[3]

        # 5
        self.groups.append(_('Reconstruction'))
        self.names.append(_('Limit water depth or water level'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[4],
                          type='Integer',
                          comment=_('Limit water depth or water level (integer) - default = {}'.format(self._get_gen_par[4])),
                          jsonstr=new_json({_('Water depth (H)'):0,
                                            _('Water level (H+Z)'):1}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[4]

        # 6
        self.groups.append(_('Reconstruction'))
        self.names.append(_('Frontier'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[5],
                          type='Integer',
                          comment=_('Frontier (integer) - default = {}'.format(self._get_gen_par[5])),
                          jsonstr=new_json({_('None'):1,
                                            _('Mean and unique'):0}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[5]

        # 7
        self.groups.append(_('Splitting'))
        self.names.append(_('Splitting type'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[6],
                          type='Integer',
                          comment=_('Splitting type (integer) - default = {}'.format(self._get_gen_par[6])),
                          jsonstr=new_json({_('HECE'):0}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[6]

        # 8
        self.groups.append(_('Problem'))
        self.names.append(_('Number of unknowns'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[7],
                          type='Integer',
                          comment=_('Number of unknowns (integer) - default = {}'.format(self._get_gen_par[7])),
                          jsonstr=new_json({_('Pure water'):4}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[7]

        # 9
        self.groups.append(_('Problem'))
        self.names.append(_('Number of equations'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[8],
                          type='Integer',
                          comment=_('Number of equations to solve (integer) - default = {}'.format(self._get_gen_par[8])),
                          jsonstr=new_json({_('Pure water'):3}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[8]

        # 10
        self.groups.append(_('Reconstruction'))
        self.names.append(_('Froude maximum'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[9],
                          type='Float',
                          comment=_('Froude maximum (Float) - default = {}'.format(self._get_gen_par[9])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[9]

        # 11
        self.groups.append(_('Problem'))
        self.names.append(_('Unequal speed distribution'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[10],
                          type='Integer',
                          comment=_('Unequal speed distribution (Integer) - default = {}'.format(self._get_gen_par[10])),
                          jsonstr=new_json({_('No'):0}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[10]

        # 12
        self.groups.append(_('Problem'))
        self.names.append(_('Conflict resolution'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[11],
                          type='Integer',
                          comment=_('Conflict resolution (integer) - default = {}'.format(self._get_gen_par[11])),
                          jsonstr=new_json({_('HECE'):0,
                                            _('Centered'):1,
                                            _('Nothing'):2}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[11]

        # 13
        self.groups.append(_('Problem'))
        self.names.append(_('Fixed/Evolutive domain'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[12],
                          type='Integer',
                          comment=_('Fixed/Evolutive domain (integer) - default = {}'.format(self._get_gen_par[12])),
                          jsonstr=new_json({_('Fixed'):0,
                                            _('Evolutive'):1}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[12]

        # 14
        self.groups.append(_('Options'))
        self.names.append(_('Topography'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[13],
                          type='Integer',
                          comment=_('Operation on toppography (integer) - default = {}'.format(self._get_gen_par[13])),
                          jsonstr=new_json({_('Mean'):1,
                                            _('Min'):3,
                                            _('Max'):2}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[13]

        # 15
        self.groups.append(_('Options'))
        self.names.append(_('Friction slope'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[14],
                          type='Float',
                          comment=_('Friction slope (Float) - default = {}'.format(self._get_gen_par[14])),
                          jsonstr=new_json({_('Explicit'):0,
                                            _('Implicit (simple)'):1,
                                            _('Implicit (full)'):-1}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[14]

        # 16
        self.groups.append(_('Options'))
        self.names.append(_('Modified infiltration'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[15],
                          type='Integer',
                          comment=_('Modified infiltration (integer) - default = {}'.format(self._get_gen_par[15])),
                          jsonstr=new_json({_('No'):0,
                                            _('Modified momentum'):2,
                                            _('Classic'):1}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[15]

        # 17
        self.groups.append(_('Options'))
        self.names.append(_('Reference water level for infiltration'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[16],
                          type='Float',
                          comment=_('Reference water level for infiltration (Float) - default = {}'.format(self._get_gen_par[16])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[16]

        # 18
        self.groups.append(_('Options'))
        self.names.append(_('Inclined axes'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[17],
                          type='Integer',
                          comment=_('Inclined axes (integer) - default = {}'.format(self._get_gen_par[17])),
                          jsonstr=new_json({_('No'):0,
                                            _('Yes'):1}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[17]

        # 19
        self.groups.append(_('Initial condition'))
        self.names.append(_('To egalize'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[18],
                          type='Integer',
                          comment=_('To egalize (integer) - default = {}'.format(self._get_gen_par[18])),
                          jsonstr=new_json({_('No'):0,
                                            _('Yes'):1}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[18]

        # 20
        self.groups.append(_('Initial condition'))
        self.names.append(_('Water level to egalize'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[19],
                          type='Float',
                          comment=_('Water level to egalize (Float) - default = {}'.format(self._get_gen_par[19])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[19]

        # 21
        self.groups.append(_('Stopping criteria'))
        self.names.append(_('Stop computation on'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[20],
                          type='Integer',
                          comment=_('Stop computation if (integer) - default = {}'.format(self._get_gen_par[20])),
                          jsonstr=new_json({_('Nothing'):0,
                                            _('Water depth'):2,
                                            _('Speed'):1}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[20]

        # 22
        self.groups.append(_('Stopping criteria'))
        self.names.append(_('Epsilon'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[21],
                          type='Float',
                          comment=_('Epsilon (Float) - default = {}'.format(self._get_gen_par[21])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[21]

        # 23
        self.groups.append(_('Options'))
        self.names.append(_('Variable topography'))
        myparams.addparam(groupname=self.groups[-1],
                          name=self.names[-1],
                          value=self._get_gen_par[22],
                          type='Integer',
                          comment=_('Variable topography (integer) - default = {}'.format(self._get_gen_par[22])),
                          jsonstr=new_json({_('No'):0,
                                            _('Yes'):1}),
                          whichdict='Default')

        myparams[(self.groups[-1],self.names[-1])] = active_vals[22]

        #DEBUG
        self.debug_groups = []
        self.debug_names = []
        active_debug = self._get_debug_par()

        # myparams.addparam(groupname=_('Options'),
        #                   name=_('Friction law'),
        #                   value='0',
        #                   type='Integer',
        #                   comment=_('Friction law (Integer) - default = 0'),
        #                   jsonstr=new_json({_('Manning-Strickler'):0,
        #                                     _('M-S + real surface 2D'):6,
        #                                     _('M-S + real surface 2D + vert. border HECE'):7,
        #                                     _('M-S + vert. border "Brufau-Garcia Navarro'):1,
        #                                     _('M-S + real surface'):2,
        #                                     _('M-S + real surface + vert. border'):3,
        #                                     _('M-S + vert. border HECE'):4,
        #                                     _('M-S + real surface + vert. border HECE'):5,
        #                                     _('Chezy'):-1,
        #                                     _('Bathurt'):-2}),
        #                   whichdict='Default')

        # DEBUG 1
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 2
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 3
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 4
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 5
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 6
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 7
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 8
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 9
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 10
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 11
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 12
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 13
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 14
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 15
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 16
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 17
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 18
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 19
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 20
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 21
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 22
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 23
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 24
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 25
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 26
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 27
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 28
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 29
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 30
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 31
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 32
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 33
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 34
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 35
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 36
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 37
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 38
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 39
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 40
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 41
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 42
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 43
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 44
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 45
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 46
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 47
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 48
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 49
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 50
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 51
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 52
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 53
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 54
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 55
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 56
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 57
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 58
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 59
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]

        # DEBUG 60
        self.debug_groups.append(_('Options'))
        self.debug_names.append(_('Variable topography'))
        idx = len(self.debug_groups)-1

        myparams.addparam(groupname=self.debug_groups[idx],
                          name=self.debug_names[idx],
                          value=self._get_debug_par[idx],
                          type='Integer',
                          comment=_(' (Integer) - default = {}'.format(self._get_debug_par[idx])),
                          jsonstr='',
                          whichdict='Default')

        myparams[(self.debug_groups[idx],self.debug_names[idx])] = active_debug[idx]


class boundary_condition_2D:
    '''
	Type des CL générales, faibles et fortes
	@author Pierre Archambeau
    '''
    vec: vector

    def write_debug(self,f):
        for curdebug in self.vdebug:
            f.write('{}\n'.format(curdebug))

    def __init__(self, i: int, j: int, ntype: int, val: float, direction: int = 1) -> None:
        self.i = i  # indice de colonne dans le plus petit maillage
        self.j = j  # indice de ligne   dans le plus petit maillage
        self.ntype = ntype  # type de cl (h=1,qx=2,qy=3,rien=4,qbx=5,qby=6,hmod=7,fr=8)
        self.val = val  # valeur à imposer
        self.direction = direction

        self.vec = vector(name='bc' + str(i) + '-' + str(j))
        self.vec.myprop.width = 4
        self.vec.myprop.color = getIfromRGB([255, 128, 125])


class prev_boundary_conditions():
    """type pour le stockage des cl générales, faibles et fortes
	@author pierre archambeau
    """

    # The BC's data as they are encoded in the files
    mybc: list[boundary_condition_2D]
    # Vectors representing the geometry of the BC.
    # For weak conditions, these are the borders.
    # For strong conditions, there's no representation
    # as they covers an entire cell (instead of a single border)
    myzones: Zones

    @property
    def nb_bc(self):
        return len(self.mybc)

    def __init__(self, parent) -> None:
        self.parent = parent
        self.reset()

    def reset(self):
        self.mybc = []
        self.myzones = Zones()
        self.myzones.add_zone(zone(name='BC_X'))
        self.myzones.add_zone(zone(name='BC_Y'))

    def fillgrid(self, gridto: CpGrid):

        gridto.SetColLabelValue(0, 'i')
        gridto.SetColLabelValue(1, 'j')
        gridto.SetColLabelValue(2, _('Type'))
        gridto.SetColLabelValue(3, _('Value'))
        gridto.SetColLabelValue(4, _('Self value'))
        gridto.SetColLabelValue(5, _('Old value'))
        gridto.SetColLabelValue(6, _('Water depth'))
        gridto.SetColLabelValue(7, _('Bottom level'))

        k = 0
        for curbc in self.mybc:
            gridto.SetCellValue(k, 0, str(curbc.i))
            gridto.SetCellValue(k, 1, str(curbc.j))
            gridto.SetCellValue(k, 2, str(curbc.ntype))
            gridto.SetCellValue(k, 3, str(curbc.val))
            gridto.SetCellValue(k, 5, str(curbc.val))
            k += 1

    def set_header(self):
        self.dx = self.parent.dxfin
        self.dy = self.parent.dyfin
        self.origx = self.parent.xminfin
        self.origy = self.parent.yminfin
        self.translx = self.parent.translx
        self.transly = self.parent.transly

    def add(self, i, j, ntype, value, orient:str):
        """ Add a new constraint
        i,j : indices
        ntype: type of the constraint
        orient: oritentation, used for drawing
        """
        assert orient in ('x','y','strongbc')

        if type(ntype) == BCType_2D:
            ntype = ntype.value[0]

        if orient == 'x':
            direction = Direction.LEFT.value
        elif orient == 'y':
            direction = Direction.BOTTOM.value
        else:
            direction = 0

        locbc = boundary_condition_2D(i, j, ntype, value, direction=direction)
        x1, y1, x2, y2 = self.get_xy(i, j, orient, True)
        locbc.vec.add_vertex(wolfvertex(x1, y1))
        locbc.vec.add_vertex(wolfvertex(x2, y2))

        self.mybc.append(locbc)
        if orient in 'x':
            self.myzones.myzones[0].add_vector(locbc.vec)
        elif orient == 'y':
            self.myzones.myzones[1].add_vector(locbc.vec)
        elif orient == 'strongbc':
            # Strong boundary conditions are not vectors.
            pass

    def read_file(self, lines: list, orient):
        """#> lecture du fichier de paramètres"""
        for curline in lines:
            tmp = curline.split(',')
            i = int(tmp[0])
            j = int(tmp[1])
            ntype = int(tmp[2])
            value = float(tmp[3])

            if orient == 'x':
                direction = Direction.LEFT.value
            elif orient == 'y':
                direction = Direction.BOTTOM.value
            else:
                direction = 0

            locbc = boundary_condition_2D(i, j, ntype, value, direction=direction)
            self.mybc.append(locbc)

            x1, y1, x2, y2 = self.get_xy(i, j, orient, True)

            locbc.vec.add_vertex(wolfvertex(x1, y1))
            locbc.vec.add_vertex(wolfvertex(x2, y2))

            if orient == 'x':
                self.myzones.myzones[0].add_vector(locbc.vec)
            elif orient == 'y':
                self.myzones.myzones[1].add_vector(locbc.vec)
            elif orient == 'strongbc':
                # Strong boundary conditions are not vectors.
                pass
            else:
                raise Exception(f"Unrecognized orientation {orient}")

    def get_xy(self, i, j, orient, aswolf=False):

        if aswolf:
            i -= 1
            j -= 1

        if orient == 'x':
            x1 = np.float64(i) * self.dx + self.origx + self.translx
            y1 = np.float64(j) * self.dy + self.origy + self.transly
            x2 = x1
            y2 = y1 + self.dy

        elif orient == 'y':
            x1 = np.float64(i) * self.dx + self.origx + self.translx
            y1 = np.float64(j) * self.dy + self.origy + self.transly
            x2 = x1 + self.dx
            y2 = y1

        elif orient == 'strongbc':
            # I put the strong BC in the middle of a cell.
            x1 = np.float64(i) * self.dx + self.origx + self.translx + self.dx/2
            y1 = np.float64(j) * self.dy + self.origy + self.transly + self.dy/2
            x2, y2 = x1, y1

        else:
            raise Exception(f"Unrecognized orientation {orient}")

        return x1, y1, x2, y2


class prev_parameters_simul:
    """paramètres de simulation
    @author pierre archambeau
    """
    my_param_blocks: list[prev_parameters_blocks]
    # FIXME Strong bc are on cell, not on borders, so their type should differ
    # from the one of clfbx/y.
    strong_bc: prev_boundary_conditions
    weak_bc_x: prev_boundary_conditions
    weak_bc_y: prev_boundary_conditions

    # For FORTRAN compatibility
    @property
    def clf(self):
        return self.strong_bc

    # For FORTRAN compatibility
    @property
    def clfbx(self):
        return self.weak_bc_x

    # For FORTRAN compatibility
    @property
    def clfby(self):
        return self.weak_bc_y

    def add_block(self, block: prev_parameters_blocks):
        assert isinstance(block, prev_parameters_blocks)
        self.my_param_blocks.append(block)
        self.nblocks += 1

    def __init__(self, parent=None) -> None:

        self.parent = parent

        ##> infos générales
        self.npas = 0  # #< nbre de pas de simulation à réaliser
        self.dur = 0.  ##< durée souhaitée d'un pas de temps
        self.freq = 0.  ##< fréquence de sortie des résultats
        self.ntypefreq = 0  ##< type de fréquence de sortie des résultats (en temps ou en pas)
        self.ntypewrite = 0  ##< format d'écriture des résultats (1 = texte, 2 = binaire, 3=csr)
        self.ntyperead = 0  ##< format de lecture des données (1 = texte, 2 = binaire, 3 = binaire par blocs)
        self.nun_seul_resu = 0  ##< ecriture d'un seul résu ou pas

        ##> maillage fin
        self.dxfin = 0.  ##< dx du maillage le + fin = maillage sur lequel sont données
        self.dyfin = 0.  ##< dy    les caract de topo, frot,...
        self.nxfin = 0  ##< nbre de noeuds selon x du maillage le + fin
        self.nyfin = 0  ##< nbre de noeuds selon y du maillage le + fin
        self.xminfin = 0.  ##< coordonnées absolues inf droites de la matrice des données
        self.yminfin = 0.  ##<(maillage le plus fin : dxfin et dyfin)

        self.translx = 0.
        self.transly = 0.

        ##> conditions limites
        self.impfgen = 0  ##< nbre de cl fortes

        self.strong_bc = prev_boundary_conditions(self)
        self.weak_bc_x = prev_boundary_conditions(self)
        self.weak_bc_y = prev_boundary_conditions(self)

        ##> stabilité et schéma
        self.ponderation = 0  ##< indicateur du type de schéma r-k
        self.vncsouhaite = 0
        # #> lecture du fichier de paramètresvncsouhaite=0.	#< nbre de courant souhaité
        self.mult_dt = 0.  ##< facteur mult du pas de temps pour vérif a posteriori
        self.noptpas = 0  ##< =1 si optimisation du pas de temps
        self.nmacc = 0  ##< mac cormack ou non

        ##> limiteurs
        self.ntyplimit = 0  ##< 0 si pas de limiteur, 1 si barth jesperson, 2 si venkatakrishnan, 3 si superbee, 4 si van leer, 5 si van albada, 6 si minmod
        self.vkvenka = 0.  ##< k de venkatakrishnan et des limiteurs modifiés

        # #> constantes de calcul
        self.vminhdiv = 0.  ##< hauteur min de division
        self.vminh = 0.  ##< hauteur d'eau min sur 1 maille
        self.vminh2 = 0.  ##< hauteur d'eau min sur 1 maille pour la calculer
        self.nepsrel = 0  ##< epsilon relatif pour la dtm de q nul sur les bords

        # #>paramètres de calcul
        self.nderdec = 0  ##< =2 si dérivées centrées, 1 sinon
        self.npentecentree = 0  ##< pente centrée ou non
        self.vlatitude = 0.  ##< latitude pour le calcul de la force de coriolis

        # #> options
        self.mailonly = 0  ##< 1 si uniquement maillage
        self.nremaillage = 0  ##< =1 si remaillage
        self.ntronc = 0  ##< troncature des variables
        self.nsmooth = 0  ##< =1 si smoothing arithmétique, =2 si smoothing géométrique
        self.nclinst = 0  ##< cl instationnaires ou pas

        # #> blocs
        # FIXME nblocs should be a property equal to len(self.my_param_blocks)
        self.nblocks = 0  ##< nombre de blocs
        self.my_param_blocks: list  ##< paramètres de blocs
        self.my_param_blocks = list()  ##< paramètres de blocs

        # #> paramètres de debug
        self.vdebug= list()

    @property
    def impfbxgen(self):
        return self.weak_bc_x.nb_bc

    @property
    def impfbygen(self):
        return self.weak_bc_y.nb_bc

    def reset_all_boundary_conditions(self):
        """ Resets strong as well as weak boundary conditions.
        """
        self.strong_bc.reset()
        self.impfgen = 0
        self.weak_bc_x.reset()
        self.weak_bc_y.reset()


    def reset_blocks(self):
        self.my_param_blocks.clear()
        self.nblocs = 0

    def setvaluesbc(self, event):

        k = 0
        for curbc in self.weak_bc_x.mybc:
            curbc.val = float(self.bcgridx.GetCellValue(k, 3))
            k += 1

        k = 0
        for curbc in self.weak_bc_y.mybc:
            curbc.val = float(self.bcgridy.GetCellValue(k, 3))
            k += 1

        dlg = wx.MessageDialog(None,
                               _('Do you want to save you .par file? \n A backup of the current file will be available in .par_back if needed.'),
                               style=wx.YES_NO)
        ret = dlg.ShowModal()

        if ret == wx.ID_YES:
            self.write_file()

        dlg.Destroy()

    def getvaluesx(self, event):
        for curmodel in self.mysimuls:
            if curmodel.checked:
                locmodel = curmodel

                curcol = 3
                if locmodel is self.parent:
                    curcol = 4

                k = 0
                for curbc in self.weak_bc_x.mybc:
                    x1, y1, x2, y2 = self.weak_bc_x.get_xy(curbc.i, curbc.j, 'x', True)

                    values1 = locmodel.get_values_from_xy(x1 - self.dxfin / 2., y1)
                    values2 = locmodel.get_values_from_xy(x1 + self.dxfin / 2., y1)

                    if values1[1][0] == '-' and values2[1][0] == '-':
                        self.bcgridx.SetCellValue(k, curcol, _('No neighbor !!'))
                    elif values1[1][0] == '-':
                        self.bcgridx.SetCellValue(k, curcol, str(values2[0][7]))
                        self.bcgridx.SetCellValue(k, 6, str(values2[0][0]))
                        self.bcgridx.SetCellValue(k, 7, str(values2[0][8]))
                    elif values2[1][0] == '-':
                        self.bcgridx.SetCellValue(k, curcol, str(values1[0][7]))
                        self.bcgridx.SetCellValue(k, 6, str(values1[0][0]))
                        self.bcgridx.SetCellValue(k, 7, str(values1[0][8]))
                    else:
                        self.bcgridx.SetCellValue(k, curcol, str((values1[0][7] + values2[0][7]) / 2.))
                        self.bcgridx.SetCellValue(k, 6, str((values1[0][0] + values2[0][0]) / 2.))
                        self.bcgridx.SetCellValue(k, 7, str((values1[0][8] + values2[0][8]) / 2.))
                    k += 1

    def getvaluesy(self, event):
        for curmodel in self.mysimuls:
            if curmodel.checked:
                locmodel = curmodel

                curcol = 3
                if locmodel is self.parent:
                    curcol = 4

                k = 0
                for curbc in self.weak_bc_y.mybc:
                    x1, y1, x2, y2 = self.weak_bc_y.get_xy(curbc.i, curbc.j, 'y', True)

                    values1 = locmodel.get_values_from_xy(x1, y1 - self.dyfin / 2.)
                    values2 = locmodel.get_values_from_xy(x1, y1 + self.dyfin / 2.)

                    if values1[1][0] == '-' and values2[1][0] == '-':
                        self.bcgridy.SetCellValue(k, curcol, _('No neighbor !!'))
                        self.bcgridy.SetCellValue(k, 6, '-')
                        self.bcgridy.SetCellValue(k, 7, '-')
                    elif values1[1][0] == '-':
                        self.bcgridy.SetCellValue(k, curcol, str(values2[0][7]))
                        self.bcgridy.SetCellValue(k, 6, str(values2[0][0]))
                        self.bcgridy.SetCellValue(k, 7, str(values2[0][8]))
                    elif values2[1][0] == '-':
                        self.bcgridy.SetCellValue(k, curcol, str(values1[0][7]))
                        self.bcgridy.SetCellValue(k, 6, str(values1[0][0]))
                        self.bcgridy.SetCellValue(k, 7, str(values1[0][8]))
                    else:
                        self.bcgridy.SetCellValue(k, curcol, str((values1[0][7] + values2[0][7]) / 2.))
                        self.bcgridy.SetCellValue(k, 6, str((values1[0][0] + values2[0][0]) / 2.))
                        self.bcgridy.SetCellValue(k, 7, str((values1[0][8] + values2[0][8]) / 2.))
                    k += 1

    def editing_bc(self, mysimuls):

        self.mysimuls = mysimuls
        self.myeditor = wx.Frame(None, id=wx.ID_ANY, title='BC editor')

        self.edit_bc = wx.Notebook(self.myeditor, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)

        self.bcx = wx.Panel(self.edit_bc, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.bcy = wx.Panel(self.edit_bc, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)

        self.edit_bc.AddPage(self.bcx, _("Boundary conditions X"), True)
        self.edit_bc.AddPage(self.bcy, _("Boundary conditions Y"), True)

        self.bcgridx = CpGrid(self.bcx, wx.ID_ANY, style=wx.WANTS_CHARS | wx.TE_CENTER)
        self.bcgridx.CreateGrid(len(self.weak_bc_x.mybc), 8)

        self.bcgridy = CpGrid(self.bcy, wx.ID_ANY, style=wx.WANTS_CHARS | wx.TE_CENTER)
        self.bcgridy.CreateGrid(len(self.weak_bc_y.mybc), 8)

        gensizer = wx.BoxSizer(wx.VERTICAL)

        sizerbcx = wx.BoxSizer(wx.VERTICAL)
        sizerbcy = wx.BoxSizer(wx.VERTICAL)
        getvalx = wx.Button(self.bcx, id=wx.ID_ANY, label=_('Get Values X'))
        getvaly = wx.Button(self.bcy, id=wx.ID_ANY, label=_('Get Values Y'))

        sizerbcx.Add(getvalx, 1, wx.EXPAND, border=5)
        sizerbcx.Add(self.bcgridx, 1, wx.EXPAND)

        sizerbcy.Add(getvaly, 1, wx.EXPAND, border=5)
        sizerbcy.Add(self.bcgridy, 1, wx.EXPAND)

        getvalx.Bind(wx.EVT_BUTTON, self.getvaluesx)
        getvaly.Bind(wx.EVT_BUTTON, self.getvaluesy)

        setval = wx.Button(self.myeditor, id=wx.ID_ANY, label=_('Set Values'))
        setval.Bind(wx.EVT_BUTTON, self.setvaluesbc)

        self.bcx.SetSizer(sizerbcx)
        self.bcy.SetSizer(sizerbcy)

        gensizer.Add(setval, 1, wx.EXPAND | wx.ALL, border=5)
        gensizer.Add(self.edit_bc, 1, wx.EXPAND | wx.ALL)

        self.bcx.Layout()
        self.bcy.Layout()

        self.weak_bc_x.fillgrid(self.bcgridx)
        self.weak_bc_y.fillgrid(self.bcgridy)

        self.myeditor.SetSizer(gensizer)
        self.myeditor.Layout()
        self.myeditor.Show()

    def read_file(self, fn=''):
        """#> lecture du fichier de paramètres"""

        if fn == '' and self.parent is None:
            return

        # MERGE Not sure about this
        if not exists(fn + '.par'):
            if fn == '':
                fn = self.parent.filenamegen

        if exists(fn + '.trl'):
            with open(fn + '.trl') as f:
                lines = f.read().splitlines()
                self.translx = float(lines[1])
                self.transly = float(lines[2])

        if exists(fn + '.par'):

            with open(fn + '.par') as f:
                lines = f.read().splitlines()

                # Lecture des PARAMETRES GLOBAUX
                # Durée de la simulation et résultats
                self.npas = np.int64(float(lines[0]))  # nbre de pas de simulation à réaliser
                self.dur = float(lines[1])  # durée souhaitée d'un pas de temps
                self.freq = float(lines[2])  # fréquence de sortie des résultats
                self.ntypefreq = int(lines[3])  # type de fréquence de sortie des résultats (en temps ou en pas)
                self.ntypewrite = int(lines[4])  # format d'écriture des résultats (1 = texte, 2 = binaire, 3=csr)
                self.ntyperead = int(lines[5])  # format de lecture des données (1 = texte, 2 = binaire, 3 = binaire par blocs)
                self.nun_seul_resu = int(lines[6])  # ecriture d'un seul résu ou pas
                # maillage fin
                self.dxfin = float(lines[7])  # dx du maillage le + fin = maillage sur lequel sont données
                self.dyfin = float(lines[8])  # dy    les caract de topo, frot,...
                self.nxfin = int(lines[9])  # nbre de noeuds selon x du maillage le + fin
                self.nyfin = int(lines[10])  # y
                self.xminfin = float(lines[11])  # coordonnées absolues inf droites de la matrice des données
                self.yminfin = float(lines[12])  # (maillage le plus fin : dxfin et dyfin)
                # conditions limites
                self.impfgen = int(lines[13])  # nbre de cl fortes
                _impfbxgen = int(lines[14])  # nbre de cl faibles sur les bords x
                _impfbygen = int(lines[15])  # nbre de cl faibles sur les bords y
                # stabilité et schéma
                self.ponderation = float(lines[16])  # indicateur du type de schéma r-k
                self.vncsouhaite = float(lines[17])  # nbre de courant souhaité
                self.mult_dt = float(lines[18])  # facteur mult du pas de temps pour vérif a posteriori
                self.noptpas = int(lines[19])  # =1 si optimisation du pas de temps
                self.nmacc = int(lines[20])  # mac cormack ou non
                # limiteurs
                self.ntyplimit = int(lines[21])  # 0 si pas de limiteur, 1 si barth jesperson, 2 si venkatakrishnan
                # 3 si superbee, 4 si van leer, 5 si van albada, 6 si minmod
                self.vkvenka = float(lines[22])  # k de venkatakrishnan et des limiteurs modifiés
                # constantes de calcul
                self.vminhdiv = float(lines[23])  # hauteur min de division
                self.vminh = float(lines[24])  # hauteur d'eau min sur 1 maille
                self.vminh2 = float(lines[25])  # hauteur d'eau min sur 1 maille pour la calculer
                self.nepsrel = int(lines[26])  # epsilon relatif pour la dtm de q nul sur les bords
                # paramètres de calcul
                self.nderdec = int(lines[27])  # =2 si dérivées centrées, 1 sinon
                self.npentecentree = int(lines[28])  # pente centrée ou non
                self.vlatitude = float(lines[29])  # latitude pour le calcul de la force de coriolis
                # options
                self.mailonly = int(lines[30])  # 1 si uniquement maillage
                self.nremaillage = int(lines[31])  # =1 si remaillage
                self.ntronc = int(lines[32])  # troncature des variables
                self.nsmooth = int(lines[33])  # =1 si smoothing arithmétique, =2 si smoothing géométrique
                self.nclinst = int(lines[34])  # cl instationnaires ou pas
                # nbre de blocs
                self.nblocks = int(lines[35])  # nombre de blocs

                # allocation des espaces mémoire pour le stockage des param de blocs
                self.my_param_blocks:list[prev_parameters_blocks] = []

                # lecture des parametres propres aux blocs
                decal = 36
                for nbblocks in range(self.nblocks):
                    curparambl = prev_parameters_blocks(lines[decal:])
                    self.my_param_blocks.append(curparambl)
                    decal += 23

                # allocation des matrices contenant les cl générales
                self.strong_bc.set_header()
                self.weak_bc_x.set_header()
                self.weak_bc_y.set_header()

                self.strong_bc.read_file(lines[decal:decal + self.impfgen], 'strongbc')
                decal += self.impfgen
                self.weak_bc_x.read_file(lines[decal:decal + _impfbxgen], 'x')
                decal += self.impfbxgen
                self.weak_bc_y.read_file(lines[decal:decal + _impfbygen], 'y')
                decal += self.impfbygen

                # lecture des paramètres debug globaux
                self.vdebug = []
                for i in range(60):
                    self.vdebug.append(float(lines[decal + i]))

                decal += 60

                # lecture des paramètres debug par blocs
                for nbblocks in range(self.nblocks):
                    for i in range(60):
                        self.my_param_blocks[nbblocks].vdebug.append(float(lines[decal + i]))
                    decal += 60

                # lecture index des blocs calculés
                if self.vdebug[0]>0:
                    for idx in range(int(self.vdebug[0])):
                        idx_block = int(lines[decal])-1
                        self.my_param_blocks[idx_block].computed = True
                        decal+=1

                # lecture des noms de chaque bloc
                try:
                    for idx in range(self.nblocks):
                        self.my_param_blocks[idx].name = lines[decal]
                        decal+=1
                except :
                    pass
        else:
            logging.warning(_('.par file not found !'))

    def write_file(self, fn=''):
        """Ecriture du fichier de paramètres"""

        if fn == '' and self.parent is None:
            return

        if fn == '':
            fn = self.parent.filenamegen

        fnback = fn + '.par_back'
        while exists(fnback):
            fnback += '_'

        from  pathlib import Path
        if Path(fn+".par").exists():
            shutil.copyfile(fn + '.par', fnback)

        with open(fn + '.par', 'w') as f:
            # for i in range(14):
            #     f.write(mylines[i] + '\n')

            f.write('{}\n'.format(self.npas))
            f.write('{}\n'.format(self.dur))
            f.write('{}\n'.format(self.freq))
            f.write('{}\n'.format(self.ntypefreq))
            f.write('{}\n'.format(self.ntypewrite))
            f.write('{}\n'.format(self.ntyperead))
            f.write('{}\n'.format(self.nun_seul_resu))
            # maillage fin
            f.write('{}\n'.format(self.dxfin))
            f.write('{}\n'.format(self.dyfin))
            f.write('{}\n'.format(self.nxfin))
            f.write('{}\n'.format(self.nyfin))
            f.write('{}\n'.format(self.xminfin))
            f.write('{}\n'.format(self.yminfin))

            f.write('{}\n'.format(self.impfgen))
            f.write(str(self.impfbxgen) + '\n')
            f.write(str(self.impfbygen) + '\n')
            # stabilité et schéma
            f.write('{}\n'.format(self.ponderation))
            f.write('{}\n'.format(self.vncsouhaite))
            f.write('{}\n'.format(self.mult_dt))
            f.write('{}\n'.format(self.noptpas))
            f.write('{}\n'.format(self.nmacc))
            # limiteurs
            f.write('{}\n'.format(self.ntyplimit))
            # 3 si superbee, 4 si van leer, 5 si van albada, 6 si minmod
            f.write('{}\n'.format(self.vkvenka))
            # constantes de calcul
            f.write('{}\n'.format(self.vminhdiv))
            f.write('{}\n'.format(self.vminh))
            f.write('{}\n'.format(self.vminh2))
            f.write('{}\n'.format(self.nepsrel))
            # paramètres de calcul
            f.write('{}\n'.format(self.nderdec))
            f.write('{}\n'.format(self.npentecentree))
            f.write('{}\n'.format(self.vlatitude))
            # options
            f.write('{}\n'.format(self.mailonly))
            f.write('{}\n'.format(self.nremaillage))
            f.write('{}\n'.format(self.ntronc))
            f.write('{}\n'.format(self.nsmooth))
            f.write('{}\n'.format(self.nclinst))
            # nbre de blocs
            f.write('{}\n'.format(self.nblocks))


            # for i in range(16, 36):
            #     f.write(mylines[i] + '\n')

            # for i in range(36, 36 + self.nblocs * 23):
            #     f.write(mylines[i] + '\n')

            for curbloc in self.my_param_blocks:
                curbloc.write_file(f)

            for i in range(len(self.weak_bc_x.mybc)):
                curbc = self.weak_bc_x.mybc[i]
                f.write('{i},{j},{type},{val}\n'.format(i=str(curbc.i), j=str(curbc.j), type=str(curbc.ntype),
                                                        val=str(curbc.val)))
            for i in range(len(self.weak_bc_y.mybc)):
                curbc = self.weak_bc_y.mybc[i]
                f.write('{i},{j},{type},{val}\n'.format(i=str(curbc.i), j=str(curbc.j), type=str(curbc.ntype),
                                                        val=str(curbc.val)))

            # for i in range(36 + self.nblocs * 23 + oldimpfx + oldimpfy, len(mylines)):
            #     f.write(mylines[i] + '\n')
            #
            # for nbblocks in range(self.nblocs):
            #     for i in range(60):
            #         self.my_param_blocks[nbblocks].vdebug.append(float(lines[decal + i]))
            #     decal += 60

            nb=0
            for idx in range(self.nblocks):
                if self.my_param_blocks[idx].computed:
                    nb+=1
            self.vdebug[0]=nb

            # paramètres debug globaux
            for curdebug in self.vdebug:
                f.write('{:g}\n'.format(curdebug))

            # paramètres debug par blocs
            for curbloc in self.my_param_blocks:
                curbloc.write_debug(f)

            # écriture des blocs à calculer
            for idx in range(self.nblocks):
                if self.my_param_blocks[idx].computed:
                    f.write('{}\n'.format(idx+1))

            # écriture des noms de chaque bloc
            for idx in range(self.nblocks):
                if self.my_param_blocks[idx].name[0]=='"':
                    f.write(self.my_param_blocks[idx].name+'\n')
                else:
                    f.write('"'+self.my_param_blocks[idx].name+'"\n')


    def add_weak_bc_x(self,
                      i: int,
                      j: int,
                      ntype: BCType_2D,
                      value: float):
        """
        Add a boundary condition  on a left vertical border of cell.
        i,j: coordinate of the cell where the left border must be set
             as a boundary. i,j are 1-based (grid coordinates.)
        """
        # FIXME float may not be correct, it should be `np.float32` to match
        # wolfarray's accuracy
        # FIXME Why do we accept "strongbc", isn't clfbx weak conditions ?
        # FIXME We should check that the BC is put at the border of
        # the computation domain, that may help the user to set its coordinates
        # right.
        assert i >= 1 and i <= self.nxfin, f"1 <= i:{i} <= {self.nxfin+1}"
        assert j >= 1 and j <= self.nyfin, f"1 <= j:{j} <= {self.nyfin+1}"
        self.weak_bc_x.add(i,j,ntype,value,orient="x")

    def add_weak_bc_y(self,
                      i: int,
                      j: int,
                      ntype: BCType_2D,
                      value: float):
        """
        Add a boundary condition  on a bottom horizontal border of cell.
        i,j: coordinate of the cell where the left border must be set
             as a boundary. i,j are 1-based (grid coordinates.)
        """
        # FIXME float may not be correct, it should be `np.float32` to match
        # wolfarray's accuracy
        # FIXME Why do we accept "strongbc", isn't clfbx weak conditions ?
        # FIXME We should check that the BC is put at the border of
        # the computation domain, that may help the user to set its coordinates
        # right.
        assert i >= 1 and i <= self.nxfin, f"1 <= i:{i} <= {self.nxfin+1}"
        assert j >= 1 and j <= self.nyfin, f"1 <= j:{j} <= {self.nyfin+1}"
        self.weak_bc_y.add(i,j,ntype,value,orient='y')

    def to_yaml(self):
        global_params =  f"""\
dxfin: {self.dxfin} # dx du maillage le + fin = maillage sur lequel sont données
dxfin: {self.dyfin} # dy    les caract de topo, frot,...
npas: {self.npas} # nbre de pas de simulation à réaliser
dur: {self.dur} # durée souhaitée d'un pas de temps
noptpas: {self.noptpas}  # =1 si optimisation du pas de temps
ntypefreq: {self.ntypefreq} # type de fréquence de sortie des résultats (en temps ou en pas)
freq: {self.freq} # fréquence de sortie des résultats
ntypewrite: {self.ntypewrite} # format d'écriture des résultats (1 = texte, 2 = binaire, 3=csr)
ntyperead: {self.ntyperead} # format de lecture des données (1 = texte, 2 = binaire, 3 = binaire par blocs)
nun_seul_resu: {self.nun_seul_resu} # ecriture d'un seul résu ou pas
nblocs: {self.nblocs} # nombre de blocs
impfbxgen: {self.impfbxgen} # nbre de cl faibles sur les bords x
impfbygen: {self.impfbygen} # nbre de cl faibles sur les bords y
ponderation: {self.ponderation} # indicateur du type de schéma r-k
nxfin: {self.nxfin} #
nyfin: {self.nyfin} #
xminfin: {self.xminfin} # coordonnées absolues inf droites de la matrice des données
yminfin: {self.yminfin} # ??? AKA origx/origy
translx: {self.translx} # ??? To Lamberts coordinates
transly: {self.transly}
# conditions limites
impfgen: {self.impfgen} # nbre de cl fortes
impfbxgen: {self.impfbxgen} # nbre de cl faibles sur les bords x
impfbygen: {self.impfbygen} # nbre de cl faibles sur les bords y
# stabilité et schéma
vncsouhaite: {self.vncsouhaite} # nbre de courant souhaité
mult_dt: {self.mult_dt}  # facteur mult du pas de temps pour vérif a posteriori
nmacc: {self.nmacc} # mac cormack ou non
# limiteurs
ntyplimit: {self.ntyplimit} # 0 si pas de limiteur, 1 si barth jesperson, 2 si venkatakrishnan
# 3 si superbee, 4 si van leer, 5 si van albada, 6 si minmod
vkvenka: {self.vkvenka} # k de venkatakrishnan et des limiteurs modifiés
# constantes de calcul
vminhdiv: {self.vminhdiv} # hauteur min de division
vminh: {self.vminh} # hauteur d'eau min sur 1 maille
vminh2: {self.vminh2} # hauteur d'eau min sur 1 maille pour la calculer
nepsrel: {self.nepsrel} # epsilon relatif pour la dtm de q nul sur les bords
# paramètres de calcul
nderdec: {self.nderdec} # =2 si dérivées centrées, 1 sinon
npentecentree: {self.npentecentree} # pente centrée ou non
vlatitude: {self.vlatitude} # latitude pour le calcul de la force de coriolis
# options
mailonly: {self.mailonly} # 1 si uniquement maillage
nremaillage: {self.nremaillage} # =1 si remaillage
ntronc: {self.ntronc} # troncature des variables
nsmooth: {self.nsmooth} # =1 si smoothing arithmétique, =2 si smoothing géométrique
nclinst: {self.nclinst} # cl instationnaires ou pas
"""

        bloc_params=[]
        for nbblocs in range(self.nblocs):
            p = self.my_param_blocks[nbblocs]
            bloc_params.append("blocks_params:")
            bloc_params.append(f"   - nconflit: {p.nconflit} ##< gestion des conflits (0), ou juste en centré (1) ou pas (2)")
            bloc_params.append(f"     ntraitefront: {p.ntraitefront} ##< type de traitement des frontières (1 = rien, 0 = moyenne et décentrement unique)")

        return global_params + "\n".join(bloc_params)



class prev_infiltration():
    """Infiltration
    Gère à la fois le fichier '.fil' (quantités au cours du temps) et '.inf' (matrice)
    @author Pierre Archambeau
    """
    my_Q: np.ndarray  # #< débits injectés par zone

    def __init__(self, parent=None, fn='') -> None:

        self.parent = parent

        if self.parent is not None:
            self.fn = self.parent.filenamegen
        elif fn != '':
            self.fn = fn
        else:
            raise Exception(_('Bad initialisation of "prev_infiltration" object in wolf2dprev.py -- check your code'))

        self.nb_zones = 0  ##< nombre de zones mentionnées dans .fil
        self.nb_steps = 0  ##< nombre de pas de temps dans .fin

        self.myarray = WolfArray_Sim2D()  ##< matrice d'infiltration (en entiers)

    def read_file(self):
        """lecture du fichier"""
        # !Identification du débit total infiltré de la simulation
        with open(self.fn + '.fil', 'r') as f:
            lines = f.read().splitlines()

        """
        line 1: nb_zonesc
        line 2: start time 1, zone1 value , zone2 value, zone3 value,...
        line 3: start time 2, zone1 value , zone2 value, zone3 value,...
        """
        self.nb_zones = int(lines[0])
        self.nb_steps = len(lines) - 1

        if self.nb_steps > 0:

            if ',' in lines[1]:
                sep = ','
            elif '\t' in lines[1]:
                sep = '\t'
            elif ';' in lines[1]:
                sep = ';'
            else:
                logging.error(_("Values in the '.fil' file are not separated by comma, semi-comma or tabulation -- Check your file -- Continuing with zero values"))
                self.my_Q = np.zerons((self.nb_steps, self.nb_zones))
                return

            locarray = [[float(val) for val in lines[i].strip().split(sep)[:self.nb_zones + 1]] for i in
                        range(1, len(lines))]
            self.my_Q = np.asarray(locarray)

    def read_array(self):
        """lecture de la matrice d'infiltration"""

        if self.parent is None:
            logging.warning(_('No defined parent --> nothing to read !'))
            return

        self.myarray.set_header(self.parent.get_header())
        self.myarray.filename = self.fn + '.inf'
        self.myarray.wolftype = WOLF_ARRAY_FULL_INTEGER
        self.myarray.read_data()

        self.myarray.array.mask = np.logical_not(self.parent.mynap)
        self.myarray.array.data[self.myarray.array.mask] = -1

        self.myarray.nbnotnull = self.myarray.array.count()
        self.myarray.nullvalue = -1.

        self.myarray.mypal.colormin = np.array([.8, .8, .8])
        self.myarray.mypal.set_bounds()

        self.myarray.updatepalette(0)
        self.myarray.loaded = True

        pass

    def zones_values_at_time(self, t):
        for i in range(self.nb_steps-1):
            if self.my_Q[i,0] <= t < self.my_Q[i+1,0]:
                return self.my_Q[i,1:]

    def plot_plt(self, figax=None, show=True):

        if figax is None:
            fig, ax = plt.subplots(1, 1)
        else:
            fig,ax = figax

        sequence, nb_zones = self.my_Q.shape
        for zone in range(1,nb_zones):
            ax.plot(self.my_Q[:, 0], self.my_Q[:, zone], label=f'Infil {zone}')

        ax.legend()

        if show:
            fig.show()

class prev_suxsuy():

    """
    Enumération des bords potentiellement conditions limites selon X et Y

    Dans WOLF, un bord X est un segment géométrique orienté selon Y --> le débit normal au bord est orienté selon X
    Dans WOLF, un bord Y est un segment géométrique orienté selon X --> le débit normal au bord est orienté selon Y

    La logique d'appellation est donc "hydraulique"

    @remark Utile pour l'interface VB6/Python pour l'affichage

    """
    myborders: Zones
    mysux: zone
    mysuy: zone

    def __init__(self, parent) -> None:

        self.parent = parent
        self.filenamesux = self.parent.filenamegen + '.sux'
        self.filenamesuy = self.parent.filenamegen + '.suy'

        self.myborders = Zones()
        self.mysux = zone(name='sux')
        self.mysuy = zone(name='sux')

        self.myborders.add_zone(self.mysux)
        self.myborders.add_zone(self.mysuy)

    def read_file(self):

        with open(self.filenamesux, 'r') as f:
            linesX = f.read().splitlines()
        with open(self.filenamesuy, 'r') as f:
            linesY = f.read().splitlines()

        linesX = [np.float64(curline.split(',')) for curline in linesX]
        linesY = [np.float64(curline.split(',')) for curline in linesY]

        myparams: prev_parameters_simul
        myparams = self.parent.myparam

        dx = myparams.dxfin
        dy = myparams.dyfin
        ox = myparams.xminfin
        oy = myparams.yminfin
        tx = myparams.translx
        ty = myparams.transly

        k = 1
        for curline in linesX:
            x1 = (curline[0] - 1.) * dx + tx + ox
            y1 = (curline[1] - 1.) * dy + ty + oy
            x2 = x1
            y2 = y1 + dy

            vert1 = wolfvertex(x1, y1)
            vert2 = wolfvertex(x2, y2)

            curborder = vector(name='b' + str(k))

            self.mysux.add_vector(curborder)
            curborder.add_vertex([vert1, vert2])

            k += 1

        k = 1
        for curline in linesY:
            x1 = (curline[0] - 1.) * dx + tx + ox
            y1 = (curline[1] - 1.) * dy + ty + oy
            x2 = x1 + dx
            y2 = y1

            vert1 = wolfvertex(x1, y1)
            vert2 = wolfvertex(x2, y2)

            curborder = vector(name='b' + str(k))

            self.mysuy.add_vector(curborder)
            curborder.add_vertex([vert1, vert2])

            k += 1

        self.myborders.find_minmax(True)


class bloc_file():
    """
    Objet permettant la lecture et la manipulation d'un fichier .BLOC

    ***

    Objectif :
     - fournir l'information nécessaire au code Fortran pour mailler le domaine en MB
     - contient des informations géométriques
        - domaine de calcul
        - contour de bloc
     - contient des informations de résolution de maillage
        - tailles de maille souhaitées selon X et Y pour chaque bloc

    ***

    Contenu du fichier :
     - nombre de blocs, nombre maximum de vertices contenu dans les polygones présents (soit contour extérieur, soit contour de bloc)
     - nombre de vertices à lire pour le contour général (une valeur négative indique que 3 colonnes sont à lire)
        - liste de vertices du contour général (sur 2 -- X,Y -- ou 3 colonnes -- X,Y, flag -- la 3ème colonne ne devrait contenir que 0 ou 1 -- 1==segment à ignorer dans les calcul d'intersection du mailleur)

            @remark En pratique, le "flag" sera stocké dans la propriété "z" du vertex --> sans doute pas optimal pour la compréhension --> à modifier ??

     - informations pour chaque bloc
        - nombre de vertices du polygone de contour
        - liste de vertices (2 colonnes -- X et Y)
        - extension du bloc calé sur la grille magnétique et étendu afin de permettre le stockage des relations de voisinage (2 lignes avec 2 valeurs par ligne)
            - xmin, xmax
            - ymin, ymax

            @remark L'extension, sur tout le pourtour, vaut 2*dx_bloc+dx_max_bloc selon X et 2*dy_bloc+dy_max_bloc selon Y
            @remark Pour une taille de maille uniforme on ajoute donc l'équivalent de 6 mailles selon chaque direction (3 avant et 3 après)

     - résolution pour chaque bloc ("nb_blocs" lignes)
        - dx, dy

    ***

    Remarques :
        - nb_blocs n'est pas un invariant. Il faut donc faire attention lors de la création/manipulation de l'objet --> A fixer?
        - pour les simulations existantes, la taille de la grille magnétique n'est pas une information sauvegardée dans les fichiers mais provient du VB6 au moment de la création de la simulation
          @TODO : coder/rendre une grille magnétique et sans doute définir où stocker l'info pour garantir un archivage correct
        -

    """

    # bloc extents are polygons delimiting the area of each block. These
    # rectangle have the same proportion as the block arrays (but of course
    # are in world coordinates)
    my_blocks: list["bloc_extent"]

    # self.my_vec_blocks.myzones (class: Zones) has two `zone`:
    #  [0] + General Zone
    #         + external border : representing the global contour (an arbitrary polygon)
    #  [1] + Block extents
    #         +-> myvectors: representing the extents (rectangles around the blocks)
    my_vec_blocks: Zones

    def __init__(self, parent: None) -> None:

        self.parent = parent
        self.nb_blocks = -1

        if exists(self.parent.filenamegen + '.bloc'):

            self.filename = self.parent.filenamegen + '.bloc'

            self.nb_blocks = 0  # #< nombre de blocs
            self.max_size_cont = 0  # #< taille maximale des contours
            self.interior = False  # #< gestion des contours intérieurs --> ne tient pas compte des allers-retours vers les contours internes lors des calculs d'intersection

            self.dx_grid = 0.  ##< pas spatial selon X du grid magnétique
            self.dy_grid = 0.  ##< pas spatial selon Y du grid magnétique

            self.dx_max = 0.  ##< plus grande taille de bloc selon X
            self.dy_max = 0.  ##< plus grande taille de bloc selon Y

            self.my_blocks:list[bloc_extent] = []
            self.my_vec_blocks = Zones(parent=parent.get_mapviewer())  # #< vecteur des objets blocs
            self.my_vec_blocks.add_zone(zone(name='General',parent=self.my_vec_blocks))
            self.my_vec_blocks.add_zone(zone(name='Blocks extents',parent=self.my_vec_blocks))
        else:
            # If there's no bloc file then assume we're creating a new one,
            # therefore we give it a name (so it can be saved later).
            self.my_blocks = []
            self.filename = self.parent.filenamegen + '.bloc'
            self.my_vec_blocks = Zones(parent=parent.get_mapviewer())  # #< vecteur des objets blocs
            self.my_vec_blocks.add_zone(zone(name='General',parent=self.my_vec_blocks))
            self.my_vec_blocks.add_zone(zone(name='Blocks extents',parent=self.my_vec_blocks))

    @property
    def general_contour_zone(self) -> zone:
        return self.my_vec_blocks.myzones[0]

    @property
    def blocks_extents_zone(self) -> zone:
        return self.my_vec_blocks.myzones[1]


    def read_file(self):

        if self.filename is None:
            return

        if not exists(self.filename):
            return

        ox = self.parent.myparam.xminfin
        oy = self.parent.myparam.yminfin
        tx = self.parent.myparam.translx
        ty = self.parent.myparam.transly

        trlx = tx
        trly = ty

        general = zone(name='General',parent=self.my_vec_blocks)
        self.my_vec_blocks.add_zone(general)

        external_border = bloc_external_border(is2D=True, name='external border')  ##< vecteur du contour externe - polygone unique entourant la matrice "nap", y compris les zones internes reliées par des segments doublés (aller-retour)
        general.add_vector(external_border)

        myextents = zone(name='Blocks extents',parent=self.my_vec_blocks)
        self.my_vec_blocks.add_zone(myextents)

        # #ouverture du fichier
        with open(self.filename, 'r') as f:
            lines = f.read().splitlines()

        # #lecture du nombre de blocs et de la taille maximale du contour
        tmpline = lines[0].split(',')
        self.nb_blocks = int(tmpline[0])
        self.max_size_cont = int(tmpline[1])

        # #lecture du nombre de points du contour extérieur
        nb = int(lines[1])

        # Si nb est négatif, il existe une troisième colonne qui dit si le segment est utile ou pas
        # (maillage de zones intérieures)
        # ATTENTION:
        #   - cette 3ème valeur est soit 0 ou 1
        #   - 0 = segment à utiliser dans les calculs
        #   - 1 = segment à ignorer
        #   - le segment est défini sur base du point courant et du point précédent
        if nb < 0:
            self.interior = True

        nb = np.abs(nb)

        # lecture des données du contour extérieur
        decal = 2
        if self.interior:
            for i in range(decal, nb + decal):
                tmpline = lines[i].split(',')
                # FIXME no *dx, *dy ??? I think it's i,j : cell coordinates
                x = float(tmpline[0]) + trlx
                y = float(tmpline[1]) + trly
                in_use = float(tmpline[2])
                curvert = wolfvertex(x, y, in_use)
                # Ici le test est sur 0, toute autre valeur est donc acceptée mais en pratique seul 1 doit être utilisé afin de pouvoir être utilisé dans le code Fortran ou le VB6
                # @TODO : Il serait sans doute plus rigoureux de rendre un message d'erreur si autre chose que 0 ou 1 est trouvé
                curvert.in_use = in_use == 0.

                external_border.add_vertex(curvert)
        else:
            for i in range(decal, nb + decal):
                tmpline = lines[i].split(',')
                x = float(tmpline[0]) + trlx
                y = float(tmpline[1]) + trly
                curvert = wolfvertex(x, y)

                external_border.add_vertex(curvert)

        external_border.close_force() # assure que le contour est fermé

        # lecture des données par bloc
        decal = nb + 2
        for i in range(self.nb_blocks):
            curextent = bloc_extent(self, lines[decal:],i+1)
            myextents.add_vector(curextent.external_border)
            curextent.external_border.parentzone = myextents

            self.my_blocks.append(curextent)

            # MERGE I'll leave it for later
            # self.blocks_extents_zone.add_vector(curextent.external_border)
            # curextent.external_border.parentzone = self.blocks_extents_zone

            decal += curextent.nb + 3

        # lecture des tailles de maille pour tous les blocs
        for i in range(self.nb_blocks):
            tmp = lines[decal].split(',')
            self.my_blocks[i].dx = float(tmp[0])
            self.my_blocks[i].dy = float(tmp[1])
            decal += 1

        self.my_vec_blocks.find_minmax(True)
        self._get_max()

    def write_file(self):
        # writing bloc file

        self.update_nbmax()

        ox = self.parent.myparam.xminfin
        oy = self.parent.myparam.yminfin
        tx = self.parent.myparam.translx
        ty = self.parent.myparam.transly

        trlx = tx
        trly = ty

        general:zone
        general = self.my_vec_blocks.myzones[0]
        external_border:bloc_external_border
        external_border = general.myvectors[0]

        # ouverture du fichier
        with open(self.filename, 'w') as f:

            # écriture du nombre de blocs et de la taille maximale du contour
            f.write('{},{}\n'.format(self.nb_blocks,self.max_size_cont))

            # #lecture du nombre de points du contour extérieur
            if self.interior :
                f.write('{}\n'.format(-external_border.nbvertices))
                xyz=external_border.asnparray3d()
                xyz[:,0] -= trlx # Les coordonnées sont stockées en absolu, il faut donc retrancher la translation X
                xyz[:,1] -= trly # Les coordonnées sont stockées en absolu, il faut donc retrancher la translation XY

                np.savetxt(f,xyz,fmt='%f,%f,%u')
            else:
                f.write('{}\n'.format(external_border.nbvertices))
                xy=external_border.asnparray()
                xy[:,0] -= trlx # Les coordonnées sont stockées en absolu, il faut donc retrancher la translation X
                xy[:,1] -= trly # Les coordonnées sont stockées en absolu, il faut donc retrancher la translation Y

                np.savetxt(f,xy,fmt='%f,%f')

            # écriture des données par bloc
            for i in range(self.nb_blocks):
                curbloc:bloc_extent
                curvec:vector

                curbloc = self.my_blocks[i]

                curvec = curbloc.external_border
                curvec.verify_limits()

                xy=curvec.asnparray()
                xy[:,0] -= trlx # Les coordonnées sont stockées en absolu, il faut donc retrancher la translation X
                xy[:,1] -= trly # Les coordonnées sont stockées en absolu, il faut donc retrancher la translation Y

                f.write('{}\n'.format(curvec.nbvertices))
                np.savetxt(f,xy,fmt='%f,%f')
                f.write('{},{}\n'.format(curbloc.xmin,curbloc.xmax))
                f.write('{},{}\n'.format(curbloc.ymin,curbloc.ymax))

            # écriture des tailles de maille pour tous les blocs
            for i in range(self.nb_blocks):
                f.write('{:g},{:g}\n'.format(self.my_blocks[i].dx,self.my_blocks[i].dy))

    def _get_max(self):
        self.dx_max = max([curblock.dx for curblock in self.my_blocks])
        self.dy_max = max([curblock.dx for curblock in self.my_blocks])

    def modify_extent(self):

        self.my_vec_blocks.find_minmax(True)

    def update_nbmax(self):
        # MERGE renamed self.my_vec_blocks.myzones[1] wiht more explicit name.
        nb = [len(cur.myvertices) for cur in self.blocks_extents_zone.myvectors]
        nb += [len(self.general_contour_zone.myvectors[0].myvertices)]
        self.max_size_cont = np.max(nb)

class bloc_external_border(vector):
    """

    Extension d'un vecteur afin de stocker un polygone de contour soit du domaine de calcul, soit d'un bloc

    L'extension est utile pour définir la propriété :
        - mylimits
    et les routines:
        - set_limits
        - verify_limits

    @TODO _external_border n'est peut-être pas idéal pour la bonne compréhension --> FIX?

    """
    def __init__(self, lines: list = ..., is2D=True, name='', parentzone=None) -> None:
        super().__init__(lines, is2D, name, parentzone)


    def set_limits(self):

        # Set self.minx, self.maxx), (self.miny, self.maxy)
        # on basis of the self.myvertices
        self.find_minmax()
        self.mylimits = ((self.xmin, self.xmax), (self.ymin, self.ymax))

    def verify_limits(self):

        self.find_minmax()

        if self.xmin < self.mylimits[0][0] or self.xmax > self.mylimits[0][1] or \
                self.ymin < self.mylimits[1][0] or self.ymax > self.mylimits[1][1]:

            for curv in self.myvertices:
                curv: wolfvertex
                # Force the vertex inside self.mylimits
                curv.limit2bounds(self.mylimits)

COLOURS_BLOCKS=[(0,0,255),(255,0,0),(0,255,0),(255,255,0),(255,0,255),(0,255,255),(0,125,255),(255,125,0),(125,0,255),(25,25,255)]

class bloc_extent:
    parent: bloc_file
    # Contour externe du bloc (en coordonnées réelles, c-à-d non
    # translatée vis-à-vis du bloc général)
    external_border: bloc_external_border

    # Please note that both these values will be read
    # in the block file (not in this class)

    dx: float  ##< taille de discrétisation selon X
    dy: float  ##< taille de discrétisation selon Y

    # In the following, "une fois qu'il a été "accroché" sur le grid
    # magnétique" means that xmin is in fact xmin - (dxmax + 2*dx),
    # xmax is xmax + (dxmax + 2*dx) and the same for ymin and ymax.

    xmin: float  ##< position minimale selon X du contour une fois qu'il a été "accroché" sur le grid magnétique
    xmax: float  ##< position maximale selon X du contour une fois qu'il a été "accroché" sur le grid magnétique
    ymin: float  ##< position minimale selon Y du contour une fois qu'il a été "accroché" sur le grid magnétique
    ymax: float  ##< position maximale selon Y du contour une fois qu'il a été "accroché" sur le grid magnétique
    """

    Classe permettant de contenir:
        - le polygone de définition du bloc
        - les bornes de l'étendue augmentée

    Ici xmin, xmax, ymin, ymax sont à dissocier des propriétés du vecteur contour et ne représentent donc pas les coordonnées min et max des vertices mais bien une zone rectangulaire contenant tout le bloc

    """
    def __init__(self, parent: bloc_file, lines=[],idx=0) -> None:
        self.parent = parent  # #< objetparent

        # parent: bloc_file
        # parent.parent: bloc_file.parent == 2D model
        dx = parent.parent.myparam.dxfin
        dy = parent.parent.myparam.dyfin
        ox = parent.parent.myparam.xminfin
        oy = parent.parent.myparam.yminfin
        tx = parent.parent.myparam.translx
        ty = parent.parent.myparam.transly

        trlx = tx
        trly = ty

        self.xmin = 0.  ##< position minimale selon X du contour une fois qu'il a été "accroché" sur le grid magnétique
        self.xmax = 0.  ##< position maximale selon X du contour une fois qu'il a été "accroché" sur le grid magnétique
        self.ymin = 0.  ##< position minimale selon Y du contour une fois qu'il a été "accroché" sur le grid magnétique
        self.ymax = 0.  ##< position maximale selon Y du contour une fois qu'il a été "accroché" sur le grid magnétique

        # FIXME 0 ??? So it means it's irrelevant => x,y coords
        # instead of i,j ?
        self.dx = 0.  ##< taille de discrétisation selon X
        self.dy = 0.  ##< taille de discrétisation selon Y

        self.external_border = bloc_external_border(
            name='block n° '+str(idx), lines=None)  # #< contour externe du bloc (en coordonnées réelles, c-à-d non translatée vis-à-vis du bloc général)

        self.external_border.myprop.color=getIfromRGB(COLOURS_BLOCKS[idx % 9])

        if not lines:
            # lines is None or [] means we're creating a new bloc_extent from scratch.
            self.nb = 0
        else:

            ##lecture du nombre de points du contour extérieur
            self.nb = int(lines[0])

            ##lecture des données
            for i in range(self.nb):
                tmp = lines[i + 1].split(',')

                x = float(tmp[0]) + trlx
                y = float(tmp[1]) + trly

                curvert = wolfvertex(x, y)
                self.external_border.add_vertex(curvert)

            self.external_border.close_force()  ##on force la fermeture du contour extérieur des blocs
            self.external_border.set_limits() # on retient les limites en cas de modifications

            ##emprise du bloc en accord avec le grid magnétique et l'extension de surface utile pour les relations de voisinage entre blocs
            tmp = lines[self.nb + 1].split(',')
            self.xmin = float(tmp[0])
            self.xmax = float(tmp[1])
            tmp = lines[self.nb + 2].split(',')
            self.ymin = float(tmp[0])
            self.ymax = float(tmp[1])


class xy_file():
    """
    Contour du domaine

    Les infos de cette classe sont redondantes avec le contour contenu dans le fichier .bloc
    Dans l'interface VB6, il est cependant généré avant le fichier .bloc

    @remark Le fichier n'est pas utilisé par le code de calcul Fortran --> principalement pré-traitement/visualisation

    """
    myzones: Zones

    def __init__(self, simparent=None):

        self.parent = simparent

        self.myzones = Zones(parent=self.parent)

        myzone = zone(name='contour', parent=self.myzones)
        myvect = vector(name='xy', parentzone=myzone)

        self.myzones.add_zone(myzone)
        myzone.add_vector(myvect)

        # MERGE In some cases there's no xy file
        if exists(self.parent.filenamegen + '.xy'):
            with open(self.parent.filenamegen + '.xy', 'r') as f:
                lines = f.read().splitlines()

            nb = int(lines[0])

            # Choose the right split char
            splitchar = ' '
            if lines[1].find(',') > 0:
                splitchar = ','

            for i in range(nb):
                tmp = re.sub('\\s+', ' ', lines[i + 1].strip()).split(splitchar)
                x = float(tmp[0])
                y = float(tmp[1])

                curvert = wolfvertex(x + self.parent.myparam.translx, y + self.parent.myparam.transly)
                myvect.add_vertex(curvert)

            self.myzones.find_minmax(True)
