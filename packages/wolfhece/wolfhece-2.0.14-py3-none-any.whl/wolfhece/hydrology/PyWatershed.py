import os
from scipy.interpolate import interpolate
from scipy.spatial import KDTree
from matplotlib import figure as mplfig
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import logging
from tqdm import tqdm

from ..PyTranslate import _
from ..PyVertex import wolfvertex, cloud_vertices
from ..wolf_array import *
from ..PyCrosssections import crosssections as CrossSections
from ..GraphNotebook import PlotNotebook
from .read import *

LISTDEM=['dem_before_corr','dem_after_corr','dem_10m','dem_20m','crosssection']
#LISTDEM=['dem_after_corr']

class Node_Watershed:
    """Noeud du modèle hydrologique maillé"""
    i:int   #indice i dans la matrice
    j:int   #indice j dans la matrice

    x:float # coordonnée X
    y:float # coordonnée Y

    index:int  # Numérotation de la maille dans la liste de l'objet Watershed qui l'a initialisé

    dem:dict[str,float] # dictionnaire des valeurs d'altitudes
    demdelta:float      # correction apportée dans la phase de prépro

    crosssections:list  # sections en travers sontenues dans la maille

    time:float      # temps de propagation - cf Drainage_basin.time
    slope:float     # pente calculée ne prépro
    sloped8:float   # pente selon les 8 voisins

    slopecorr:dict  # pente corrigée
    demcorr:dict    # dictionnaire d'alrtitude corrigées

    river:bool      # maille rivière => True
    reach:int       # index du bief
    sub:int         # inde du sous-bassin
    forced:bool     # maille d'échange forcé
    uparea:float    # surface drainée - cf Drainage_basin.cnv

    strahler:int    # indice de Strahler - cf "create_index"
    reachlevel:int  # Niveau du bief - cf "create_index"

    cums:float      # longueur curviligne cumulée **depuis l'aval** -- cf "incr_curvi"
    incrs:float     # incrément de longueur curvi - dx ou sqrt(2)*dx si voisin en crois ou en diagonale

    down:"Node_Watershed"           # pointeur vers le noeud aval
    up:list["Node_Watershed"]       # pointeurs vers le(s) noeud(s) amont
    upriver:list["Node_Watershed"]  # pointeurs vers le(s) noeud(s) **rivière** amont

    flatindex:int = -1  # index de la zone de plat

    def incr_curvi(self):
        """Incrémentation de la longueur curviligne"""

        if self.down is None:
            self.cums=0.
        else:
            self.cums = self.down.cums+self.incrs

        for curup in self.up:
            curup.incr_curvi()

    def mean_slope_up(self, threshold:float)-> float:
        """Pente moyenne sur depuis les mailles amont"""
        curnode: Node_Watershed
        meanslope=0.
        nbmean=0
        for curnode in self.up:
            if curnode.slope>threshold:
                nbmean+=1.
                meanslope+=curnode.slope
        if nbmean>0:
            meanslope=meanslope/nbmean

        return meanslope

    def slope_down(self, threshold:float)->float:
        """
        Recherche d'une pente supérieure à un seuil
        Parcours vers l'aval
        """
        slopedown=0.
        curnode=self
        while curnode.slope < threshold:
            if curnode.down is None:
                break
            curnode=curnode.down

        slopedown = curnode.slope
        return slopedown

    def slope_upriver(self,threshold:float)->float:
        """
        Recherche d'une pente supérieure à un seuil
        Parcours vers l'amont uniquement selon les rivières
        """
        slopeup=0.
        if self.slope<threshold:
            if len(self.upriver)>0:
                slopeup=self.upriver[0].slope_upriver(threshold)
            else:
                slopeup=-1.
        else:
            slopeup = self.slope

        return slopeup

    def set_strahler(self, strahler:int):
        """

        """
        self.strahler = strahler


class RiverSystem:
    """
    Classe du réseau de rivières d'un modèle hydrologique WOLF
    """
    nbreaches:int   # nombre de biefs

    #  reaches
    #  |__['reaches']
    #  |  |__[idx]
    #  |     |__['upstream']
    #  |     |__['baselist']
    #  |__['indexed']
    #  |__['strahler']

    reaches:dict    # dictionnaire des biefs

    kdtree:KDTree   # structure de recherche de voisinage

    upmin:dict      # cf slope_correctionmin
    upmax:dict      # cf slope_correctionmax

    parent:"Watershed"  # objet Watershed parent
    upstreams:dict      # dictionnaire des noeuds en amont

    maxlevels:int       # nombre total de niveaux
    maxstrahler:int     # indice de Strahler max

    tslopemin:float =None   # seuil de pente minimale
    tslopemax:float =None   # seuil de pente maximale

    plotter:PlotNotebook = None # gestionnaire de graphiques
    savedir:str         # répertoire de sauvegarde

    def __init__(self,
                 rivers:list[Node_Watershed],
                 parent:"Watershed",
                 thslopemin:float,
                 thslopemax:float,
                 savedir:str='',
                 computecorr:bool=False,
                 *args,
                 **kwargs):

        self.savedir = savedir
        self.parent  = parent

        self.all_nodes = rivers

        self.init_kdtree(self.all_nodes)

        self.nbreaches = max([x.reach for x in rivers])
        self.reaches   = {}
        self.reaches['reaches'] = {}

        self.upstreams = {}
        self.upstreams['list'] = []

        for curreach in range(1,self.nbreaches+1):
            # attention numérotation 1-based
            listreach, curup = parent.find_rivers(whichreach=curreach)

            if len(curup.upriver) == 0:
                # on est en tête de réseau
                self.upstreams['list'].append(curup)

            self.reaches['reaches'][curreach]={}
            curdict=self.reaches['reaches'][curreach]
            curdict['upstream']=curup
            curdict['baselist']=listreach

        self.create_index() # index et Strahler

        if computecorr:
            self.tslopemin=thslopemin
            self.tslopemax=thslopemax
            self.slope_correctionmin()
            self.slope_correctionmax()

        return super().__init__(*args, **kwargs)

    def init_kdtree(self, nodes:list[Node_Watershed]):
        """Create a KDTree structure from coordinates"""
        xy = [[curnode.x, curnode.y]  for curnode in nodes]
        self.kdtree = KDTree(xy)

    def get_nearest_nodes(self, xy:np.ndarray, nb=int) -> tuple[np.ndarray, list[Node_Watershed]]:
        """
        Return the distance and the  nearest Node_Watershed

        :param xy = np.ndarray - shape (n,2)
        :param nb = number of neighbors

        return
        """
        dd, ii = self.kdtree.query(xy, nb)

        return dd, [self.all_nodes[curi] for curi in ii]

    def get_cums(self, whichreach:int=None, whichup:int=None):
        """
        Récupération de la position curvi
        """
        curnode:Node_Watershed
        if whichreach is not None:
            nodeslist=self.reaches['reaches'][whichreach]['baselist']
            x=[curnode.cums for curnode in nodeslist]
        elif whichup is not None:
            x=[]
            curnode=self.upstreams['list'][whichup]
            while curnode is not None:
                x.append(curnode.cums)
                curnode=curnode.down
        else:
            x=[]

        return x

    def get_dem(self, whichdem:str, whichreach:int=None, whichup:int=None):
        """
        Récupération de l'altitude pour une matrice spécifique
        """
        if whichreach is not None:
            nodeslist=self.reaches['reaches'][whichreach]['baselist']
            dem=[curnode.dem[whichdem] for curnode in nodeslist]
        elif whichup is not None:
            curnode:Node_Watershed
            dem=[]
            curnode=self.upstreams['list'][whichup]
            while curnode is not None:
                dem.append(curnode.dem[whichdem])
                curnode=curnode.down
        return dem

    def get_dem_corr(self, whichdem:str, whichreach:int=None, whichup:int=None):
        """
        Récupération de l'altitude corrigée pour une matrice spécifique
        """
        if whichreach is not None:
            nodeslist=self.reaches['reaches'][whichreach]['baselist']
            dem=[curnode.demcorr[whichdem] for curnode in nodeslist]
        elif whichup is not None:
            curnode:Node_Watershed
            dem=[]
            curnode=self.upstreams['list'][whichup]
            while curnode is not None:
                dem.append(curnode.dem[whichdem])
                curnode=curnode.down
        return dem

    def get_slope(self, whichslope:str=None, whichreach:int=None, whichup:int=None):
        """
        Récupération de la pente
        """
        if whichslope is None:
            if whichreach is not None:
                nodeslist=self.reaches['reaches'][whichreach]['baselist']
                slope=[curnode.slope for curnode in nodeslist]
            elif whichup is not None:
                curnode:Node_Watershed
                slope=[]
                curnode=self.upstreams['list'][whichup]
                while curnode is not None:
                    slope.append(curnode.slope)
                    curnode=curnode.down
        else:
            if whichreach is not None:
                nodeslist=self.reaches['reaches'][whichreach]['baselist']
                slope=[curnode.slopecorr[whichslope]['value'] for curnode in nodeslist]
            elif whichup is not None:
                curnode:Node_Watershed
                slope=[]
                curnode=self.upstreams['list'][whichup]
                while curnode is not None:
                    slope.append(curnode.slopecorr[whichslope]['value'])
                    curnode=curnode.down

        return slope

    def create_index(self):
        """
        Incrément d'index depuis l'amont jusque l'exutoire final
        Parcours des mailles rivières depuis tous les amonts et Incrémentation d'une unité
        Résultat :
         - tous les biefs en amont sont à 1
         - Les autres biefs contiennent le nombre de biefs en amont

        Indice de Strahler
        """
        for curup in self.upstreams['list']:
            curnode:Node_Watershed
            curnode=curup
            while not curnode is None:
                curnode.reachlevel +=1
                curnode=curnode.down

        #recherche de l'index max --> à l'exutoire
        self.maxlevels = self.parent.outlet.reachlevel
        self.maxstrahler=0
        self.reaches['indexed']={}
        for i in range(1,self.maxlevels+1):
            self.reaches['indexed'][i]=[]

        #création de listes pour chaque niveau
        for curreach in self.reaches['reaches']:
            curdict=self.reaches['reaches'][curreach]
            listreach=curdict['baselist']
            curlevel=listreach[0].reachlevel
            self.reaches['indexed'][curlevel].append(curreach)

        #création de listes pour chaque amont
        #  on parcourt toutes les mailles depuis chaque amont et on ajoute les index de biefs qui sont différents
        for idx,curup in enumerate(self.upstreams['list']):
            curdict=self.upstreams[idx]={}
            curdict['up']=curup
            curdict['fromuptodown']=[]
            curdict['fromuptodown'].append(curup.reach)
            curnode=curup.down
            while not curnode is None:
                if curnode.reach!=curdict['fromuptodown'][-1]:
                    curdict['fromuptodown'].append(curnode.reach)
                curnode=curnode.down

        #création de l'indice de Strahler
        self.reaches['strahler']={}
        #on commence par ajouter les biefs de 1er niveau qui sont à coup sûr d'indice 1
        self.reaches['strahler'][1]=self.reaches['indexed'][1]
        for curreach in self.reaches['strahler'][1]:
            self.set_strahler_in_nodes(curreach,1)

        #on parcourt les différents niveaux
        for i in range(2,self.maxlevels+1):
            listlevel=self.reaches['indexed'][i]
            for curreach in listlevel:
                curup:Node_Watershed
                curup=self.reaches['reaches'][curreach]['upstream']
                upidx=list(x.strahler for x in curup.upriver)
                sameidx=upidx[0]==upidx[-1]
                maxidx=max(upidx)

                curidx=maxidx
                if sameidx:
                    curidx+=1
                    if not curidx in self.reaches['strahler'].keys():
                         #création de la liste du niveau supérieur
                         self.reaches['strahler'][curidx]=[]
                         self.maxstrahler=curidx

                self.reaches['strahler'][curidx].append(curreach)
                self.set_strahler_in_nodes(curreach,curidx)


        myarray=WolfArray(mold=self.parent.subs_array)
        myarray.reset()
        curnode:Node_Watershed
        for curreach in self.reaches['reaches']:
            curdict=self.reaches['reaches'][curreach]
            listreach=curdict['baselist']
            for curnode in listreach:
                i=curnode.i
                j=curnode.j
                myarray.array[i,j]=curnode.strahler
        myarray.filename = self.parent.dir+'\\Characteristic_maps\\Drainage_basin.strahler'
        myarray.write_all()
        myarray.reset()
        for curreach in self.reaches['reaches']:
            curdict=self.reaches['reaches'][curreach]
            listreach=curdict['baselist']
            for curnode in listreach:
                i=curnode.i
                j=curnode.j
                myarray.array[i,j]=curnode.reachlevel
        myarray.filename = self.parent.dir+'\\Characteristic_maps\\Drainage_basin.reachlevel'
        myarray.write_all()

    def set_strahler_in_nodes(self, whichreach:int, strahler:int):
        """
        Mise à jour de la propriété dans chaque noeud du bief
        """
        listnodes = self.reaches['reaches'][whichreach]['baselist']

        curnode:Node_Watershed
        for curnode in listnodes:
            curnode.set_strahler(strahler)

    def plot_dem(self, which:int=-1):
        """
        Graphiques
        """
        mymarkers=['x','+','1','2','3','4']
        if which==-1:
            fig=self.plotter.add('All Reaches')

            ax=fig.add_ax()

            for curreach in self.reaches['reaches']:
                x=np.array(self.get_cums(whichreach=curreach))
                for idx,curdem in enumerate(LISTDEM):
                    y=np.array(self.get_dem(curdem,whichreach=curreach))

                    xmask=np.ma.masked_where(y==99999.,x)
                    ymask=np.ma.masked_where(y==99999.,y)

                    ax.scatter(xmask,ymask,marker=mymarkers[idx],label=curdem)
            ax.legend()
            fig.canvas.draw()

        elif which==-99:
            size=int(np.ceil(np.sqrt(self.nbreaches)))

            fig=self.plotter.add('reaches')

            for index,curreach in enumerate(self.reaches['reaches']):
                #curax=ax[int(np.floor(index/size)),int(np.mod(index,size))]
                curax=fig.add_ax()

                curdict=self.reaches['reaches'][curreach]
                x=np.array(self.get_cums(whichreach=curreach))

                for idx,curdem in enumerate(LISTDEM):
                    y=np.array(self.get_dem(curdem,whichreach=curreach))

                    xmask=np.ma.masked_where(y==99999.,x)
                    ymask=np.ma.masked_where(y==99999.,y)

                    curax.scatter(xmask,ymask,marker=mymarkers[idx],label=curdem)
            curax.legend()
            fig.canvas.draw()

        elif which==-98:
            size=int(np.ceil(np.sqrt(len(self.upstreams['list']))))

            fig=self.plotter.add('reaches')

            for idxup,curup in enumerate(self.upstreams['list']):
                curax=fig.add_ax()

                x=np.array(self.get_cums(whichup=idxup))

                for idx,curdem in enumerate(LISTDEM):
                    y=np.array(self.get_dem(curdem,whichup=idxup))

                    xmask=np.ma.masked_where(y==99999.,x)
                    ymask=np.ma.masked_where(y==99999.,y)
                    curax.scatter(xmask,ymask,marker=mymarkers[idx],label=curdem)

            curax.legend()
            fig.canvas.draw()

        elif which>-1:
            if which<len(self.upstreams['list']):
                if not self.plotter is None:
                    fig=self.plotter.add('Upstream n°'+str(which))
                else:
                    fig=plt.figure()

                ax=fig.add_ax()

                x=np.array(self.get_cums(whichup=which))
                for idx,curdem in enumerate(LISTDEM):
                    y=np.array(self.get_dem(curdem,whichup=which))

                    xmask=np.ma.masked_where(y==99999.,x)
                    ymask=np.ma.masked_where(y==99999.,y)
                    ax.scatter(xmask,ymask,marker=mymarkers[idx],label=curdem)

            ax.legend()
            fig.canvas.draw()

    def plot_dem_and_corr(self, which:int=-1, whichdem:str='dem_after_corr'):
        """
        Graphiques
        """

        if which<len(self.upstreams['list']):
            if not self.plotter is None:
                fig=self.plotter.add('Upstream n°'+str(which))
            else:
                fig=plt.figure()
                fig.suptitle('Upstream n°'+str(which))

            ax=fig.add_ax()

            x=np.array(self.get_cums(whichup=which))
            y=np.array(self.get_dem(whichdem,whichup=which))

            xcorr=self.upmin[which][whichdem][0]
            ycorr=self.upmin[which][whichdem][1]

            xmask=np.ma.masked_where(y==99999.,x)
            ymask=np.ma.masked_where(y==99999.,y)

            ax.scatter(xmask,ymask,marker='x',label=whichdem)
            ax.scatter(xcorr,ycorr,marker='+',label='selected points')

            ax.legend()
            fig.canvas.draw()

            if not self.savedir=='':
                plt.savefig(self.savedir+'\\Up'+str(which)+'_'+whichdem+'.png')

    def plot_slope(self, which:int=-1):
        """
        Graphiques
        """
        mymarkers=['x','+','1','2','3','4']
        if which==-1:
            fig=self.plotter.add('reaches')
            ax=fig.add_ax()

            for curreach in self.reaches['reaches']:
                x=self.get_cums(whichreach=curreach)
                for idx,curdem in enumerate(LISTDEM):
                    y=self.get_slope(curdem,whichreach=curreach)
                    ax.scatter(x,y,marker=mymarkers[idx],label=curdem)
            fig.canvas.draw()

        elif which==-99:
            size=int(np.ceil(np.sqrt(self.nbreaches)))
            fig=self.plotter.add('reaches')

            for index,curreach in enumerate(self.reaches['reaches']):
                curax=fig.add_ax()

                x=self.get_cums(whichreach=curreach)

                for idx,curdem in enumerate(LISTDEM):
                    y=self.get_slope(curdem,whichreach=curreach)
                    curax.scatter(x,y,marker=mymarkers[idx],label=curdem)
            curax.legend()
            fig.canvas.draw()

        elif which==-98:
            size=int(np.ceil(np.sqrt(len(self.upstreams['list']))))

            fig=self.plotter.add('reaches')

            for idxup,curup in enumerate(self.upstreams['list']):
                curax=fig.add_ax()
                x=self.get_cums(whichup=idxup)

                for idx,curdem in enumerate(LISTDEM):
                    y=self.get_slope(curdem,whichup=idxup)
                    curax.scatter(x,y,marker=mymarkers[idx],label=curdem)
            curax.legend()
            fig.canvas.draw()

    def write_slopes(self):
        """
        Ecriture sur disque
        """
        #Uniquement les pentes rivières
        for curlist in LISTDEM:
            slopes= WolfArray(self.parent.dir+'\\Characteristic_maps\\Drainage_basin.slope')
            slopes.reset()
            for curreach in self.reaches['reaches']:
                curdict=self.reaches['reaches'][curreach]
                listreach=curdict['baselist']

                curnode:Node_Watershed
                ijval = np.asarray([[curnode.i, curnode.j, curnode.slopecorr[curlist]['value']]  for curnode in listreach])
                slopes.array[np.int32(ijval[:,0]),np.int32(ijval[:,1])]=ijval[:,2]

            slopes.filename = self.parent.dir+'\\Characteristic_maps\\Drainage_basin.slope_corr_riv_'+curlist
            slopes.write_all()

    def slope_correctionmin(self):
        """
        Correction pente minimale
        """
        if self.tslopemin is not None:
            logging.info(_('select min - river'))
            self.selectmin()
            logging.info(_('slope correction min - river'))
            self.compute_slopescorr(self.upmin)

    def slope_correctionmax(self):
        """
        Correction pente maximale
        """
        if self.tslopemax is not None:
            logging.info(_('select max - river'))
            self.selectmax()
            logging.info(_('slope correction max - river'))
            self.compute_slopescorr(self.upmax)

    def selectmin(self):
        """
        Sélection des valeurs minimales afin de conserver une topo décroissante vers l'aval --> une pente positive
        """
        self.upmin={}

        #on initialise le dictionnaire de topo min pour chaque amont
        for idx,curup in enumerate(self.upstreams['list']):
            self.upmin[idx]={}

        curnode:Node_Watershed
        for curdem in LISTDEM:
            logging.info(_('Current DEM : {}'.format(curdem)))
            for idx,curup in enumerate(self.upstreams['list']):
                #on part de l'amont
                curnode=curup
                x=[]
                y=[]

                x.append(curnode.cums)

                if curdem=='crosssection':
                    basey=min(curnode.dem[curdem],curnode.dem['dem_after_corr'])
                else:
                    basey=curnode.dem[curdem]

                y.append(basey)
                curnode=curnode.down

                locs= self.parent.resolution
                while not curnode is None:
                    if curdem=='crosssection':
                        yloc=min(curnode.dem[curdem],curnode.dem['dem_after_corr'])
                    else:
                        yloc=curnode.dem[curdem]

                    #on ajoute la maille si la pente est suffisante, sinon cekla créera un trou dans le parcours
                    if (basey-yloc)/locs>self.tslopemin:
                        x.append(curnode.cums)
                        y.append(yloc)
                        basey=yloc
                        locs= self.parent.resolution
                    else:
                        locs+= self.parent.resolution

                    #if curnode.i==232 and curnode.j==226:
                    #    a=1

                    curnode=curnode.down

                #on stocke les vecteurs de coordonnées curvi et d'altitudes pour les zones respectant les critères
                self.upmin[idx][curdem]=[x,y]

    def selectmax(self):
        """
        Sélection des valeurs maximales afin de conserver une topo décroissante vers l'aval --> une pente positive
        """
        # on travaille sur base de la topo corrigée min
        self.upmax={}

        #on initialise le dictionnaire de topo max pour chaque amont
        for idx,curup in enumerate(self.upstreams['list']):
            self.upmax[idx]={}

        ds=self.parent.resolution
        curnode:Node_Watershed
        for curdem in LISTDEM:
            logging.info(_('Current DEM : {}'.format(curdem)))
            for idx,curup in enumerate(self.upstreams['list']):
                curnode=curup
                x=[]
                y=[]

                basey=curnode.demcorr[curdem]['value']

                x.append(curnode.cums)
                y.append(basey)
                curnode=curnode.down

                locs= ds
                while not curnode is None:
                    yloc=curnode.demcorr[curdem]['value']

                    if (basey-yloc)/locs>self.tslopemax:
                        while len(x)>1 and (basey-yloc)/locs>self.tslopemax:
                            x.pop()
                            y.pop()
                            basey=y[-1]
                            locs+=ds

                    if yloc<y[-1]:
                        x.append(curnode.cums)
                        y.append(yloc)
                        basey=yloc
                        locs=ds

                    curnode=curnode.down

                self.upmax[idx][curdem]=[x,y]

    def compute_slopescorr(self, whichdict:dict):
        """
        Calcul des pents corrigées
        """
        curnode:Node_Watershed
        for curdem in LISTDEM:
            logging.info(_('Current DEM : {}'.format(curdem)))
            for idx,curup in enumerate(self.upstreams['list']):
                curdict=whichdict[idx][curdem]
                xmin=curdict[0]
                if len(xmin)>1:
                    ymin=curdict[1]
                    x=self.get_cums(whichup=idx)

                    #on cale une fonction d'interpolation sur la sélection dans lequalle on a oublié les pentes faibles --> à trou
                    f=interpolate.interp1d(xmin,ymin, fill_value='extrapolate')
                    #on interpole sur tous les x --> on remplit les trous
                    y=f(x)
                    #calcul des pentes sur base des noeuds aval
                    slopes=self.compute_slope_down(x,y)

                    #on remplit le dictionnaire de résultat
                    curnode=curup
                    i=0
                    while not curnode is None:
                        #if curnode.i==232 and curnode.j==226:
                        #    a=1
                        curnode.demcorr[curdem]['parts'].append(y[i])
                        curnode.slopecorr[curdem]['parts'].append(slopes[i])
                        i+=1
                        curnode=curnode.down

        #calcul de la moyenne sur base des valeurs partielles
        for curdem in LISTDEM:
            for curreach in self.reaches['reaches']:
                nodeslist=self.reaches['reaches'][curreach]['baselist']
                for curnode in nodeslist:
                    #if curnode.i==232 and curnode.j==226:
                    #    a=1
                    if len(nodeslist)<2:
                        if not self.tslopemin is None:
                            curnode.slopecorr[curdem]['value']=max(self.tslopemin,curnode.slope)
                        else:
                            curnode.slopecorr[curdem]['value']=self.tslopemin=1.e-4

                        if not self.tslopemax is None:
                            curnode.slopecorr[curdem]['value']=min(self.tslopemax,curnode.slope)
                    else:
                        curnode.demcorr[curdem]['value']=np.mean(curnode.demcorr[curdem]['parts'])
                        curnode.slopecorr[curdem]['value']=np.mean(curnode.slopecorr[curdem]['parts'])

                    #on vide les parts
                    curnode.demcorr[curdem]['parts']=[]
                    curnode.slopecorr[curdem]['parts']=[]

    def compute_slope_down(self, x, y):
        """
        Calcul de pente sur base de x et y
        """
        slope=[]
        for i in range(len(x)-1):
            slope.append((y[i+1]-y[i])/(x[i+1]-x[i]))
        slope.append(slope[-1])
        return slope

    def plot_all_in_notebook(self):
        """
        Graphiques
        """
        self.plotter = PlotNotebook()

        for i in range(self.nbreaches):
            self.plot_dem_and_corr(i,whichdem='crosssection')
        self.plot_dem()
        self.plot_slope(-98)
        self.plot_dem(-98)

class RunoffSystem:
    """Classe de l'ensemble des mailles de ruissellement d'un modèle hydrologique WOLF"""
    nodes:list[Node_Watershed]  # liste de noeuds

    parent:"Watershed"
    upstreams:dict

    tslopemin:float
    tslopemax:float

    upmin:dict
    upmax:dict

    def __init__(self,
                 runoff:list[Node_Watershed],
                 parent:"Watershed",
                 thslopemin:float = None,
                 thslopemax:float = None,
                 computecorr:bool=False,
                 *args,
                 **kwargs):

        self.parent  = parent
        self.nodes = runoff
        self.upstreams={}

        #sélection des mailles qui ont une surface unitaire comme surface drainée
        areaup = pow(parent.resolution,2)/1.e6
        self.upstreams['list']=list(filter(lambda x: (x.uparea-areaup)<1.e-6 ,runoff))

        if computecorr:
            self.tslopemin = thslopemin
            self.tslopemax = thslopemax

            self.slope_correctionmin()
            self.slope_correctionmax()

        return super().__init__(*args, **kwargs)

    def get_oneup(self, idx:int) -> Node_Watershed:
        """
        Récupération d'un amont sur base de l'index
        """
        return self.upstreams['list'][idx]

    def get_cums(self,whichup:int=None):

        if not whichup is None:
            curnode:Node_Watershed
            x=[]
            curnode=self.get_oneup(whichup)
            while not curnode.river:
                x.append(curnode.cums)
                curnode=curnode.down
            if len(x)==1:
                x.append(curnode.cums)
        else:
            x=[]

        return x

    def get_dem(self, whichdem:str, whichup:int=None):
        if not whichdem in LISTDEM:
            return

        if not whichup is None:
            curnode:Node_Watershed
            dem=[]
            curnode=self.get_oneup(whichup)
            while not curnode.river:
                dem.append(curnode.dem[whichdem])
                curnode=curnode.down
        return dem

    def get_dem_corr(self, whichdem:str, whichup:int=None):
        if not whichdem in LISTDEM:
            return

        if not whichup is None:
            curnode:Node_Watershed
            dem=[]
            curnode=self.get_oneup(whichup)
            while not curnode.river:
                dem.append(curnode.dem[whichdem])
                curnode=curnode.down
        return dem

    def get_slope(self, whichslope:str=None, whichup:int=None):

        if whichslope is None:
            if not whichup is None:
                curnode:Node_Watershed
                slope=[]
                curnode=self.get_oneup(whichup)
                while not curnode.river:
                    slope.append(curnode.slope)
                    curnode=curnode.down
        else:
            if not whichup is None:
                curnode:Node_Watershed
                slope=[]
                curnode=self.get_oneup(whichup)
                while not curnode.river:
                    slope.append(curnode.slopecorr[whichslope]['value'])
                    curnode=curnode.down

        return slope

    def plot_dem(self, which:int=-1):

        mymarkers=['x','+','1','2','3','4']
        if which>-1:
            if which<len(self.upstreams['list']):
                fig=plt.figure()
                fig.suptitle('Upstream n°'+str(which))

                x=np.array(self.get_cums(whichup=which))
                for idx,curdem in enumerate(LISTDEM):
                    y=np.array(self.get_dem(curdem,whichup=which))

                    xmask=np.ma.masked_where(y==99999.,x)
                    ymask=np.ma.masked_where(y==99999.,y)
                    plt.scatter(xmask,ymask,marker=mymarkers[idx],label=curdem)

            plt.legend()
        plt.show()

    def plot_dem_and_corr(self, which:int=-1, whichdem:str='dem_after_corr'):

        if which<len(self.upstreams['list']):
            fig=plt.figure()
            fig.suptitle('Upstream n°'+str(which))

            x=np.array(self.get_cums(whichup=which))
            y=np.array(self.get_dem(whichdem,whichup=which))

            xcorr=self.upmin[which][whichdem][0]
            ycorr=self.upmin[which][whichdem][1]

            xmask=np.ma.masked_where(y==99999.,x)
            ymask=np.ma.masked_where(y==99999.,y)

            plt.scatter(xmask,ymask,marker='x',label=whichdem)
            plt.scatter(xcorr,ycorr,marker='+',label='selected points')

            plt.legend()
            plt.savefig(r'D:\OneDrive\OneDrive - Universite de Liege\Crues\2021-07 Vesdre\Simulations\Hydrologie\Up'+str(which)+'_'+whichdem+'.png')
            #plt.show()

    def write_slopes(self):
        #Uniquement les pentes runoff
        for curlist in LISTDEM:
            slopes= WolfArray(self.parent.dir+'\\Characteristic_maps\\Drainage_basin.slope')
            slopes.reset()
            curnode:Node_Watershed
            for curnode in self.nodes:
                i=curnode.i
                j=curnode.j
                slopes.array[i,j]=curnode.slopecorr[curlist]['value']

            slopes.filename = self.parent.dir+'\\Characteristic_maps\\Drainage_basin.slope_corr_run_'+curlist
            slopes.write_all()

    def slope_correctionmin(self):
        if not self.tslopemin is None:
            logging.info(_('select min - runoff'))
            self.selectmin()
            logging.info(_('slope correction min - runoff'))
            self.compute_slopescorr(self.upmin)

    def slope_correctionmax(self):
        if not self.tslopemax is None:
            logging.info(_('select max - runoff'))
            self.selectmax()
            logging.info(_('slope correction max - runoff'))
            self.compute_slopescorr(self.upmax)

    def selectmin(self):
        #Sélection des valeurs minimales afin de conserver une topo décroissante vers l'aval --> une pente positive
        self.upmin={}

        #on initialise le dictionnaire de topo min pour chaque amont
        for idx,curup in enumerate(self.upstreams['list']):
            self.upmin[idx]={}

        ds=self.parent.resolution
        curnode:Node_Watershed
        for curdem in LISTDEM:
            logging.info(_('Current DEM : {}'.format(curdem)))
            for idx,curup in enumerate(self.upstreams['list']):
                curnode=curup
                x=[]
                y=[]

                if curdem=='crosssection':
                    basey=min(curnode.dem[curdem],curnode.dem['dem_after_corr'])
                else:
                    basey=curnode.dem[curdem]

                x.append(curnode.cums)
                y.append(basey)
                curnode=curnode.down

                locs=ds
                while not curnode is None:
                    if curdem=='crosssection':
                        yloc=min(curnode.dem[curdem],curnode.dem['dem_after_corr'])
                    else:
                        yloc=curnode.dem[curdem]

                    if (basey-yloc)/locs>self.tslopemin:
                        x.append(curnode.cums)
                        y.append(yloc)
                        basey=yloc
                        locs=ds
                        if curnode.river:
                            break
                    else:
                        locs+=ds
                    curnode=curnode.down

                self.upmin[idx][curdem]=[x,y]

    def selectmax(self):
        #Sélection des valeurs minimales afin de conserver une topo décroissante vers l'aval --> une pente positive
        self.upmax={}

        #on initialise le dictionnaire de topo min pour chaque amont
        for idx,curup in enumerate(self.upstreams['list']):
            self.upmax[idx]={}

        ds=self.parent.resolution
        curnode:Node_Watershed
        for curdem in LISTDEM:
            logging.info(_('Current DEM : {}'.format(curdem)))
            for idx,curup in enumerate(self.upstreams['list']):
                curnode=curup
                x=[]
                y=[]

                """
                if curdem=='crosssection':
                    basey=min(curnode.demcorr[curdem]['value'],curnode.demcorr['dem_after_corr']['value'])
                else:
                    basey=curnode.demcorr[curdem]['value']
                """
                basey=curnode.demcorr[curdem]['value']

                x.append(curnode.cums)
                y.append(basey)
                curnode=curnode.down

                locs= ds
                while not curnode is None:
                    """
                    if curdem=='crosssection':
                        yloc=min(curnode.demcorr[curdem]['value'],curnode.demcorr['dem_after_corr']['value'])
                    else:
                        yloc=curnode.demcorr[curdem]['value']
                    """
                    yloc=curnode.demcorr[curdem]['value']

                    if (basey-yloc)/locs>self.tslopemax:
                        while len(x)>1 and (basey-yloc)/locs>self.tslopemax:
                            x.pop()
                            y.pop()
                            basey=y[-1]
                            locs+=ds

                    if yloc<y[-1]:
                        x.append(curnode.cums)
                        y.append(yloc)
                        basey=yloc
                        locs=ds
                        if curnode.river:
                            break

                    curnode=curnode.down
                    #if curnode.i==187 and curnode.j==207:
                    #    a=1

                self.upmax[idx][curdem]=[x,y]

    def compute_slopescorr(self, whichdict:dict):
        curnode:Node_Watershed
        for curdem in LISTDEM:
            logging.info(_('Current DEM : {}'.format(curdem)))
            for idx,curup in enumerate(self.upstreams['list']):
                curdict=whichdict[idx][curdem]
                xmin=curdict[0]
                if len(xmin)>1:
                    ymin=curdict[1]
                    x=self.get_cums(whichup=idx)

                    f=interpolate.interp1d(xmin,ymin, fill_value='extrapolate')
                    y=f(x)
                    slopes=self.compute_slope_down(x,y)

                    curnode=curup
                    i=0
                    while not curnode.river:
                        #if curnode.i==187 and curnode.j==207:
                        #    a=1
                        curnode.demcorr[curdem]['parts'].append(y[i])
                        curnode.slopecorr[curdem]['parts'].append(slopes[i])
                        i+=1
                        curnode=curnode.down
        #calcul de la moyenne sur base des valeurs partielles
        for curdem in LISTDEM:
            for curnode in self.nodes:
                #if curnode.i==187 and curnode.j==207:
                #    a=1
                if len(curnode.slopecorr[curdem]['parts'])<2:
                    #Ce cas particulier peut arriver si des mailles BV sont remplies par une zone plate qui s'étend en rivière
                    # Comme on ne recherche de mailles plus basses que dans la partie BV, il n'est pas possible de corriger les pentes
                    if not self.tslopemin is None:
                        curnode.slopecorr[curdem]['value']=max(self.tslopemin,curnode.slope)
                    else:
                        curnode.slopecorr[curdem]['value']=1.e-4

                    if not self.tslopemax is None:
                        curnode.slopecorr[curdem]['value']=min(self.tslopemax,curnode.slope)
                else:
                    curnode.demcorr[curdem]['value']=np.mean(curnode.demcorr[curdem]['parts'])
                    curnode.slopecorr[curdem]['value']=np.mean(curnode.slopecorr[curdem]['parts'])

                curnode.demcorr[curdem]['parts']=[]
                curnode.slopecorr[curdem]['parts']=[]

    def compute_slope_down(self, x, y):
        """
        Calcul de la pente sur base de listes X et Y
        """
        slope=[]
        for i in range(len(x)-1):
            slope.append((y[i+1]-y[i])/(x[i+1]-x[i]))
        slope.append(slope[-1])
        return slope

class SubWatershed:
    """ Classe sous-bassin versant """
    def __init__(self,
                 parent:"Watershed",
                 name:str,
                 idx:int,
                 mask:WolfArray,
                 nodes:list[Node_Watershed],
                 runoff:list[Node_Watershed],
                 rivers:list[Node_Watershed]) -> None:

        self.parent = parent
        self.index  = idx
        self.name   = name
        self.mask   = mask
        self.nodes  = nodes
        self.rivers = rivers
        self.runoff = runoff
        self.idx_reaches = np.unique(np.asarray([x.reach for x in rivers]))

    @property
    def surface(self) -> float:
        return self.mask.nbnotnull * self.mask.dx * self.mask.dy

class Watershed:
    """Classe bassin versant"""

    header:header_wolf  # header_wolf of "Drainage_basin.sub" wolf_array

    dir: str            # Répertoire de modélisation

    outlet:Node_Watershed   # exutoire

    subs_array: WolfArray # "Drainage_basin.sub" wolf_array

    nodes:list[Node_Watershed] # all nodes
    nodesindex:np.ndarray # indirect access to mynodes, contains index of instance in list
    rivers:list[Node_Watershed] # all river nodes
    runoff:list[Node_Watershed] # all runoff nodes

    couplednodes:list # forced exchanges

    subcatchments: list[SubWatershed]
    statisticss: dict

    couplednodesxy:list[float,float,float,float]
    couplednodesij:list[tuple[int,int],tuple[int,int]]

    riversystem:RiverSystem     # réseau de rivières
    runoffsystem:RunoffSystem   # écoulement diffus/hydrologique

    to_update_times:bool        # switch to detect if the time matrix should be updated

    def __init__(self,
                 dir:str,
                 thzmin:float=None,
                 thslopemin:float=None,
                 thzmax:float=None,
                 thslopemax:float=None,
                 crosssections:CrossSections=None,
                 computestats:bool=False,
                 computecorr:bool=False,
                 plotstats:bool=False,
                 plotriversystem=False,
                 *args, **kwargs):

        logging.info(_('Read files...'))
        self.dir=os.path.normpath(dir)

        self.subs_array   = WolfArray(self.dir+'\\Characteristic_maps\\Drainage_basin.sub')

        self.header = self.subs_array.get_header()

        #FIXME
        isOk, fe_file = check_path(os.path.join(self.dir, "Coupled_pairs.txt"), prefix=self.dir)
        self.couplednodesxy=[]
        self.couplednodesij=[]

        if isOk>=0:
            f = open(fe_file, 'r')
            lines = f.read().splitlines()
            f.close()

            if lines[0]=='COORDINATES':
                for xy in enumerate(lines[1:]):
                    xup,yup,xdown,ydown=xy[1].split('\t')
                    self.couplednodesxy.append([float(xup),float(yup),float(xdown),float(ydown)])
                    self.couplednodesij.append([self.subs_array.get_ij_from_xy(float(xup),float(yup)),self.subs_array.get_ij_from_xy(float(xdown),float(ydown))])

        logging.info(_('Initialization of nodes...'))
        self.nodesindex = np.zeros([self.subs_array.nbx,self.subs_array.nby], dtype=int)
        self.outlet = None
        self.up = None
        self.init_nodes()

        logging.info(_('Initialization of subwatersheds...'))
        self.init_subs()

        if not crosssections is None:
            logging.info(_('Cross sections...'))
            self.crosssections = crosssections
            self.attrib_cs_to_nodes()
        else:
            self.crosssections = None

        logging.info(_('Slopes corrections...'))
        self.riversystem  = RiverSystem(self.rivers , self,thslopemin=thslopemin, thslopemax=thslopemax, computecorr=computecorr)
        self.runoffsystem = RunoffSystem(self.runoff, self,thslopemin=thslopemin, thslopemax=thslopemax, computecorr=computecorr)

        if computestats or plotstats:
            logging.info(_('Statistics...'))
            self.compute_stats(plotstats)

        #Ecriture des résultats de correction des pentes
        if computecorr:
            logging.info(_('Writing data to disk'))
            self.write_dem()
            self.write_slopes()

        if plotriversystem:
            logging.info(_('Plot rivers'))
            self.riversystem.plot_all_in_notebook()

        self.to_update_times = False

        logging.info(_('Done!'))

    @property
    def nb_subs(self):
        return int(ma.max(self.subs_array.array))

    @property
    def resolution(self):
        return self.header.dx

    def get_node_from_ij(self, i:int,j:int):
        """
        Récupération d'un objet Node_Watershed sur base des indices (i,j)
        """
        shape = self.nodesindex.shape
        if i<0 or i>=shape[0]:
            return None
        if j<0 or j>=shape[1]:
            return None
        idx = self.nodesindex[i,j]
        if idx<0 or idx >= len(self.nodes):
            return None

        return self.nodes[idx]

    def get_node_from_xy(self, x:float, y:float):
        """
        Récupération d'un objet Node_Watershed sur base des coordonnées (x,y)
        """
        i,j = self.header.get_ij_from_xy(x,y)
        return self.get_node_from_ij(i,j)

    def write_slopes(self):
        """
        Ecriture sur disque
        """
        for curlist in LISTDEM:
            curpath=self.dir+'\\Characteristic_maps\\corrslopes\\'+curlist
            os.makedirs(curpath,exist_ok=True)
            slopes= WolfArray(self.dir+'\\Characteristic_maps\\Drainage_basin.slope')

            ijval = np.asarray([[curnode.i, curnode.j, curnode.slopecorr[curlist]['value']]  for curnode in self.nodes])
            slopes.array[np.int32(ijval[:,0]),np.int32(ijval[:,1])]=ijval[:,2]

            slopes.filename = curpath +'\\Drainage_basin.slope_corr'
            slopes.write_all()

    def write_dem(self):
        """
        Ecriture sur disque
        """
        for curlist in LISTDEM:
            curpath=self.dir+'\\Characteristic_maps\\corrdem\\'+curlist
            os.makedirs(curpath,exist_ok=True)
            dem= WolfArray(self.dir+'\\Characteristic_maps\\Drainage_basincorr.b')

            ijval = np.asarray([[curnode.i, curnode.j, curnode.demcorr[curlist]['value']]  for curnode in self.nodes])
            dem.array[np.int32(ijval[:,0]),np.int32(ijval[:,1])]=ijval[:,2]

            dem.filename = curpath +'\\Drainage_basincorr.b'
            dem.write_all()

    @property
    def crosssections(self):
        return self._cs

    @crosssections.setter
    def crosssections(self, value:CrossSections):
        self._cs = value

    def attrib_cs_to_nodes(self):
        """
        Attribution des sections en travers aux noeuds
        """
        if self.crosssections is not None:
            for curlist in self.crosssections:
                for namecs in curlist.myprofiles:
                    curvert:wolfvertex
                    curcs=curlist.myprofiles[namecs]

                    try:
                        curvert=curcs['bed']
                    except:
                        curvert=curlist.get_min(whichprofile=curcs)

                    i,j=self.subs_array.get_ij_from_xy(curvert.x,curvert.y)
                    curnode:Node_Watershed
                    curnode =self.nodes[self.nodesindex[i,j]]

                    if curnode.river:
                        if curnode.crosssections is None:
                            curnode.crosssections=[]
                        curnode.crosssections.append(curcs)
                        curnode.dem['crosssection']=min(curnode.dem['crosssection'],curvert.z)

    def init_nodes(self):
        """
        Initialisation des noeuds
        """

        self.nodes=[Node_Watershed() for i in range(self.subs_array.nbnotnull)]

        dem_before_corr= WolfArray(self.dir+'\\Characteristic_maps\\Drainage_basin.b')
        dem_after_corr= WolfArray(self.dir+'\\Characteristic_maps\\Drainage_basincorr.b')
        #Tests of the existance of the delta dem
        isOk,demdeltaFile = check_path(os.path.join(self.dir,'Characteristic_maps\\Drainage_basindiff.b'))
        if isOk<0:
            logging.error("The ...dif.b file is not present! Please check the reason or launch again the hydrological preprocessing! A Null diff matrix will then be considered for the next steps.")
            demdelta = WolfArray(mold=dem_after_corr)
            demdelta.array = 0.0
        else:
            demdelta = WolfArray(demdeltaFile)
        #
        slopes= WolfArray(self.dir+'\\Characteristic_maps\\Drainage_basin.slope',masknull=False)
        reaches= WolfArray(self.dir+'\\Characteristic_maps\\Drainage_basin.reachs')
        cnv= WolfArray(self.dir+'\\Characteristic_maps\\Drainage_basin.cnv')
        times= WolfArray(self.dir+'\\Characteristic_maps\\Drainage_basin.time')


        dem_after_corr.array.mask = self.subs_array.array.mask

        nb=0
        for index,i_sub in tqdm(np.ndenumerate(self.subs_array.array), 'Numbering'):
            if(i_sub>0):
                i=int(index[0])
                j=int(index[1])
                self.nodesindex[i,j]=nb
                nb+=1

        curnode:Node_Watershed
        nb=0
        for index, i_sub in tqdm(np.ndenumerate(self.subs_array.array), 'Initialization'):
            if(i_sub>0):
                i=int(index[0])
                j=int(index[1])
                x, y = self.header.get_xy_from_ij(i,j)
                curnode =self.nodes[self.nodesindex[i,j]]

                curnode.i = i
                curnode.j = j

                curnode.x = x
                curnode.y = y

                curnode.crosssections = None
                curnode.down = None

                curnode.index=nb
                curnode.dem={}
                curnode.dem['dem_before_corr']=dem_before_corr.array[i,j]
                curnode.dem['dem_after_corr']=dem_after_corr.array[i,j]
                curnode.dem['crosssection']=99999.
                curnode.demdelta=demdelta.array[i,j]
                curnode.slope=slopes.array[i,j]

                curnode.slopecorr={}
                for curlist in LISTDEM:
                    curnode.slopecorr[curlist]={}
                    curnode.slopecorr[curlist]['parts']=[]
                    curnode.slopecorr[curlist]['value']=curnode.slope

                curnode.demcorr={}
                for curlist in LISTDEM:
                    curnode.demcorr[curlist]={}
                    curnode.demcorr[curlist]['parts']=[]
                    curnode.demcorr[curlist]['value']=curnode.dem['dem_after_corr']

                curnode.sub=int(i_sub)
                curnode.time=times.array[i,j]
                curnode.uparea=cnv.array[i,j]
                curnode.river=not reaches.array.mask[i,j]
                if curnode.river:
                    curnode.reach=int(reaches.array[i,j])
                curnode.forced=False
                curnode.up=[]
                curnode.upriver=[]
                curnode.strahler=0
                curnode.reachlevel=0
                nb+=1

        curdown:Node_Watershed
        #Liaison échanges forcés
        incr=slopes.dx
        for curexch in self.couplednodesij:
            i=int(curexch[0][0])
            j=int(curexch[0][1])
            curnode=self.nodes[self.nodesindex[i,j]]
            curnode.forced=True
            idown = int(curexch[1][0])
            jdown = int(curexch[1][1])
            curdown = self.nodes[self.nodesindex[idown,jdown]]
            curnode.down = curdown
            curdown.up.append(curnode)
            if curnode.river:
                curdown.upriver.append(curnode)
            curnode.incrs = incr * np.sqrt(pow(curdown.i-i,2)+pow(curdown.j-j,2))

        #Liaison hors échanges forcés
        for curnode in tqdm(self.nodes, 'Linking'):
            if not curnode.forced:
                i=curnode.i
                j=curnode.j

                curtop=curnode.dem['dem_after_corr']

                neigh = [[i-1,j],[i+1,j],[i,j-1], [i,j+1]]
                diff = [dem_after_corr.array[curi,curj]-curtop if not dem_after_corr.array.mask[curi,curj] else 100000. for curi,curj in neigh]
                mindiff = np.min(diff)
                if mindiff<0:
                    index = diff.index(mindiff)
                    if index==0:
                        curdown = self.nodes[self.nodesindex[i-1,j]]
                    elif index==1:
                        curdown = self.nodes[self.nodesindex[i+1,j]]
                    elif index==2:
                        curdown = self.nodes[self.nodesindex[i,j-1]]
                    else:
                        curdown = self.nodes[self.nodesindex[i,j+1]]

                    curnode.down = curdown
                    curdown.up.append(curnode)
                    if curnode.river:
                        curdown.upriver.append(curnode)
                    curnode.incrs=incr
                else:
                    self.outlet = curnode

        #Rechreche de la pente dans les voisins en croix dans la topo non remaniée
        for curnode in tqdm(self.nodes, 'Finding slope'):
            if not curnode.forced:
                i=curnode.i
                j=curnode.j

                curtop = curnode.dem['dem_before_corr']

                neigh = [[i-1,j], [i+1,j], [i,j-1], [i,j+1], [i-1,j-1], [i+1,j+1], [i+1,j-1], [i-1,j+1]]
                diff = [dem_before_corr.array[curi,curj]-curtop if not dem_before_corr.array.mask[curi,curj] else 100000. for curi,curj in neigh ]
                mindiff = np.min(diff)

                fact=1.
                if mindiff<0:
                    index = diff.index(mindiff)
                    if index>3:
                        fact=np.sqrt(2)

                curnode.sloped8 = -mindiff/(self.resolution*fact)

        self.rivers=list(filter(lambda x: x.river,self.nodes))
        self.rivers.sort(key=lambda x: x.dem['dem_after_corr'])
        sys.setrecursionlimit(len(self.nodes))
        self.outlet.incr_curvi()

        self.find_dem_subpixels()

        self.runoff=self.find_runoffnodes()

    def find_rivers(self, whichsub:int=0, whichreach:int=0) -> tuple[list[Node_Watershed], Node_Watershed]:
        """
        Recherche des mailles rivières
        :param whichsub : numéro du sous-bassin à traiter
        :param whicreach : numéro du tronçon à identifier
        """
        if whichsub>0 and whichsub<=self.nb_subs:
            if whichreach>0:
                myrivers=list(filter(lambda x: x.river and x.sub==whichsub and x.reach==whichreach,self.rivers))
            else:
                myrivers=list(filter(lambda x: x.river and x.sub==whichsub,self.rivers))
        else:
            if whichreach>0:
                myrivers=list(filter(lambda x: x.river and x.reach==whichreach,self.rivers))
            else:
                myrivers=list(filter(lambda x: x.river,self.rivers))

        myrivers.sort(key=lambda x: x.dem['dem_after_corr'])

        up=None
        if len(myrivers)>0:
            up=myrivers[-1]

        return myrivers,up

    def find_sub(self, whichsub:int=0) -> list[Node_Watershed]:
        """
        Recherche des mailles du sous-bassin versant
        :param whichsub : numéro du sous-bassin à traiter
        """
        if whichsub>0 and whichsub<=self.nb_subs:
            mysub=list(filter(lambda x: x.sub==whichsub, self.nodes))
        else:
            mysub=self.nodes.copy()

        mysub.sort(key=lambda x: x.dem['dem_after_corr'])

        return mysub

    def init_subs(self):
        """
        Initialize Sub-Catchments
        """
        self.subcatchments=[]

        #Initialisation de la matrice de mask (d'une extension et d'une résolution similaire aux données radar)
        for i in tqdm(range(1,self.nb_subs+1), 'Subwatershed'):
            curmask = WolfArray(mold=self.subs_array)
            curmask.mask_allexceptdata(float(i))
            all_river_nodes, _ = self.find_rivers(i)

            cursub = SubWatershed(self,
                                  name = 'sub n'+str(i),
                                  idx=i-1,
                                  mask = curmask,
                                  nodes = self.find_sub(i),
                                  runoff=self.find_runoffnodes(i),
                                  rivers=all_river_nodes,
                                  )

            self.subcatchments.append(cursub)

    def find_runoffnodes(self, whichsub:int=0) -> list[Node_Watershed]:
        """
        Recherche des mailles du bassin versant seul (sans les rivières)
        :param whichsub : numéro du sous-bassin à traiter
        """
        if whichsub>0 and whichsub<=self.nb_subs:
            myrunoff=list(filter(lambda x: not x.river and x.sub==whichsub,self.nodes))
        else:
            myrunoff=list(filter(lambda x: not x.river,self.nodes))

        myrunoff.sort(key=lambda x: x.dem['dem_after_corr'])

        return myrunoff

    def index_flatzone(self, listofsortednodes:list, threshold:float):
        """
        Indexation des zones de plat
        """

        curnode:Node_Watershed
        curflat:Node_Watershed

        curindex=0
        for curnode in listofsortednodes[-1:1:-1]:
            addone=False
            while curnode.slope<threshold and curnode.flatindex==-1:
                addone=True
                curnode.flatindex=curindex
                if curnode.down is None:
                    break
                curnode=curnode.down
            if addone:
                curindex+=1

        return curindex

    def find_flatnodes(self, listofsortednodes:list):
        """
        Recherche des mailles dans des zones de faibles pentes
        :param listofsortednodes : liste triée de mailles
        """
        myflatnodes=list(filter(lambda x: x.flatindex>-1,listofsortednodes))

        return myflatnodes

    def find_flatzones(self, listofsortednodes:list, maxindex:int):
        """
        Recherche des mailles dans des zones de faibles pentes
        :param listofsortednodes : liste triée de mailles
        """
        myflatzones=[[]] * maxindex
        for i in range(maxindex):
            myflatzones[i]=list(filter(lambda x: x.flatindex==i,listofsortednodes))

        return myflatzones

    def find_dem_subpixels(self):
        """
        Recherche des altitudes dans un mnt plus dense
        """
        demsubs = {}
        file_10m = os.path.join(self.dir,'mnt10m.bin')
        isOk, file_10m = check_path(file_10m, prefix=self.dir)
        if isOk>=0:
            dem_10m=WolfArray(file_10m)
            demsubs["dem_10m"] = dem_10m

        file_20m = os.path.join(self.dir,'mnt20m.bin')
        isOk, file_20m = check_path(file_20m, prefix=self.dir)
        if isOk>=0:
            dem_20m=WolfArray(file_20m)
            demsubs["dem_20m"] = dem_20m


        # demsubs={'dem_10m':dem_10m,'dem_20m':dem_20m}
        if len(demsubs)==0:
            return

        curnode:Node_Watershed
        for curdem in tqdm(demsubs, 'Sub-pixeling'):
            locdem=demsubs[curdem]
            dx=locdem.dx
            dy=locdem.dy

            for curnode in tqdm(self.nodes):
                curi=curnode.i
                curj=curnode.j

                curx,cury=self.subs_array.get_xy_from_ij(curi,curj)

                decalx=(self.resolution-dx)/2.
                decaly=(self.resolution-dy)/2.
                x1=curx-decalx
                y1=cury-decaly
                x2=curx+decalx
                y2=cury+decaly

                i1,j1=locdem.get_ij_from_xy(x1,y1)
                i2,j2=locdem.get_ij_from_xy(x2,y2)

                curnode.dem[curdem]=np.min(locdem.array[i1:i2+1,j1:j2+1])

    def compute_stats(self, plot:bool=False):
        """
        Calcul des statistiques de pente
        """
        self.statisticss={}

        slopes=np.array(list(x.slope for x in self.nodes))
        slopesrunoff=np.array(list(x.slope for x in list(filter(lambda x: not x.river,self.nodes))))
        slopesriver=np.array(list(x.slope for x in list(filter(lambda x: x.river,self.nodes))))

        curdict=self.statisticss
        curdict['slopemin'] = np.min(slopes)
        curdict['slopemax'] = np.max(slopes)
        curdict['slopemedian'] = np.median(slopes)
        curdict['slopemean'] = np.mean(slopes)
        curdict['hist'] = slopes
        curdict['hist_watershed'] = slopesrunoff
        curdict['hist_reaches'] = slopesriver
        curdict['count_neg'] = np.count_nonzero(slopes < 0.)

        logging.info(_('Min : {}'.format(curdict['slopemin'])))
        logging.info(_('Max : {}'.format(curdict['slopemax'])))
        logging.info(_('Median : {}'.format(curdict['slopemedian'])))
        logging.info(_('Mean : {}'.format(curdict['slopemean'])))
        logging.info(_('Non Zero : {}'.format(curdict['count_neg'])))

        for curlist in LISTDEM:
            curdict=self.statisticss[curlist]={}

            slopes=np.array(list(x.slopecorr[curlist]['value'] for x in self.nodes))
            slopesrunoff=np.array(list(x.slopecorr[curlist]['value'] for x in list(filter(lambda x: not x.river,self.nodes))))
            slopesriver=np.array(list(x.slopecorr[curlist]['value'] for x in list(filter(lambda x: x.river,self.nodes))))

            curdict['slopemin'] = np.min(slopes)
            curdict['slopemax'] = np.max(slopes)
            curdict['slopemedian'] = np.median(slopes)
            curdict['slopemean'] = np.mean(slopes)
            curdict['hist'] = slopes
            curdict['hist_watershed'] = slopesrunoff
            curdict['hist_reaches'] = slopesriver
            curdict['count_neg'] = np.count_nonzero(slopes < 0.)

            logging.info(_('Current list : '.format(curlist)))
            logging.info(_('Min : {}'.format(curdict['slopemin'])))
            logging.info(_('Max : {}'.format(curdict['slopemax'])))
            logging.info(_('Median : {}'.format(curdict['slopemedian'])))
            logging.info(_('Mean : {}'.format(curdict['slopemean'])))
            logging.info(_('Non Zero : {}'.format(curdict['count_neg'])))

        if plot:
            self.plot_stats()

    def plot_stats(self):

        self.myplotterstats = PlotNotebook()

        bin1=np.array([1.e-8,1.e-7,1.e-6,5.e-6])
        bin2=np.linspace(1.e-5,1e-3,num=20)
        bin3=np.linspace(2.e-3,1e-1,num=20)
        bin4=np.linspace(.11,1,num=100)
        bins=np.concatenate((bin1,bin2,bin3,bin4))

        fig=self.myplotterstats.add(_('Slope distribution - log'))

        ax = fig.add_ax()
        ax.hist(self.statisticss['hist'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xscale('log')
        ax.set_xlabel(_('All meshes'))

        for curlist in LISTDEM:
            curdict=self.statisticss[curlist]
            ax.hist(curdict['hist'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)

        ax = fig.add_ax()
        ax.hist(self.statisticss['hist_watershed'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xscale('log')
        ax.set_xlabel(_('Watershed'))

        for curlist in LISTDEM:
            curdict=self.statisticss[curlist]
            ax.hist(curdict['hist_watershed'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)

        ax = fig.add_ax()
        ax.hist(self.statisticss['hist_reaches'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xscale('log')
        ax.set_xlabel(_('River'))

        for curlist in LISTDEM:
            curdict=self.statisticss[curlist]
            ax.hist(curdict['hist_reaches'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)

        ax.legend()
        fig.canvas.draw()

        fig=self.myplotterstats.add(_('Slope distribution'))
        ax:plt.axis

        ax = fig.add_ax()
        ax.hist(self.statisticss['hist'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xlabel(_('All meshes'))

        for curlist in LISTDEM:
            curdict=self.statisticss[curlist]
            ax.hist(curdict['hist'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)

        ax = fig.add_ax()
        ax.hist(self.statisticss['hist_watershed'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xlabel(_('Watershed'))

        for curlist in LISTDEM:
            curdict=self.statisticss[curlist]
            ax.hist(curdict['hist_watershed'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)

        ax = fig.add_ax()
        ax.hist(self.statisticss['hist_reaches'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xlabel(_('River'))

        for curlist in LISTDEM:
            curdict=self.statisticss[curlist]
            ax.hist(curdict['hist_reaches'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)

        ax.legend()
        fig.canvas.draw()

    def analyze_flatzones(self):
        """
        Analyse des zones de plat
        """
        self.myplotterflat = PlotNotebook()

        ### Flat zones
        eps=1e-7
        #indexation des zones "indépendantes" de plats - ruissellement
        maxindex=self.index_flatzone(self.runoff,eps)
        #identification des mailles dans les zones
        myflatnodes=self.find_flatnodes(self.runoff)
        #création de listes avec les noeuds dans chaque zone
        myflats=self.find_flatzones(myflatnodes,maxindex)

        #calcul de la longueur de la zone de plat --> sommation du nombre de mailles
        lenflats=np.zeros((maxindex),dtype=np.int32)
        for i in range(maxindex):
            lenflats[i]=len(myflats[i])

        #indexation des zones "indépendantes" de plats - rivières
        maxindexrivers=self.index_flatzone(self.rivers,eps)
        #création de listes avec les noeuds dans chaque zone - rivières
        myflatsrivers=self.find_flatzones(self.rivers,maxindexrivers)

        #calcul de la longueur de la zone de plat --> sommation du nombre de mailles
        lenflatsrivers=np.zeros((maxindexrivers),dtype=np.int32)
        for i in range(maxindexrivers):
            lenflatsrivers[i]=len(myflatsrivers[i])

        fig:mplfig.Figure
        fig=self.myplotterflat.add("Nb nodes in flat area")
        ax=fig.add_ax()
        mybins=np.arange(0.5,np.max(lenflats),1.)
        myticks=np.arange(1,np.ceil(np.max(lenflats)),1)
        ax.hist(lenflats,bins=mybins)
        ax.set_xlabel(_('Nb nodes in flat area - runoff'))
        ax.set_xticks(myticks)
        ax.set_xbound(.5,np.max(lenflats))
        ax.set_ylabel('Nb flat areas')
        ax.set_yscale('log')

        ax=fig.add_ax()
        mybinsrivers=np.arange(0.5,np.max(lenflatsrivers),1.)
        myticksrivers=np.arange(1,np.ceil(np.max(lenflatsrivers)),1)
        ax.hist(lenflatsrivers,bins=mybinsrivers)
        ax.set_xlabel(_('Nb nodes in flat area - rivers'))
        ax.set_xticks(myticksrivers)
        ax.set_xbound(.5,np.max(lenflatsrivers))
        ax.set_ylabel('Nb flat areas')
        ax.set_yscale('log')

        fig=self.myplotterflat.add("Nb nodes in flat area")
        ax=fig.add_ax()
        ax.hist(lenflats,bins=mybins,cumulative=True,density=True)
        ax.set_xlabel(_('Nb nodes in flat area - runoff'))
        ax.set_xticks(myticks)
        ax.set_xbound(.5,np.max(lenflats))
        ax.set_ylabel('Cumulative flat areas')
        #ax.set_yscale('log')

        ax=fig.add_ax()
        ax.hist(lenflatsrivers,bins=mybinsrivers,cumulative=True,density=True)
        ax.set_xlabel(_('Nb nodes in flat area - rivers'))
        ax.set_xticks(myticksrivers)
        ax.set_xbound(.5,np.max(lenflatsrivers))
        ax.set_ylabel('Cumulative flat areas')
        #ax.set_yscale('log')
        fig.canvas.draw()

        #Tri des pentes dans différentes listes

        #toutes les mailles
        sdown=[]
        sup=[]
        for curflat in myflats:
            for curnode in curflat:
                #recherche de la pente aval plus grande que le seuil
                sdown.append(curnode.slope_down(eps))
                #recherche de la pente amont moyenne - uniquement pour les mailles qui ont une pente supérieure au seuil
                sup.append(curnode.mean_slope_up(eps))

        sflat=[]
        sdownraw=[]
        for curflat in myflats:
            for curnode in curflat:
                #pente de la maille aval
                sdownraw.append(curnode.down.slope)
                #pente courante
                sflat.append(curnode.slope)

        #mailles rivières
        sdownriv=[]
        supriv=[]
        suponlyriv=[]
        for curflat in myflatsrivers:
            for curnode in curflat:
                #recherche de la pente aval plus grande que le seuil
                sdownriv.append(curnode.slope_down(eps))
                #recherche de la pente amont moyenne - uniquement pour les mailles qui ont une pente supérieure au seuil
                supriv.append(curnode.mean_slope_up(eps))
                #recherche de la pente amont > seuil
                suponlyriv.append(curnode.slope_upriver(eps))

        sdownd8=[]
        suponlyriv1=[]
        for curflat in myflatsrivers:
            for curnode in curflat:
                #pente aval selon voisines D8
                sdownd8.append(curnode.sloped8)
                #recherche de la pente amont > seuil
                suponlyriv1.append(curnode.slope_upriver(eps))

        sflatriver=[]
        sdownrawriver=[]
        sd8rawriver=[]
        for curflat in myflatsrivers:
            if len(curflat)==1:
                for curnode in curflat:
                    if not curnode.down is None:
                        sd8rawriver.append(curnode.sloped8)
                        sdownrawriver.append(curnode.down.slope)
                        sflatriver.append(curnode.slope)


        #tracage des graphiques
        fig=self.myplotterflat.add("Scatter plots")
        ax=fig.add_ax()
        ax.scatter(sdownrawriver,sflatriver,marker='o',label='slope down vs flat slope')
        ax.scatter(sdownriv,suponlyriv,marker='+',label='slope down vs slope d8')
        ax=fig.add_ax()
        ax.scatter(sdownraw,sflat,marker='0',label='slope down vs flat slope')
        ax.scatter(sdown,sup,marker='+',label='slope down vs slope up')
        fig.canvas.draw()

        fig=self.myplotterflat.add("Scatter plots 2")
        curax=fig.add_ax()
        curax.scatter(sdown,sup,marker='+')
        curax.set_xlabel(_('Slope down [-]'))
        curax.set_ylabel(_('Mean slope up [-]'))
        curax.set_aspect('equal','box')
        curax.set_xbound(0,.55)
        curax.set_ybound(0,.55)
        curax.set_title('Runoff')

        curax=fig.add_ax()
        curax.scatter(sdownriv,supriv,marker='+')
        curax.set_xlabel(_('Slope down [-]'))
        curax.set_ylabel(_('Mean slope up [-]'))
        curax.set_aspect('equal','box')
        curax.set_xbound(0,.55)
        curax.set_ybound(0,.55)
        curax.set_title('River')

        curax=fig.add_ax()
        curax.scatter(sdownriv,suponlyriv,marker='+')
        curax.set_xlabel(_('Slope down [-]'))
        curax.set_ylabel(_('Slope up only river [-]'))
        curax.set_aspect('equal','box')
        curax.set_xbound(0,.55)
        curax.set_ybound(0,.55)
        curax.set_title('River')

        curax=fig.add_ax()
        curax.scatter(sdownd8,suponlyriv1,marker='+')
        curax.set_xlabel(_('Slope D8 [-]'))
        curax.set_ylabel(_('Slope up only river [-]'))
        curax.set_aspect('equal','box')
        curax.set_xbound(0,.3)
        curax.set_ybound(0,.3)
        curax.set_title('River')
        fig.canvas.draw()

    def update_times(self, wolf_time=None):

        if wolf_time is None:
            wolf_time = WolfArray(self.dir+'\\Characteristic_maps\\Drainage_basin.time')

        for cur_node in self.nodes:
            cur_node.time = wolf_time[cur_node.i, cur_node.j]

        self.to_update_times = False
