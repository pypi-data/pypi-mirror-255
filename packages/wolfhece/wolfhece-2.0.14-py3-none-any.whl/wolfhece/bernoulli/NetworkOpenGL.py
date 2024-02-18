import matplotlib.pyplot as plt
import numpy as np
import itertools as it
import time
import matplotlib as mpl
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from wx.lib.plot import PolyLine, PlotCanvas, PlotGraphics
import wx
import wx.grid as grid
import wx.glcanvas as glcanvas
import wx.lib.mixins.listctrl  as  listmix
from os.path import dirname, join, curdir
import re
from math import pi,ceil,sin,cos,sqrt
import logging

try:
    from OpenGL.GL import *
    from OpenGL.GLUT import *
    from OpenGL.GLU import *
except:
    msg=_('Error importing OpenGL library')
    msg+=_('   Python version : ' + sys.version)
    msg+=_('   Please check your version of opengl32.dll -- conflict may exist between different files present on your desktop')
    raise Exception(msg)

from ..PyTranslate import _
from ..pylogging import create_wxlogwindow
from ..PyParams import Wolf_Param, Type_Param, key_Param
from ..PyPalette import wolfpalette
try:
    from ..libs import wolfpy
except:
    msg=_('Error importing wolfpy.pyd')
    msg+=_('   Python version : ' + sys.version)
    msg+=_('   If your Python version is not 3.7.x or 3.9.x, you need to compile an adapted library with compile_wcython.py in wolfhece library path')
    msg+=_('   See comments in compile_wcython.py or launch *python compile_wcython.py build_ext --inplace* in :')
    msg+='      ' + dirname(__file__)

    raise Exception(msg)

cubeVertices = ((100,100,0),(100,10,0),(100,200,0),(10,100,0))
cubeEdges = ((0,1),(0,2),(0,3),(1,2),(1,3))
width, height = 500, 400

#Paramètres liés à l'utilisation des paramètres généraux
Special_Entries     = ['Roughness Law','Roughness Law Valves','Presence of leakages','Effect of Inertia','Associated_Opt_Problem','Name_Linear_Solver']
Dft_Param           = ['2','2','0','0','0','ma27']
Translation_Entry   = [[[],[]],[[],[]],[[],[]],[[],[]],[[],[]],[[],[]]]
Translation_Entry[0][0] = ['1','2','3','4','5','6','7','8']
Translation_Entry[0][1] = ['Bazin','Colebrook','Manning','Barr_Bathurst','Haaland','Colebrook_White_explicit','Manning_2Dvert','Hazen_Williams']
Translation_Entry[1][0] = ['1','2','3','4','5','6','7','8']
Translation_Entry[1][1] = ['Bazin','Colebrook','Manning','Barr_Bathurst','Haaland','Colebrook_White_explicit','Manning_2Dvert','Hazen_Williams']
Translation_Entry[5][0] = ['ma27','ma57','ma77','ma86','ma97','mumps']
Translation_Entry[5][1] = ['ma27','ma57','ma77','ma86','ma97','mumps']
for i in range(3):
    Translation_Entry[i+2][0]=['0','1']
    Translation_Entry[i+2][1]=['No','Yes']

class Bernoulli_Frame(wx.Frame):
    """
    Fenêtre d'interaction utilisateur
    """
    def __init__(self, *args, **kwargs):
        super(Bernoulli_Frame, self).__init__(*args, **kwargs)

        self.InitUI()

    def InitUI(self):

        #Partie Menu

        menubar = wx.MenuBar()

        #Premier menu
        fileMenu = wx.Menu()
        NewNet=fileMenu.Append(wx.ID_NEW, _('&New'))
        menuOpen=fileMenu.Append(wx.ID_OPEN, _('&Open'),_('Open a file to edit'))
        SaveNet=fileMenu.Append(wx.ID_SAVE, _('&Save'))
        Launch=fileMenu.Append(wx.ID_ANY, _('&Launch Simulation'))
        fileMenu.AppendSeparator()

        imp = wx.Menu()
        self.Network0D=False
        NWoE=imp.Append(wx.ID_ANY, _('Import EPANET'))
        #imp.Append(wx.ID_ANY, 'Import bookmarks...')
        #imp.Append(wx.ID_ANY, 'Import mail...')

        fileMenu.Append(wx.ID_ANY, _('I&mport'), imp)

        #On associe les différents évènements liés à ces menus
        #Fermeture de l'application
        qmi = wx.MenuItem(fileMenu, wx.ID_EXIT, _('&Quit\tCtrl+W'))
        fileMenu.Append(qmi)

        self.Bind(wx.EVT_MENU, self.OnQuit, qmi)
        self.Bind(wx.EVT_MENU, self.OpenNetwork, menuOpen)
        pathname=self.Bind(wx.EVT_MENU, self.SaveNetwork, SaveNet)
        self.InitNetwork=0
        self.Bind(wx.EVT_MENU, self.LaunchSimul, Launch)
        #Ouvrir réellement nouveau fichier

        menubar.Append(fileMenu, _('&File'))
        self.menubar=menubar
        self.SetMenuBar(self.menubar)
        #Ouvrir box pour ajouter nouveau jeu ou nouveau lien
        #On associe les différents évènements

        #Partie Toolbar
        self.count = 5
        self.LocalNode =[0,0,0]
        self.toolbar = self.CreateToolBar()
        # tundo = self.toolbar.AddTool(wx.ID_UNDO, '', wx.Bitmap(join(dirname(__file__),'exit8.png')))
        # tredo = self.toolbar.AddTool(wx.ID_REDO, '',wx.Bitmap(join(dirname(__file__),'exit7.png')))
        # self.toolbar.EnableTool(wx.ID_REDO, False)
        # self.toolbar.AddSeparator()
        texit = self.toolbar.AddTool(wx.ID_EXIT, '', wx.Bitmap(join(dirname(__file__),'exit3.png')))
        self.toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.OnQuit, texit)
        # self.Bind(wx.EVT_TOOL, self.OnUndo, tundo)
        # self.Bind(wx.EVT_TOOL, self.OnRedo, tredo)

        self.SetSize((600, 600))
        self.SetTitle(_('Network 0D'))
        self.Centre()
        Click_Info=[]
        #Evènements pour la création et importation d'un réseau depuis un dossier EPANET (inp) fourni par l'utilisateur
        self.Bind(wx.EVT_TOOL, self.ImportEPanet, NWoE)

        #Evènements pour la création d'un nouveau réseau
        self.Bind(wx.EVT_TOOL, self.on_new_frame, NewNet)
        self.mylogs = create_wxlogwindow(_('Informations'))

    # def OnUndo(self, e):
    #     if self.count > 1 and self.count <= 5:
    #         self.count = self.count - 1

    #     if self.count == 1:
    #         self.toolbar.EnableTool(wx.ID_UNDO, False)

    #     if self.count == 4:
    #         self.toolbar.EnableTool(wx.ID_REDO, True)

    # def OnRedo(self, e):
    #     if self.count < 5 and self.count >= 1:
    #         self.count = self.count + 1

    #     if self.count == 5:
    #         self.toolbar.EnableTool(wx.ID_REDO, False)

    #     if self.count == 2:
    #         self.toolbar.EnableTool(wx.ID_UNDO, True)


    def OnQuit(self, e):
        self.Close()

    def OpenNetwork(self, e):
        """Importation d'un réseau 0D sur base d'un fichier .vecz"""

        #Recherche du fichier .vecz(structure géométrique) dans les dossiers de l'utilisateur

        dlg = wx.DirDialog(self, _("Choose the Network directory"))

        if dlg.ShowModal() == wx.ID_OK:

            #Ajout d'éléments supplémentaires de menu liés à la mise en place d'un réseau 0D
            #Menu d'ajout d'éléments
            if(not(self.Network0D)):
                self.Menu_Network()
            Test=1
            if Test==1:
                #Obtention du chemin d'accès
                mainpath=dlg.GetPath()
                self.mainpath=mainpath
                #namepath='D:\\ProgThomas\\wolf_oo\\Sources-Thomas3\\Solutions\\Unit_Tests\\to_debug\\Network_Valve\\Network_Vectors.vecz'
                #Lecture du fichier en vue d'obtenir une structure d'objet (via dictionnaires + listes) de type "Zones"
                #Première étape est de vérifier que le dossier contient bien le fichier .vecz attendu
                vecpath=mainpath+'\\Network_Vectors.vecz'
                self.Zones=Import_vecz(vecpath)
                logging.info(_('-The graph of the network is included'))
                self.NewNetwork=False
                self.Saved_Network=True
                if(self.Zones!=False):
                    #Evènements liés à l'obtention d'informations sur le noeud ou lignée identifiée via un clic
                    #self=self.canvas.mpl_connect('button_press_event', self.OnClick)
                    #Préparation des capacité externes liées à la manipulation de l'affichage
                    self.Add_Properties()
                    #Sous-routine pour extraire l'ensemble des numéros de vecteur et de noeuds
                    #Création du réseau afin de l'afficher en rendant comme résultat les éléments d'une structure OpenGL
                    TTTime=[0.0,0.0,0.0,0.0,0.0,0.0,0.0]
                    start = time.time()
                    #Edg_OGL reprend les différents éléments connecteurs du réseau, avec système de colonnes
                    #Premières donnes reprennent numéro des noeuds connectés,seconde numéroaiton, 3ème nombre d'éléments par zone et 4 appartenance à une zone particulière
                    #Cinquième indique si l'élément spécial doit être affiché avec couleur différente
                    self.Network,self.Edition_Mode,self.List_Nodes_OGL,self.Edg_OGL=Create_Network(self.Zones)
                    self.Modif_Edges=True
                    self.Modif_Nodes=True
                    logging.info(_('-List of nodes and edges in the network are identified'))
                    end  = time.time()
                    TTTime[0]=end-start
                    title_frame=_('Network 0D')
                    #Affichage du réseau
                    start = time.time()
                    self.Show_Network()
                    end  = time.time()
                    TTTime[1]=end-start
                    #On importe à présent l'ensemble des paramètres venant des différents sous-dossiers ou paramètres généraux de résolution
                    start = time.time()
                    self.Param=self.Import_General_Parameters(mainpath)
                    self.Patterns=Import_Patterns(mainpath)
                    #Paramètres généraux dans le menu à ajouter
                    self.General_Parameters_Menu()
                    logging.info(_('-General Parameters of the network are included'))
                    #Patterns dans le menu à ajouter
                    self.Patterns_Exchange_Menu()
                    logging.info(_('-Patterns of the network are included'))
                    end  = time.time()
                    TTTime[2]=end-start
                    #Pompes dans le menu à ajouter
                    start = time.time()
                    self.Patterns_Pumps_Menu()
                    end  = time.time()
                    TTTime[3]=end-start
                    start = time.time()
                    Type_Analysis=1
                    self.Nodes,AttrNode,ListedAttr,DftAttrNode,FoundAttr=Import_Nodes_Attributes(mainpath,self.List_Nodes_OGL,self.Param,Type_Analysis)
                    logging.info(_('-Nodes attributes are included'))
                    end  = time.time()
                    TTTime[4]=end-start
                    start = time.time()
                    self.Zones=Import_Vector_Attributes(mainpath,self.Zones,self.Param,self.List_Nodes_OGL)
                    logging.info(_('-Vectors attributes are included'))
                    end  = time.time()
                    TTTime[5]=end-start
                    start = time.time()
                    self.Zones,self.Nodes=Add_Main_Attributes(self.Zones,self.Nodes)
                    end  = time.time()
                    TTTime[6]=end-start
                t=1
            dlg.Destroy()

    def Menu_Network(self):
        """  Sous-routine permettant la mise en place des différents menus utiles pour la manipulation d'un réseau """
        AddMenu = wx.Menu()
        self.Network0D=True
        NewNode=AddMenu.Append(wx.ID_ANY, _('&New Node'))
        NewEdge=AddMenu.Append(wx.ID_ANY, _('&New Edge'))
        NewPattern=AddMenu.Append(wx.ID_ANY, _('&New Pattern'))
        AddMenu.AppendSeparator()
        Edition=AddMenu.Append(30, _('&Activate Edit Network'))
        self.menubar.Append(AddMenu, _('&New Element'))
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU, self.Node_To_add, NewNode)
        self.Bind(wx.EVT_MENU, self.Edge_To_add, NewEdge)
        self.Bind(wx.EVT_MENU, self.Pattern_To_add, NewPattern)
        self.Bind(wx.EVT_MENU, self.Edition_Evaluation, Edition)
        #Menu pour accéder à des informations générales sur le réseau : trouver et identifier éléments avec certaines caractéristiques
        ResearchMenu = wx.Menu()
        self.menubar.Append(ResearchMenu, _('&General'))
        self.SetMenuBar(self.menubar)
        Element=ResearchMenu.Append(wx.ID_ANY, _('&Trouver Element'))
        Recherche=ResearchMenu.Append(wx.ID_ANY, _('&Rechercher Element'))
        #Revoir exactement ce qui était recherché avec tous ces éléments
        #Special=ResearchMenu.Append(wx.ID_ANY, '&Show special Data')
        self.Bind(wx.EVT_MENU, self.Find_Spec_Elem, Element)
        self.Bind(wx.EVT_MENU, self.Edge_To_add, Recherche)
        #self.Bind(wx.EVT_MENU, self.Show_Spec_Elem, Special)
        #Menu permettant de comparer selon méthode d'aggrégation de la demande le pourcentage lié aux méthodes comparées
        #Special2=ResearchMenu.Append(wx.ID_ANY, '&Compare Agreg. Method.')
        #self.Bind(wx.EVT_MENU, self.Show_Spec_Elem, Special2)
        #self.SpecCases=[Special.Id,Special2.Id]
        #Sous-Menu réalisé afin de faire des phases de zoom
        ResearchMenu.AppendSeparator()
        ZoomELem=ResearchMenu.Append(wx.ID_ANY, _('&Zoom'))
        self.Bind(wx.EVT_MENU, self.Zoom_Elem, ZoomELem)
        PauseZoomELem=ResearchMenu.Append(wx.ID_ANY, _('&Pause Zoom'))
        self.Bind(wx.EVT_MENU, self.PauseZoom_Elem, PauseZoomELem)
        IDPause=self.menubar.FindMenuItem(_('General'),_('Pause Zoom'))
        self.menubar.Enable(IDPause,False)

    def ImportEPanet(self, e):
        """Ouverture de fichier ".vecz" """
        dlg = wx.FileDialog(self,_("Choose .inp file"), wildcard="inp (*.inp)|*.inp|all (*.*)|*.*")
        if dlg.ShowModal() == wx.ID_OK:
            namepath=dlg.GetPath()
            t=1
        dlg.Destroy()

    def OnOpen(self, e):
        """Obtention du patch menant au fichier ".vecz" pour obtenir fichier "zones" """
        dlg = wx.FileDialog(self, _("Choose the .vecz file"),
                           defaultDir = "",
                           defaultFile = "",
                           wildcard = "*")
        if dlg.ShowModal() == wx.ID_OK:
            namepath=dlg.GetPath()
            t=1
        dlg.Destroy()

    def on_new_frame(self, event):
        """Ouverture d'une fenêtre supplémentaire"""
        title = 'New Network'
        #Première phase : définir nom du réseau et dossier de création
        self.NetworkName,mainpath=self.Import_Directory()
        self.Zones=[]
        self.Network,self.Edition_Mode,self.List_Nodes_OGL,self.Edg_OGL=Create_Network(self.Zones)
        self.Modif_Edges=True
        self.Modif_Nodes=True
        self.Zones=Init_Zones()
        self.Add_Properties()
        self.Param=self.Import_General_Parameters(mainpath)

        self.Initialise_Network()
        self.Zones,self.Nodes=Add_Main_Attributes(self.Zones,self.Nodes)
        self.NewNetwork=True
        self.Saved_Network=False
        self.Menu_Network()
        #Patterns dans le menu à ajouter
        self.General_Parameters_Menu()
        #Patterns dans le menu à ajouter
        self.Patterns=[]
        self.Patterns_Exchange_Menu()
        #Afficher les paramètres directement obtenus afin de les confronter à l'utilisateur
        New_FrameGen=self.Prepare_Network(mainpath)
        New_frame=NewNodeFrame(_('New node in the network'),self)
        r=2
        #New_frame=NewEdgeFrame('New edge in the network',self)
        #self.frame_number += 1


    def Initialise_Network(self):
        """Initialisation des variables du système"""
        self.Nodes={}
        self.Nodes['Reservoirs']={}
        self.Nodes['IncJunctions']={}
        Test=0


    def Assoc_element(self):
        """Procédure utilisée pour identifier le noeud ou vecteur le plus proche d'un clic effectué par l'utilisateur"""
        Index,dist=closest_node(self.LocNode,  self.List_Nodes_OGL['CoordPlan'][:])
        Index2,dist2=closest_node(self.LocNode,  self.List_Nodes_OGL['VecCoord'][:])
        #On va recherche alors les informations auprès de l'élément : noeud ou vecteur
        self.LocalNode=[]
        Type_Node='Vector'
        IndexF=Index2
        if(dist<dist2):
            Type_Node='Node'
            IndexF=Index

        self.LocalNode.append(IndexF)
        Test=1
        if(Type_Node=='Vector'):
            self.Print_VectorData()
        else:
            if(Type_Node=='Node'):
                #On fait une recherche limitée aux noeuds pour extraire informations réellement importantes
                TypeNode=self.List_Nodes_OGL['TypeNode'][Index]
                #NameNode=self.List_Nodes_OGL['PosNode'][Index]

                self.LocalNode=[]
                self.LocalNode.append(Index)
                self.LocalNode.append(TypeNode)
                self.LocalNode.append('NotMyName')
                self.Print_NodeData()

        return Test


    def Node_To_add(self,e):
        """Procédure d'ajout d'un noeud au sein du réseau"""
        Test=1
        #Nouvelle fenêtre s'ouvrant permettant ainsi d'ajouter les coordonnées du noeud
        New_frame=NewNodeFrame('New node in the network',self)
        #

    def Edge_To_add(self,e):
        """Procédure d'ajout d'un Edge au sein du réseau"""
        Test=1
        #Parcours du Graph à faire afin de s'assurer qu'au minimum deux noeuds sont bien présents au sein du réseau
        New_frame=NewEdgeFrame('New edge in the network',self)


    def Pattern_To_add(self,e):
        """Procédure d'ajout d'un Pattern au sein du réseau"""
        Test=1
        #Nouvelle fenêtre permettant d'à la fois
        #New_Pattern=NewPatternFrame('New pattern in the network',self)
        dia = MyDialog(self, -1, 'Add new patterns (Quit to activate your choices)')
        dia.ShowModal()
        dia.Destroy()


    def Edition_Evaluation(self,e):
        """Mise à jour des variables d'édition notamment pour arrêter ou commencer la phase d'édition du réseau"""
        self.First_Node=[]
        self.Last_Node=[]
        if(self.Edition_Mode):
            self.Edition_Mode=False
            Test=1
            self.menubar.SetLabel(30,'&Activate Edit Network')
            self.menubar.Refresh()
            #La fin de la partie d'édition devrait s'accompagner d'une recharge effective du réseau afin de l'afficher également
            #Une recharge du réseau devrait d'ailleurs se faire après l'ajout de tout noeud/liaison
            Test=1
        else:
            self.Edition_Mode=True
            Test=1
            self.menubar.SetLabel(30,'&DEactivate Edit Network')
            self.menubar.Refresh()
            Test=1


    def Network_To_Show(self):
        """Mise en place d'une procédure uniquement dédiée à initier la représentation du réseau   """
        self.Show_Network()

    def onMotion(self, evt):
        """This is a bind event for the mouse moving on the MatPlotLib graph
            screen. It will give the x,y coordinates of the mouse pointer.
        """
        xdata = evt.xdata
        ydata = evt.ydata
        try:
            x = round(xdata,4)
            y = round(ydata,4)
        except:
            x = ""
            y = ""

        self.Text.SetLabelText("x : %s ,y: %s" % (x,y))


    def Print_VectorData(self):
        """Sous-routine utilisée pour ouvrir une nouvelle fenêtre locale via un clic gauche afin d'afficher les informations du vecteur sélectionné"""
        #Ouverture d'une nouvelle fenêtre
        #On va rechercher les informations sur le vecteur ainsi identifié
        Index=int(self.LocalNode[0])
        NumZone=int(self.List_Nodes_OGL['IdZone'][Index])
        NumVec=self.List_Nodes_OGL['NbrElVec'][Index]
        PosVec=self.List_Nodes_OGL['PosVec'][Index]
        self.Edg_OGL[4]=[0]*len(self.Edg_OGL[4])
        self.Edg_OGL[4][PosVec]=1
        VecName=self.Zones[NumZone]['Name'][NumVec]
        title = 'Vector ID: '+VecName
        frame = Mywin(parent=self,title=title,MainW=self,Type_Element=0)


    def Print_NodeData(self):
        """Sous-routine utilisée pour ouvrir une nouvelle fenêtre locale via un clic gauche afin d'afficher les informations du noeud sélectionné"""
        #Ouverture d'une nouvelle fenêtre
        #On va rechercher les informations sur le vecteur ainsi identifié
        Index=int(self.LocalNode[0])
        NumVec=self.List_Nodes_OGL['NbrEl'][Index]
        NodeName=self.List_Nodes_OGL['NameNode'][Index]
        Test=Add_Pattern_Dft_Value(self.Nodes)
        self.LocalNode[2]=NodeName
        #Affichage mis en valeur du noeud identifié
        self.List_Nodes_OGL['SpecNode']=[0]*len(self.List_Nodes_OGL['SpecNode'])
        self.List_Nodes_OGL['SpecNode'][Index]=1
        title = 'Node ID: '+NodeName
        frame = Mywin(parent=self,title=title,MainW=self,Type_Element=1)


    def Import_Directory(self):
        """On vient demander à l'utilisateur de fournir le fichier principal de son réseau, dans laquel il souhaite sauvegarder celui-ci potentiellement"""
        dlg = wx.DirDialog(self, "Choose the Network directory")
        result=dlg.ShowModal()
        if result == wx.ID_OK:
            Directory = dlg.GetPath()
        else:
            Directory='D:\\'
            Message="The default directory is the following :"+Directory
            logging.info(Message)
        dlg.Destroy()
        Name='Test_Network'
        return Name,Directory


    def Prepare_Network(self,pathname):
        """On vient écrire dans le dossier remis par l'utilisateur les paramètres afin de les afficher à l'écran pour éventuellement les modifier via l'utilisateur"""
        #Partie exportation des fichiers principaux généraux
        IERR=General_Parameters(self.Param, pathname)
        self.ParamFile=pathname+'\\General_Network.param'
        self.GeneralParam = Wolf_Param(self, filename=self.ParamFile)
        Test=1


    def Import_General_Parameters(self,namepath):
        """On va recherche les différents paramètres généraux utiles de la simulation selon leur catégorie afin de former un dictionnaire"""
        #Dossier Principal
        #MainDir = os.path.dirname(namepath)
        MainDir = namepath+'\\'
        Param={}
        #Fichier habituel
        ParamFile=MainDir+'General_Network.param'
        #On vérifie que le fichier est bien présent
        File_To_Read=os.path.isfile(ParamFile)
        Default_Param=False
        if(File_To_Read):
            self.GeneralParam=Wolf_Param(self,filename=ParamFile, toShow=False, DestroyAtClosing=False)
            Param = Read_Param_file(ParamFile)
        else:
            dlg = wx.MessageDialog(
                None, "No general parameters found. Used default parameters ?", "Default parameters", wx.YES_NO | wx.CENTRE
            )
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                #On applique les paramètres génériques
                ParamFile=MainDir+'General_Network.param.default'
                File_To_Read=os.path.isfile(ParamFile)
                if(File_To_Read):
                    #Procédure identique à faire via le fichier param.default
                    #Il faut introduire à la main les différents paramètres ... A compléter
                    Test=1
                    Param=Read_Param_file(ParamFile)
                else:
                    Default_Param=True
                    logging.info('Default parameters Used')
                     #Il faut introduire à la main les différents paramètres ... A compléter
                    Test=2
            else:
                Default_Param=True


            if (Default_Param):
                Category_Name=['Time','General Parameters of the network','Simulation Parameters','IPOPT Optimization Parameters']
                Param[Category_Name[0]]={}
                Param[Category_Name[1]]={}
                Param[Category_Name[2]]={}
                Param[Category_Name[3]]={}
                Param['General Parameters of the network']['Roughness Law']=['2','Used roughness law in the network for pipes (integer)']
                Param['General Parameters of the network']['Roughness Law Valves']=['2','Used roughness law in the network for valves (integer)']
                Param['General Parameters of the network']['Presence of leakages']=['0','The leakages will create water losses at the nodes of the network (integer)']
                Param['General Parameters of the network']['Effect of Inertia']=['0','The inertia effects are applied to pipes and valves (integer)']
                Param['Time']['Time step']=['3.6000000000000000E+03','Time between two time steps (double)']
                Param['Time']['Maximum time step allowed']=['3.6000000000000000E+03','Maximum time allowef for time step (double)']
                Param['Time']['Maximum time']=['3.6000000000000000E+04','Time of simulation in seconds (double)']
                Param['Time']['Time between each saved configuration']=['3.6000000000000000E+03','Chosen time between each configuration (double)']
                Param['Time']['Type of time network evaluation']=['10','The network can be evaluated thanks to simulated or optimized resolution (integer)']
                Param['Time']['Number of time used steps']=['72','The number of time steps which are really used for the network for each element in the network (integer)']
                Param['Time']['Number of time save steps']=['72','The maximum number of time steps which can be saved for the network for each element in the network. Il faut au minimum Total_Div_Time (integer)']
                Param['Time']['Saved time steps']=['1','The values obtained at each time steps are saved (integer)']
                Param['Simulation Parameters']['Number Iterations']=['200','Number of iterations before a reset of the current time step (integer)']
                Param['IPOPT Optimization Parameters']['Associated_Opt_Problem']=['1','Network evaluated by IPOPT optimization (integer)']
                Param_A=['Name_Linear_Solver','Used_mu_param_Strategy','Nbr_Max_Iterations_Allowed','Dual_Tol_Threshold_Objective','Primal_Tol_Threshold_Objective']
                Param_B=['Global_Tol_Threshold_Objective','Accept_Dual_Tol_Threshold_Objective','Accept_Primal_Tol_Threshold_Objective','Accept_Global_Tol_Threshold_Objective']
                Param_C=['Writed_Results_Ipopt','Choice_Time']
                Param_Ipopt=Param_A+Param_B+Param_C
                Val_Dft=['ma27','monotone','3000','1.0000000000000001E-09','1.0000000000000001E-09','1.0000000000000001E-09','1.0000000000000000E-08','1.0000000000000000E-09','1.0000000000000000E-08','0','0','0']
                Comments_A=['Linear solver used to solve the network','Strategy which is used to evaluate during iterations the value of the barrier parameter','Maximum allowed number of iterations to find an acceptable level of resolution (integer)','Allowed dual violation of the constraints for the absolute tolerance (double)']
                Comments_B=['Allowed primal violation of the constraints for the absolute tolerance (double)','Allowed absolute tolerance (double)','Allowed acceptable dual violation of the constraints for the tolerance (double)']
                Comments_C=['Allowed acceptable primal violation of the constraints for the tolerance (double)','Allowed acceptable tolerance (double)','Writed Results (integer)','Chosen type of resolution']
                Comments_Ipopt=Comments_A+Comments_B+Comments_C
                for i in range(len(Param_Ipopt)):
                    Param['IPOPT Optimization Parameters'][Param_Ipopt[i]]=[Val_Dft[i],Comments_Ipopt[i]]
                Test=1
        return Param


    def Update_Param(self):
        """Mise-à-jour des paramètres sur base de la sauvegarde du fichier de paramètres"""
        ParFrame=self.GeneralParam
        for group in ParFrame.myparams.keys():
            for param_name in ParFrame.myparams[group].keys():
                self.Param[group][param_name]=ParFrame.myparams[group][param_name][key_Param.VALUE]
                Test=1
        Test=1

    def Select_Node(self,LocNode,List_Nodes):
        #Choix à faire du premier ou second noeud de l'Edge : on vient donc associer selon les coordonnées du noeud, celui qui est le plus proche
        #Loc_Node,dis=closest_node(LocNode, Discr_Nodes['Coord'][:])
        Ind_Node,dis=closest_node(LocNode, List_Nodes['CoordPlan'][:])
        #Ind_Node,dis=closest_node(Discr_Nodes['Coord'][Loc_Node], List_Nodes['CoordPlan'][:])
        Ind_Node=Ind_Node+1
        if(bool(self.First_Node)):
            #Cela signifie qu'il faut donc bien remplir le deuxième noeud de la nouvelle liaison à ajouter
            self.Last_Node.append(Ind_Node)
            FNode=self.First_Node[0]
            LNode=self.Last_Node[0]
            self.Ident_Nodes=[self.List_Nodes_OGL['NameNode'][FNode-1],self.List_Nodes_OGL['NameNode'][LNode-1]]
            New_frame=NewEdgeFrame('New edge in the network',self)
            self.Ident_Nodes=[]
            #Link=(FNode,LNode)
            #NbPipes=self.Edg_OGL[2][0]
            #NbPipes=NbPipes+1
            #self.Edg_OGL[2][0]=NbPipes
            #self.Edg_OGL[0].append(Link)
            #self.Edg_OGL[1].append(NbPipes)
            #self.Edg_OGL[3].append(0)
            #self.Edg_OGL[4].append(0)

            self.First_Node=[]
            self.Last_Node=[]
            if(hasattr(self,'loc_new_edge')):
                self.loc_new_edge='X'
        else:
            #Premier Noeud qu'il faut remplir
            self.First_Node.append(Ind_Node)
            if(bool(self.First_Node) and bool(self.Last_Node)):
                #Cela ne peut se produire que s'il y a une intervention manuelle infructueuse de l'utilisateur
                Nb_edges=len(self.Graph.edges)
                FNode=self.First_Node[0]
                LNode=self.Last_Node[0]
                Link=(FNode,LNode)
                self.Edg_OGL[0].append(Link)
                self.Edg_OGL[1].append(Link)
                self.Edg_OGL[3].append(0)
                self.Edg_OGL[4].append(0)
                self.Modif_Edges=True
                self.First_Node=[]
                self.Last_Node=[]
        Test=1


    def Show_Network(self):
        """Sous-routine spécifique dédiée à l'affichage du réseau"""
        self.Centre()
        frame_sizer = wx.BoxSizer(wx.VERTICAL)

        #Partie Figure
        if(hasattr(self,'canvas2')):
            self.canvas2.Destroy()
        if(hasattr(self,'canvas')):
            self.canvas.Destroy()
        self.canvas2 = CubeCanvas(self)
        self.canvas2.Refresh()
        frame_sizer.Add(self.canvas2, 1, wx.EXPAND)
        if(hasattr(self,'Show_Results')):
            if(bool(self.Show_Results)):
                Bar_Name=['HeadNodes[m]','Altimetry[m]','Discharge[m³/s]','Diameter[m]']
                Nb_Colorbar=0
                if(self.Show_Results[0]>0):
                    Norm_Bars=[[self.ExtrVectors[0]],[self.ExtrVectors[1]]]
                    if(self.Show_Results[1]>0):
                        Nb_Colorbar=2
                        Norm_Bars[0].append(self.ExtrNodes[0])
                        Norm_Bars[1].append(self.ExtrNodes[1])
                    else:
                        Nb_Colorbar=1
                else:
                    if(self.Show_Results[1]>0):
                        Nb_Colorbar=1
                        Norm_Bars=[[self.ExtrNodes[0]],[self.ExtrNodes[1]]]
                #Partie Colorbar
                #Evaluation du nom à choisir
                Bar_Nam=[]
                for i in range(len(Bar_Name)):
                    if(self.Param_Simul[i]==1):
                        Bar_Nam.append(Bar_Name[i])
                for i in range(Nb_Colorbar):
                    self.figure, ax = plt.subplots(figsize=(4, 0.5))
                    self.figure.subplots_adjust(bottom=0.8)

                    cmap = mpl.cm.RdYlGn
                    #Frame_loc.ExtrNodes,Frame_loc.ExtrVectors
                    norm = mpl.colors.Normalize(vmin=Norm_Bars[0][i], vmax=Norm_Bars[1][i])

                    self.figure.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                                    cax=ax, orientation='horizontal', label=Bar_Nam[i])

                    self.canvas = FigureCanvas(self, -1, self.figure)
                    self.canvas.Refresh()

                    frame_sizer.Add(self.canvas, 0,  wx.EXPAND)


        self.SetSizer(frame_sizer)
        Test=1
        #self.Fit()


    def Gen_Param_To_show(self,e):
        """Sous-routine pour l'ouverture d'une frame permettant d'illustrer les paramètres généraux de résolution du système"""
        if self.GeneralParam is not None:
            self.GeneralParam.Show()

        # #New_frame=GenParamFrame('Used parameters in the network',self)
        # ParamFile=join(self.mainpath, 'General_Network.param')
        # self.GeneralParam=Wolf_Param(self,filename=ParamFile)


    def General_Parameters_Menu(self):
        """Menu permettant d'accéder au contenu des paramètres généraux du dossier afin de réaliser comment est construit le réseau"""
        AddMenu = wx.Menu()
        self.menubar.Append(AddMenu, '&General Parameters')
        self.SetMenuBar(self.menubar)
        MenuName='Show'
        General_Download=AddMenu.Append(wx.ID_ANY, MenuName)
        self.Bind(wx.EVT_MENU, self.Gen_Param_To_show, General_Download)


    def Pattern_To_show(self,e):
        """Affichage du Pattern sous format de Tableau + possibilité affichage graphique Matplotlib"""
        Test=1
        #Nouvelle fenêtre s'ouvrant permettant ainsi d'ajouter les coordonnées du noeud
        self.IDLocPattern = e.GetId()
        New_frame=NewPatternFrame('Used pattern in the network',self)
        test=1


    def Patterns_Exchange_Menu(self):
        """Mise en place des Menus de Pattern"""

        AddMenu = wx.Menu()
        NewNode=[]
        i=0
        self.PatternName=[]
        for Name in self.Patterns:
            MenuName='&'+Name
            self.PatternName.append(Name)
            NewNode.append([])
            NewNode[i]=AddMenu.Append(wx.ID_ANY, MenuName)
            i=i+1
            #AddMenu.AppendSeparator()
        self.menubar.Append(AddMenu, '&Patterns')
        self.SetMenuBar(self.menubar)
        self.IDPattern=[]
        for i in range(len(self.Patterns)):
            self.IDPattern.append(NewNode[i].Id)
            self.Bind(wx.EVT_MENU, self.Pattern_To_show, NewNode[i])

        Test=1


    def Patterns_Pumps_Menu(self):
        """Mise en place des Menus de Pattern"""

        AddMenu = wx.Menu()
        NewNode=[]
        i=0
        #On vérifie en premier lieu s'il y a évidemment des pompes dans le réseau
        NbVectors=self.Zones[1]['NbrVec']
        if(bool(NbVectors)):
            for Name in self.Zones[1]['Name']:
                MenuName='&'+Name
                NewNode.append([])
                NewNode[i]=AddMenu.Append(wx.ID_ANY, MenuName)
                i=i+1
                #AddMenu.AppendSeparator()
            self.menubar.Append(AddMenu, '&Pumps')
            self.SetMenuBar(self.menubar)
            self.IDPump=[]
            for i in range(len(self.Zones[1]['Name'])):
                self.IDPump.append(NewNode[i].Id)
                self.Bind(wx.EVT_MENU, self.Pump_To_show, NewNode[i])

        Test=1


    def Pump_To_show(self,e):
        """Affichage du Pattern sous format de Tableau + possibilité affichage graphique Matplotlib"""
        Test=1
        #Nouvelle fenêtre s'ouvrant permettant ainsi d'ajouter les coordonnées du noeud
        self.IDLocPump = e.GetId()
        New_frame=NewPumpFrame('Used pump in the network',self)

        test=1


    def SaveNetwork(self,e):
        """Procedure d'écriture des différents fichiers du réseau implémenté pour sauvegarder modifications ou exécuter simulation"""
        #Première étape liée au choix du dossier où le nouveau dossier réseau est placé ainsi que le nom de ce dossier réseau
        test=1
        with wx.DirDialog(self, "Select Save directory (Create it if needed)") as dirDialog:

            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = dirDialog.GetPath()

        #Vérification prélable qu'un réseau 0D a bien été chargé
        if(hasattr(self,'Zones')):
            self.Saved_Network=True
            #Partie exportation du fichier .vecz.
            file_zone=pathname+'\\Network_Vectors.vecz'
            IERR=Export_vecz(self.Zones,file_zone)
            #Partie exportation des coordonnées des noeuds
            IERR=Export_vecr(self.Nodes,pathname)
            #Partie exportation des différents attributs de vecteurs
            IERR=Export_Vec_Attributes(self.Zones,self.Param,pathname)
            #Partie exportation des différents attributs de noeuds
            IERR=Export_Node_Attributes(self.Nodes,pathname)
            #Partie exportation des fichiers principaux généraux
            IERR=General_Parameters(self.Param,pathname)
            #Partie exportation des patterns
            IERR=Export_Patterns(self.Patterns,pathname)
        else:
            #Problème de format proposé par l'utilisateur, un évènement doit être appelé
            dlg = wx.MessageDialog(
                None, "No valid network to save", "Incorrect request", wx.YES_NO | wx.CANCEL | wx.CENTRE
            )
            result = dlg.ShowModal()
            dlg.Destroy()

        self.mainpath=pathname
        return pathname


    def Find_Spec_Elem(self,e):
        """Evènement permettant d'identifier la position immédiate d'un noeud ou d'une canalisation sur base de son nom"""
        #Nouvelle fenêtre s'ouvrant permettant ainsi d'ajouter le nom de l'élément ainsi que le type d'élément à rechercher
        New_frame=IdElementFrame('Researched element in the network',self)


    def Show_Spec_Elem(self,e):
        """Sous-routine destinée à aller chercher les informations paramétriques disponibles pour étudier l'influence des paramètres sur indicateur de réseau"""
        #Première étape est de demander à l'utilisateur de fournir nom de fichier où trouver l'étude paramétrique du réseau
        #dlg = wx.FileDialog(self,"Choose .vpar file", wildcard="vpar (*.vpar)|*.vpar|all (*.*)|*.*")
        Case_Message=['Choose the param file','Choose the comparison file']
        Case_Test=[0,1]
        self.IDSpecialCase = e.GetId()
        IDCase=e.GetId()
        for i in range(len(self.SpecCases)):
            if(self.SpecCases[i]==IDCase):
                Message=Case_Message[i]
                Case=Case_Test[i]
        dlg = wx.FileDialog(self,Message)
        Test=0
        Ident_Types=['Reservoirs','IncJunctions']
        if dlg.ShowModal() == wx.ID_OK:
            namepath=dlg.GetPath()
            Test=1
        dlg.Destroy()
        if(Test==1):
            if(not(hasattr(self,'cptParam'))):
                #Deuxième étape est de récupérer les informations pour les Noeuds
                #Chaque liste commence par "New_Param"
                File_To_Read=os.path.isfile(namepath)
                cptParam=-1
                NewParam='New_Param'
                IdParam='Params'
                for TypeNode in Ident_Types:
                    for NameNode in self.Nodes[TypeNode]:
                        self.Nodes[TypeNode][NameNode][IdParam]=[]
                if(File_To_Read):
                    with open(namepath) as f:
                        content = f.readlines()
                    content = [x.rstrip('\n') for x in content]
                    for NewLine in content:
                        NewLine=NewLine.lstrip()
                        if(NewLine==NewParam):
                            cptParam +=1
                        else:
                            #On doit déconstruire la ligne pour accéder au nom de la chambre et donc à la valeur de l'indice
                            New_Word=re.split(r'\,', NewLine)
                            if(len(New_Word)==2):
                                for TypeNode in Ident_Types:
                                    if(New_Word[0] in self.Nodes[TypeNode]):
                                        self.Nodes[TypeNode][New_Word[0]][IdParam].append(float(New_Word[1]))
                            else:
                                #Un autre critère peut également être un espace
                                New_Word= NewLine.split()
                                if(len(New_Word)==2 and Case==0):
                                    for TypeNode in Ident_Types:
                                        if(New_Word[0] in self.Nodes[TypeNode]):
                                            self.Nodes[TypeNode][New_Word[0]][IdParam].append(float(New_Word[1]))
                                else:
                                    if(len(New_Word)==4 and Case==1):
                                        for TypeNode in Ident_Types:
                                            if(New_Word[0] in self.Nodes[TypeNode]):
                                                self.Nodes[TypeNode][New_Word[0]][IdParam].append(float(New_Word[1]))
                                                self.Nodes[TypeNode][New_Word[0]][IdParam].append(float(New_Word[2]))
                                                self.Nodes[TypeNode][New_Word[0]][IdParam].append(float(New_Word[3]))
                self.cptParam=cptParam+1
                self.Nodes['ActivParams']=[0]*(self.cptParam)
        #Ouverture vers une nouvelle fenêtre pour savoir ce que l'utilisateur souhaite voir comme paramètres sur le dessin via check-list (possibilité de choisir lesquels sont montrés
        self.ShowSpecCase=Case
        if(Case==0):
            New_frame=ParamToShow(self,'Parameters to show')
        else:
            self.Show_Param_Clients=True


    def analyse_params(self):
        """Analyse de tous les paramètres présents """
        Test_Node=2
        Test_Vector=0
        Sizes=[1.0,10.0]
        MaxAbs=0.0
        MinAbs=10000000.0
        Activ='ActivParams'
        TypeNodes=['Reservoirs','IncJunctions']
        #Initialisation palette de couleurs si nécessaire
        if(not(hasattr(self,'mypalo'))):
            self.mypalo=wolfpalette(None,"Palette of colors")
            self.mypalo.nb,self.mypalo.values,self.mypalo._segmentdata,self.mypalo.colorsflt=self.mypalo.export_palette_matplotlib('RdYlGn')
        #Une direction de lecture, une sur la taille des cercles montrant l'importance relative d'un paramètre tandis que la couleur sera unique par paramètre pour les distinguer
        #Etape d'initiation est d'identifier le nombre de paramètres actifs et de paramétriser la couleur
        cpt_activ_param=0
        for ActivNodes in self.Nodes[Activ]:
            if(ActivNodes==1):
                cpt_activ_param += 1
        Tot_param=float(cpt_activ_param)
        No_color=[0.0,0.0,0.0,0.0]
        cpt_activ_param=0
        cpt_param=0
        Loc_Param_Color=[]
        for ActivNodes in self.Nodes[Activ]:
            if(ActivNodes==1):
                if(Tot_param>1.0):
                    Loc=0.0+(float(cpt_activ_param))/(Tot_param-1.0)
                else:
                    Loc=0.0
                Loc_Color=self.mypalo.lookupcolorflt(Loc)
                Loc_Param_Color.append(Loc_Color)
                cpt_activ_param += 1
            else:
                Loc_Param_Color.append(No_color)
            cpt_param+=1
        #Première étape est de récupérer informations utiles selon paramètres actifs
        ListParams=[]
        for TypeNode in TypeNodes:
            for NameNode in self.Nodes[TypeNode]:
                if(NameNode=='MA007'):
                    Test=1
                if(not(hasattr(self.Nodes[TypeNode][NameNode],'SizeAffich'))):
                    self.Nodes[TypeNode][NameNode]['SizeAffich']=[0.0]*len(self.Nodes[TypeNode][NameNode]['Params'])
                cpt_el=0
                SumParam=0.0
                for ActivNodes in self.Nodes[Activ]:
                    if(ActivNodes==1):
                        #ListParams.append(self.Nodes[TypeNode][NameNode]['Params'][cpt_el])
                        if(bool(self.Nodes[TypeNode][NameNode]['Params'])):
                            SumParam += float(self.Nodes[TypeNode][NameNode]['Params'][cpt_el])
                    cpt_el += 1
                ListParams.append(SumParam)
                if(SumParam>MaxAbs):
                    MaxAbs=SumParam
                if(SumParam<MinAbs):
                    MinAbs=SumParam
        DiffExtr=MaxAbs-MinAbs
        Pente=(Sizes[1]-Sizes[0])/(MaxAbs-MinAbs)
        Coeff=Sizes[1]-Pente*MaxAbs
        Param_Color=[]
        #On a les valeurs extrêmes : il faut donc évaluer pour chaque cercle sa taille d'affichage
        cpt_elem=0
        for TypeNode in TypeNodes:
            for NameNode in self.Nodes[TypeNode]:
                Val=ListParams[cpt_elem]/MaxAbs
                if(Val>0.98):
                    Test=1
                self.Nodes[TypeNode][NameNode]['Radius']=Val
                if(bool(self.Nodes[TypeNode][NameNode]['Params'])):
                    self.Nodes[TypeNode][NameNode]['Part_Params']=[0.0]*len(self.Nodes[TypeNode][NameNode]['Params'])
                else:
                    self.Nodes[TypeNode][NameNode]['Part_Params']=1.0
                cpt_param = 0
                for Param in self.Nodes[TypeNode][NameNode]['Params']:
                    if(self.Nodes[Activ][cpt_param]==1):
                        if(bool(self.Nodes[TypeNode][NameNode]['Params']) and ListParams[cpt_elem]>0.0):
                            self.Nodes[TypeNode][NameNode]['Part_Params'][cpt_param]=self.Nodes[TypeNode][NameNode]['Params'][cpt_param]/ListParams[cpt_elem]
                        else:
                            self.Nodes[TypeNode][NameNode]['Part_Params'][cpt_param]=0.0
                        self.Nodes[TypeNode][NameNode]['SizeAffich'][cpt_param]=Pente*Param+Coeff
                    cpt_param += 1
                cpt_elem += 1
        return Test_Node,Test_Vector,Loc_Param_Color


    def analyse_params_Clients(self):
        """Analyse de tous les paramètres présents pour évaluer la présence et proportions de clients selon chaque méthode d'aggrégation"""
        Test_Node=2
        Test_Vector=0
        Sizes=[1.0,10.0]
        MaxAbs=0.0
        MinAbs=10000000.0
        Activ='ActivParams'
        TypeNodes=['Reservoirs','IncJunctions']
        #Initialisation palette de couleurs si nécessaire
        if(not(hasattr(self,'mypalo'))):
            self.mypalo=wolfpalette(None,"Palette of colors")
            self.mypalo.nb,self.mypalo.values,self.mypalo._segmentdata,self.mypalo.colorsflt=self.mypalo.export_palette_matplotlib('RdYlGn')
        #Une direction de lecture, une sur la taille des cercles montrant l'importance relative d'un paramètre tandis que la couleur sera unique par paramètre pour les distinguer
        #Etape d'initiation est d'initialiser le nombre de paramètres et le couleur des cercles

        cpt_activ_param=3
        Tot_param=float(cpt_activ_param)
        No_color=[0.0,0.0,0.0,0.0]
        cpt_activ_param=0
        cpt_param=0
        self.Nodes[Activ]=[1,1,1]
        Loc_Param_Color=[]
        for ActivNodes in self.Nodes[Activ]:
            if(ActivNodes==1):
                if(Tot_param>1.0):
                    Loc=0.0+(float(cpt_activ_param))/(Tot_param-1.0)
                else:
                    Loc=0.0
                Loc_Color=self.mypalo.lookupcolorflt(Loc)
                Loc_Param_Color.append(Loc_Color)
                cpt_activ_param += 1
            else:
                Loc_Param_Color.append(No_color)
            cpt_param+=1
        #Première étape est de récupérer informations utiles selon paramètres actifs
        ListParams=[]
        ListParams2=[]
        for TypeNode in TypeNodes:
            for NameNode in self.Nodes[TypeNode]:
                if(NameNode=='MA007'):
                    Test=1
                cpt_el=0
                SumParam=0.0
                MaxLoc=0.0
                for ActivNodes in self.Nodes[Activ]:
                    if(ActivNodes==1):
                        if(bool(self.Nodes[TypeNode][NameNode]['Params'])):
                            Loc_Val= float(self.Nodes[TypeNode][NameNode]['Params'][cpt_el])
                            if(Loc_Val>MaxAbs):
                                MaxAbs=Loc_Val
                            if(Loc_Val<MinAbs):
                                MinAbs=Loc_Val
                            if(Loc_Val>MaxLoc):
                                MaxLoc=Loc_Val
                            SumParam += float(self.Nodes[TypeNode][NameNode]['Params'][cpt_el])
                    cpt_el += 1
                ListParams.append(SumParam)
                ListParams2.append(MaxLoc)
        DiffExtr=MaxAbs-MinAbs
        Pente=(Sizes[1]-Sizes[0])/(MaxAbs-MinAbs)
        Coeff=Sizes[1]-Pente*MaxAbs
        Param_Color=[]
        #On a les valeurs extrêmes : il faut donc évaluer pour chaque cercle sa taille d'affichage
        cpt_elem=0
        for TypeNode in TypeNodes:
            for NameNode in self.Nodes[TypeNode]:
                Val=ListParams2[cpt_elem]/MaxAbs
                if(Val>0.98):
                    Test=1
                self.Nodes[TypeNode][NameNode]['Radius']=Val
                if(bool(self.Nodes[TypeNode][NameNode]['Params'])):
                    self.Nodes[TypeNode][NameNode]['Part_Params']=[0.0]*len(self.Nodes[TypeNode][NameNode]['Params'])
                else:
                    self.Nodes[TypeNode][NameNode]['Part_Params']=1.0
                cpt_param = 0
                for Param in self.Nodes[TypeNode][NameNode]['Params']:
                    if(self.Nodes[Activ][cpt_param]==1):
                        if(bool(self.Nodes[TypeNode][NameNode]['Params']) and ListParams[cpt_elem]>0.0):
                            self.Nodes[TypeNode][NameNode]['Part_Params'][cpt_param]=self.Nodes[TypeNode][NameNode]['Params'][cpt_param]/ListParams[cpt_elem]
                        else:
                            self.Nodes[TypeNode][NameNode]['Part_Params'][cpt_param]=0.0
                        #self.Nodes[TypeNode][NameNode]['SizeAffich'][cpt_param]=Pente*Param+Coeff
                    cpt_param += 1
                cpt_elem += 1
        return Test_Node,Test_Vector,Loc_Param_Color


    def Add_Properties(self):
        """Sous-routine destinée à initier les capacités de l'affichage (zoom, ...)"""
        self.Zoom=0
        self.NodeZoom=0
        self.ZoomN=[[],[],[],[]]

    def Zoom_Elem(self,e):
        """#Sous-routine permettant d'initialiser la procédure de Zoom consistant à sélectionner les deux coins opposés d'un rectangle pour définir
            #zone de zoom"""
        ZoomName='Zoom'
        ZoomPause='Pause Zoom'
        if(self.Zoom==1):
            ZoomName='End Zoom'
        if(self.Zoom==2):
            ZoomPause='Unpause Zoom'
        IndexItem=self.menubar.FindMenuItem('General',ZoomName)
        IndexItem2=self.menubar.FindMenuItem('General',ZoomPause)
        if(self.Zoom==0):
            self.Zoom=1
            self.menubar.SetLabel(IndexItem,'&End Zoom')
            self.menubar.Enable(IndexItem2,True)
            self.menubar.Refresh()
            #La fin de la partie d'édition devrait s'accompagner d'une recharge effective du réseau afin de l'afficher également
            #Une recharge du réseau devrait d'ailleurs se faire après l'ajout de tout noeud/liaison
            Test=1
        else:
            self.Zoom=0
            self.ZoomN=[[],[],[],[]]
            self.NodeZoom=0
            self.menubar.SetLabel(IndexItem,'&Zoom')
            self.menubar.Enable(IndexItem2,False)
            self.menubar.Refresh()
            Test=1

    def PauseZoom_Elem(self,e):

        ZoomPause='Pause Zoom'
        if(self.Zoom==2):
            ZoomPause='Unpause Zoom'
        IndexItem=self.menubar.FindMenuItem('General',ZoomPause)
        if(self.Zoom!=2):
            self.Zoom=2
            self.menubar.SetLabel(IndexItem,'&Unpause Zoom')
        else:
            self.Zoom=1
            self.menubar.SetLabel(IndexItem,'&Pause Zoom')

        self.canvas2.NewDraw=True
        self.menubar.Refresh()
        Test=1


    def LaunchSimul(self,e):
        """Sous-routine dédiée au lancement d'une simulation en ouvrant notamment une fenêtre qui permet d'identifier le type de simulation voulue par l'utilisateur"""
        #Il faut sauvegarder le réseau si des modifications ont été réalisées ou si le réseau est nouveau
        if(hasattr(self,'Saved_Network')):
            New_frame=IdSimulationFrame('Type of simulation',self)
        else:
            Text='There is no saved network. Try again.'
            logging.info(Text)


    def Verified_Launch(self):
        """Simulation permettant le lancement de la simulation ainsi que sauvegarde des résultats"""
        if(not(self.Saved_Network)):
            self.mainpath=self.SaveNetwork(None)
        total_div_time=int(self.Param['Time']['Number of time used steps'][0])
        nb_chambers=len(self.Nodes['Reservoirs'])+len(self.Nodes['IncJunctions'])
        nb_chambers_fs=len(self.Nodes['Reservoirs'])
        nb_pipes=self.Zones[0]['NbrVec']
        filename_in=self.mainpath
        Init=self.InitNetwork
        H,Q=wolfpy.launch_simulation(Init,self.type_simulation,filename_in,nb_chambers,nb_pipes,total_div_time)
        #On va récupérer les noms des éléments
        #Uniquement valable pour zone canalisations
        fileLoc=filename_in+'\\Name_Pipes.txt'
        NamePipe=self.Provide_Values(fileLoc)
        #Valable pour tous les noeuds
        fileLoc=filename_in+'\\Name_Chmbrs.txt'
        NameNode=self.Provide_Values(fileLoc)
        #On s'occupe des noeuds
        self.Nodes=self.Attr_Values_Nodes(self.Nodes,H,NameNode,nb_chambers_fs,total_div_time)
        #On s'occupe des canalisations
        ID_Zone=0
        self.Zones=self.Attr_Values_Vectors(self.Zones,Q,NamePipe,ID_Zone,total_div_time)
        self.InitNetwork=1
        Test=1


    def Provide_Values(self,file):
        with open(file) as f:
            content = f.read().splitlines()

        #On ferme le fichier créé uniquement pour obtenir les noms

        return content

    def Attr_Values_Nodes(self,Nodes,H,NameListNode,nb_chambers_fs,total_div_time):
        cpt_Node=0
        TypeNode=['Reservoirs','IncJunctions']
        for Name in NameListNode:
            Name=Name.lstrip()
            if(cpt_Node<nb_chambers_fs):
                for i in range(total_div_time):
                    Nodes[TypeNode[0]][Name]['ValueH'][i]=H[cpt_Node][i]
                    Test=1
            else:
                for i in range(total_div_time):
                    Nodes[TypeNode[1]][Name]['ValueH']=H[cpt_Node][i]
                Test=1
            cpt_Node+=1
        Test=1
        return Nodes


    def Attr_Values_Vectors(self,Zones,Q,NameListVec,ID_Zone,total_div_time):
        """S'applique à une catégorie d'élément dans le réseau"""
        cpt_vec=0
        for Name in NameListVec:
            Name=Name.lstrip()
            if(Name in Zones[ID_Zone]['Name']):
                ID_El=Zones[ID_Zone]['Name'].index(Name)
                SizeVal=len(Zones[ID_Zone]['Value'][ID_El])
                for i in range(total_div_time):
                    if(i<SizeVal):
                        Zones[ID_Zone]['Value'][ID_El][i]=Q[cpt_vec][i]
                    else:
                        Zones[ID_Zone]['Value'][ID_El].append(Q[cpt_vec][i])
                cpt_vec+=1

        return Zones

class MyCanvasBase(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.init = False
        self.NewDraw = False
        #On veut s'assurer que la vérification des coordonnées se fait uniquement quand le réseau a eu le temps d'être complètement représenté
        self.Movement=0
        self.context = glcanvas.GLContext(self)

        self.lastx = self.x = 30
        self.lasty = self.y = 30
        #self.size = None
        self.SetSize(parent.Size[0],parent.Size[1])
        self.List_Nodes_OGL=parent.List_Nodes_OGL
        self.Edg_OGL=parent.Edg_OGL
        self.Modif_Edges=parent.Modif_Edges
        self.Modif_Nodes=parent.Modif_Nodes
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.Text = wx.StaticText( self, wx.ID_ANY, u"  Available Channels  ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Text.Wrap( -1 )

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        #self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)
        self.Bind(wx.EVT_RIGHT_UP, self.RightClick)


    def OnSize(self, event):
        wx.CallAfter(self.DoSetViewport)
        self.NewDraw = False
        event.Skip()


    def DoSetViewport(self):
        size = self.size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)


    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        #dc.Clear()
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        if not self.NewDraw:
            self.OnDraw()
            self.NewDraw = True

        Test=1

    #def OnMouseDown(self, evt):
     #   self.CaptureMouse()
      #  self.x, self.y = self.lastx, self.lasty = evt.GetPosition()


    #def OnMouseUp(self, evt):
     #   self.ReleaseMouse()


    def OnMouseMotion(self, evt):
        if(self.Movement==1):
            self.x, self.y = evt.GetPosition()
            #Procedure de transformations des coordonnées pour obtenir celles liées au réseau de base
            self.Coordi=[self.x,self.y]
            self.Coordi=self.UpdCoordinates()
            Round_Coord=[round(self.Coordi[0], 2),round(self.Coordi[1], 2)]
            self.Text.SetLabelText("x : %s ,y: %s" % (Round_Coord[0],Round_Coord[1]))
            if evt.Dragging() and evt.LeftIsDown():
                self.lastx, self.lasty = self.x, self.y

                self.Refresh(False)
    #Fonction générique pour passer de coordonnées pixels à coordonnées réelles du réseau
    def UpdCoordinates(self):

        SizMax=[]
        SizMax.append(self.BestVirtualSize.Width)
        SizMax.append(self.BestVirtualSize.Height)
        #On inverse coordonnée Y vu qu'elle est inversée de base
        self.Coordi[1]=self.BestVirtualSize.Height-self.Coordi[1]
        #Il faut réaliser à présenter différentes étapes de transformation inverse vis-à-vis de la mise en place du réseau
        LocCoord=[0.0,0.0]
        for i in range(2):
            self.Coordi[i]=self.Coordi[i]/SizMax[i]
            if(self.NewCoordMax[i]==self.NewCoordMin[i]):
                LocCoord[i]=self.MinCoord[i]
            else:
                LocCoord[i]=(self.Coordi[i]-self.DeltaPlace[i])/self.SizeMax[i]/self.MinimumSize*self.SizMax[i]
                LocCoord[i]=LocCoord[i]*self.Delta_Max+self.MinCoord[i]
                Test=1
        test=1
        return LocCoord

    #Fonction destinée à la fois à récupérer les informations puis à afficher les données utiles
    def OnClick(self, e):
        type_event=1
        xdata=e.Position.x
        ydata=e.Position.y
        self.Coordi=[xdata,ydata]
        self.Parent.LocNode=self.UpdCoordinates()
        self.type_click=1
        self.new_edge='X'
        if(hasattr(self,'loc_new_edge')):
            if(self.loc_new_edge!='X'):
                self.new_edge=self.loc_new_edge
        if(hasattr(self,'Edition_Mode_Local')):
            self.Edition_Mode=self.Edition_Mode_Local
        #Clic gauche renvoie des informations minimes sur le noeud ou tronçon le plus proche
        if(self.Parent.Edition_Mode):
            Test=1
            #Clic gauche utilisé directement pour faire les liaisons entre les noeuds en venant soit sélectionner le premier noeud ou le second noeud pour faire la liaison
            #Test=self.Parent.Select_Node(self.Parent.LocNode,self.Parent.Discr_Nodes,self.List_Nodes_OGL)
            Test=self.Parent.Select_Node(self.Parent.LocNode,self.List_Nodes_OGL)
        else:
            lol=1
            if(self.Parent.Zoom==1):
                self.Parent.NodeZoom+=1
                self.Parent.ZoomN[self.Parent.NodeZoom-1]=self.Parent.LocNode
                if(self.Parent.NodeZoom==2 or self.Parent.NodeZoom==4):
                    self.Parent.canvas2.NewDraw=False
            else:
                LeTest=self.Parent.Assoc_element()
                self.Parent.canvas2.NewDraw=False
                Test=1


    #Fonction destinée à la fois à récupérer les informations puis à afficher les données utiles
    def RightClick(self, e):
        type_event=1
        xdata=e.Position.x
        ydata=e.Position.y
        self.Coordi=[xdata,ydata]
        self.Parent.LocNode=self.UpdCoordinates()
        self.type_click=1
        self.new_edge='X'
        if(hasattr(self,'loc_new_edge')):
            if(self.loc_new_edge!='X'):
                self.new_edge=self.loc_new_edge
        if(hasattr(self,'Edition_Mode_Local')):
            self.Edition_Mode=self.Edition_Mode_Local
        #clic droit ouvre sur une fenêtre ouvrant sur la plupart des attributs de l'élément afin de les modifier (écriture souple ou lourde)
        if(self.Parent.Edition_Mode):
            #Le clic droit amène directement dans la sous-routine d'ajout de noeud
            New_frame=NewNodeFrame('New node in the network',self)
        else:
            #Clic Droit
            #Première étape est de savoir quel type de résultat veut afficher l'utilisateur : fenêtre intermédiaire proposant les différents choix disponibles
            #Déterminer le type de paramétrage à considérer ainsi qu'éventuellement, le pas de temps à évaluer : sous-routine à implémenter
            title='Data to draw'
            self.child_frame=Draw_Options(self,title,self)
            Parent=self.GetParent()
            #self.child_frame.Bind(wx.EVT_CLOSE, self.OnChildFrameClose)
            test=1
            #self.Show_Results=False
                #Test temporaire afin de réaliser cette fois une surimpression du réseau en affichant des résultats
        #Phase de reconnaissance des coordonnées afin d'y associer l'élément le plus proche
        test=1

    #La fermeture de la fenêtre secondaire vient donc indiquer que l'utilisateur a potentiellement renseigné ce qui l'intéressait.
    #def OnChildFrameClose(self, event):

     #   self.child_frame.Close()
      #  self.child_frame.Destroy()

       # Test=1
class CubeCanvas(MyCanvasBase):

    #Procédure pour créer le réseau : on doit conserver les proportions dans l'affichage final
    def wireCube(self):
        Coord=[]
        Coord.append([])
        Coord.append([])
        Coord.append([])
        MaxLocCoord=np.array([0.0,0.0,0.0])
        MinLocCoord=np.array([100000.0,100000.0,100000.0])
        self.Movement=0
        TTTime=[0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        start = time.time()
        Delta=[]
        SizeMax=[]
        Bords=0.05
        Test_Vector=0
        Test_Node=0
        Parent=self.GetParent()
        TypeNode=['IncJunctions','Reservoirs']
        #Partie colorisation pour affichage de résultats selon
        if(hasattr(Parent,'Show_Param_Results')):
            if(bool(Parent.Show_Param_Results)):
                Test_Node,Test_Vector,Param_Color=Parent.analyse_params()
                Test=1
        if(hasattr(Parent,'Show_Param_Clients')):
            if(bool(Parent.Show_Param_Clients)):
                Test_Node,Test_Vector,Param_Color=Parent.analyse_params_Clients()
                Test=1

        if(hasattr(Parent,'Show_Results')):
            if(bool(Parent.Show_Results)):
                Param_Color=[]
                self.Param_Vec_Color=[]
                self.mypal.nb,self.mypal.values,self.mypal._segmentdata,self.mypal.colorsflt=self.mypal.export_palette_matplotlib('RdYlGn')
                #On va chercher à identifier la couleur des tronçons ou des noeuds
                #Noeuds
                MParam=[1000000,0]
                #Frame_loc.ExtrNodes,Frame_loc.ExtrVectors
                if(Parent.ExtrNodes[0]!=MParam[0] or Parent.ExtrNodes[1]!=MParam[1]):
                    Test_Node=1
                    MParam[0]=Parent.ExtrNodes[0]
                    MParam[1]=Parent.ExtrNodes[1]
                    #Test afin de vérifier si les extrémités sont identiques, dans ce cas, on impose 0 sauf si valeur nulle : unité
                    NullValue=0.0
                    if(MParam[0]==MParam[1]):
                        if(MParam[0]==NullValue):
                            MParam[1]=1.0
                        else:
                            MParam[0]=0.9*MParam[0]
                    #Première partie est utilisée pour construire Param_Color
                    for i in self.List_Nodes_OGL['Coord']:
                        Param_Color.append([0.0,0.0,0.0,0.0])
                    for Type in TypeNode:
                        for NameNode in Parent.Nodes[Type]:
                            Param=float(Parent.Nodes[Type][NameNode]['ShowVal'])
                            Pos=Parent.Nodes[Type][NameNode]['IndPos']
                            Loc=(Param-MParam[0])/(MParam[1]-MParam[0])
                            Loc_Color=self.mypal.lookupcolorflt(Loc)
                            Param_Color[Pos]=Loc_Color
                    nb_node=len(Param_Color)
                    test=1
                #Vecteurs
                MParam=[1000000,0]
                #Frame_loc.ExtrNodes,Frame_loc.ExtrVectors
                if(Parent.ExtrVectors[0]!=MParam[0] or Parent.ExtrVectors[1]!=MParam[1]):
                    Test_Vector=1
                    MParam[0]=Parent.ExtrVectors[0]
                    MParam[1]=Parent.ExtrVectors[1]
                    #Test afin de vérifier si les extrémités sont identiques, dans ce cas, on impose 0 sauf si valeur nulle : unité
                    NullValue=0.0
                    if(MParam[0]==MParam[1]):
                        if(MParam[0]==NullValue):
                            MParam[1]=1.0
                        else:
                            MParam[0]=0.9*MParam[0]
                    for i in self.Edg_OGL[0]:
                        self.Param_Vec_Color.append(1.0)
                    Cpt_orig=0
                    for i in range(len(Parent.Zones)):
                        NbVectors=Parent.Zones[i]['NbrVec']
                        if(bool(NbVectors)):
                            cpt_vec=Cpt_orig
                            Cpt_orig=Cpt_orig+NbVectors
                            for Param in Parent.Zones[i]['ShowVal']:
                                if(Param!='X'):
                                    Loc=(Param-MParam[0])/(MParam[1]-MParam[0])
                                    Loc_Color=self.mypal.lookupcolorflt(Loc)
                                    self.Param_Vec_Color[cpt_vec]=Loc_Color
                                else:
                                    self.Param_Vec_Color[cpt_vec]=[0.0,0.0,0.0,1.0]
                                cpt_vec=cpt_vec+1

        #Première étape : évaluer la taille disponible de la fenêtre
        self.SizMax=[]
        self.SizMax=np.array([self.BestVirtualSize.Width,self.BestVirtualSize.Height,1.0])
        MinSize=min([self.BestVirtualSize.Width,self.BestVirtualSize.Height])
        self.MinimumSize=MinSize
        MaxSize=max([self.BestVirtualSize.Width,self.BestVirtualSize.Height])
        RapportAspect=self.MinimumSize/MaxSize
        RapportAspect=1
        LMax1=RapportAspect*(1.0-2*Bords)
        HMax1=RapportAspect*(1.0-2*Bords)

        self.SizeMax=np.array([LMax1,HMax1,1])


        #self.List_Nodes_OGL,self.Edg_OGL
        if(self.Modif_Edges):
            self.Modif_Edges=False
            self.PosVert=[]
            self.IndEdge=[]
            cpt_edge=0
            for cubeEdge in self.Edg_OGL[0]:
                for cubeVertex in cubeEdge:
                    cubeVertex=cubeVertex-1
                    self.PosVert.append(cubeVertex)
                    self.IndEdge.append(cpt_edge)
                    for i in range(3):
                        Coord[i].append(self.List_Nodes_OGL['Coord'][cubeVertex][i])
                cpt_edge=cpt_edge+1
            self.MaxCoord=[]
            self.MinCoord=[]
            #Zoom se fait en réalité en contrôlant l'affichage des coordonnées extrêmes
            for Loc_Cord in Coord:
                #local_value1=max(Loc_Cord)-7000.0
                self.MaxCoord.append(max(Loc_Cord))
                #self.MaxCoord.append(local_value1)
                local_value2=min(Loc_Cord)+7000.0
                self.MinCoord.append(min(Loc_Cord))
                #self.MinCoord.append(local_value2)
                DeltaLoc=max(Loc_Cord)-min(Loc_Cord)
                #DeltaLoc=local_value1-local_value2
                Delta.append(DeltaLoc)
            self.Delta_Max=max(Delta)
        end = time.time()
        TTTime[0]=end-start
        start = time.time()

        #Le zoom se fait en cliquant deux fois, fixant alors un rectangle en considérant donc que l'utilisateur choisit les coinx extérieurs de celui-ci
        if(Parent.Zoom>0):
            #Mode 1 : on modifie le zoom tandis que le Mode 2 signifie qu'on garde le zoom actuel en place uniquement
            if(Parent.Zoom==1):
                if(Parent.NodeZoom==4):
                    Parent.NodeZoom=2
                    Parent.ZoomN[0]=Parent.ZoomN[2]
                    Parent.ZoomN[1]=Parent.ZoomN[3]
                if(Parent.NodeZoom==2):
                    self.MaxCoordZoom=[]
                    self.MinCoordZoom=[]
                    Size=0
                    Loc_Pos=[]
                    Loc_Pos.append([])
                    Loc_Pos.append([])
                    DeltaZoom=[]
                    for Coord in Parent.ZoomN:
                        Size += 1
                        if(Size<3):
                            Index = 0
                            for Position in Coord:
                                Loc_Pos[Index].append(Position)
                                Index += 1
                    for Index in range(2):
                        self.MaxCoordZoom.append(max(Loc_Pos[Index]))
                        self.MinCoordZoom.append(min(Loc_Pos[Index]))
                        DeltaLoc=max(Loc_Pos[Index])-min(Loc_Pos[Index])
                        DeltaZoom.append(DeltaLoc)
                    self.MaxCoordZoom.append(self.MaxCoord[2])
                    self.MinCoordZoom.append(self.MinCoord[2])
                    self.Delta_MaxZoom=max(DeltaZoom)
                else:
                    if(Parent.NodeZoom<2):
                        self.MaxCoordZoom=self.MaxCoord
                        self.MinCoordZoom=self.MinCoord
                        self.Delta_MaxZoom=self.Delta_Max
        else:
            self.MaxCoordZoom=self.MaxCoord
            self.MinCoordZoom=self.MinCoord
            self.Delta_MaxZoom=self.Delta_Max
        self.MaxCoord=self.MaxCoordZoom
        self.MinCoord=self.MinCoordZoom
        self.Delta_Max=self.Delta_MaxZoom
        if(self.Modif_Edges):
            self.MaxCoord=np.array(self.MaxCoord)
            self.MinCoord=np.array(self.MinCoord)
        #Troisième étape : on va donc bien exprimer les deux axes pour conserver proportions
        test=1
        for cubeVertex in self.List_Nodes_OGL['Coord']:
            loc_curb=np.array(cubeVertex)
            loc_curb=(loc_curb-self.MinCoord)/self.Delta_Max
            loc_curb=loc_curb*self.SizeMax*self.MinimumSize/self.SizMax
            if(loc_curb[0]<=1.0 and loc_curb[1]<=1.0 and loc_curb[0]>=0.0 and loc_curb[1]>=0.0):
                MaxLocCoord=np.maximum(MaxLocCoord,loc_curb)
            if(loc_curb[0]>=0.0 and loc_curb[1]>=0.0 and loc_curb[0]<=1.0 and loc_curb[1]<=1.0):
                MinLocCoord=np.minimum(MinLocCoord,loc_curb)

        #On évalue la place disponible pour centrer le réseau selon le CG
        self.DeltaPlace=[0,0,1]
        self.DeltaPlace=0.5-(MaxLocCoord+MinLocCoord)/2
        if(Parent.Zoom==1 and Parent.NodeZoom==2):
            self.DeltaPlace=[0,0,1]
        #A faire uniquement si on modifie List_Nodes_OGL, dans le cas contraire, une seule règle de trois suffit : voir s'il ne s'agit pas aussi d'un facteur d'échelle à manipuler
        #Quatrième étape, on va d'abord récupérer les coordonnées extrêmes afin de recentrer le réseau
        if(self.Modif_Nodes):
            self.NewVertiList=[]
            self.CoordOrig=[]
            #Données basiques des variables de la fenêtre
            self.NewCoordMax=[0.0,0.0,0.0]
            self.NewCoordMin=[100000.0,100000.0,100000.0]
            self.DirCoordMax=[0.0,0.0,0.0]
            self.DirCoordMin=[100000.0,100000.0,100000.0]
            Xarray=np
            cptcube=0
            for cubeVertex in self.List_Nodes_OGL['Coord']:
                loc_curb=np.array(cubeVertex)
                if(cptcube==0):
                    self.CoordOrig=[loc_curb]
                else:
                    local_curb=[loc_curb]
                    self.CoordOrig=np.append(self.CoordOrig,local_curb,0)
                    Test=1
                self.DirCoordMax=np.maximum(self.DirCoordMax,loc_curb)
                self.DirCoordMin=np.minimum(self.DirCoordMin,loc_curb)
                loc_curb2=loc_curb
                loc_curb=(loc_curb-self.MinCoord)/self.Delta_Max
                if(loc_curb[0]>0):
                    Test=2
                loc_curb=loc_curb*self.SizeMax*self.MinimumSize/self.SizMax+self.DeltaPlace
                if(loc_curb[0]>0 and loc_curb[0]<1.0 and loc_curb[1]>0 and loc_curb[1]<1.0):
                    Test=2
                self.NewCoordMax=np.maximum(self.NewCoordMax,loc_curb)
                self.NewCoordMin=np.minimum(self.NewCoordMin,loc_curb)
                loc_curb[2]=0.0
                #New_Tupl=tuple(loc_curb)
                #New_Tupl=list(loc_curb)

                if(cptcube==0):
                    #self.NewVertiList.append(New_Tupl)
                    self.NewVertiList=[loc_curb]
                else:
                    local_curb=[loc_curb]
                    self.NewVertiList=np.append(self.NewVertiList,local_curb,0)

                cptcube+=1
            self.Modif_Nodes=False
        else:
            self.Modif_Nodes=False
            #On va faire surtout règle de droit à appliquer directement sur NewVertiList
            #for Pos_Val in range(len(self.NewVertiList[0])):
            for i in range(2):
                self.NewVertiList[:,i]=(self.CoordOrig[:,i]-self.MinCoord[i])/self.Delta_Max*self.SizeMax[i]*self.MinimumSize/self.SizMax[i]+self.DeltaPlace[i]
                Test=1
            self.NewCoordMax=(self.DirCoordMax-self.MinCoord)/self.Delta_Max*self.SizeMax*self.MinimumSize/self.SizMax+self.DeltaPlace
            self.NewCoordMin=(self.DirCoordMin-self.MinCoord)/self.Delta_Max*self.SizeMax*self.MinimumSize/self.SizMax+self.DeltaPlace
            Test=2

        end = time.time()
        TTTime[1]=end-start
        start = time.time()
        cpt_edge=0
        glBegin(GL_LINES)
        Length=0.008
        glColor3f(0.0,0.0,0.0)
        Mod_Color=False
        for IdPos in range(len(self.PosVert)):
            cpt_edge=self.IndEdge[IdPos]
            if(self.Edg_OGL[4][cpt_edge]==1):
                glColor3f(0.0,255.0,0.0)
                Mod_Color=True
            else:
                if(Test_Vector==1):
                    if(cpt_edge==900):
                        Test=1
                    glColor3f(self.Param_Vec_Color[cpt_edge][0],self.Param_Vec_Color[cpt_edge][1],self.Param_Vec_Color[cpt_edge][2])
                    Mod_Color=True
            glVertex3dv(self.NewVertiList[self.PosVert[IdPos]])
            if(Mod_Color):
                glColor3f(0.0,0.0,0.0)
        glEnd()
        end = time.time()
        TTTime[2]=end-start
        start = time.time()
        #On représente les éléments particuliers(pompes/valves)
        cpt_edge=0
        glColor3f(0.0, 0.0, 0.0)
        for cubeEdge in self.Edg_OGL[0]:
            if(self.Edg_OGL[3][cpt_edge]>0): #Type d'élément est une pompe/vanne qui doit être renseignée de façon différente
                #On renseigne le fait sur le dessin qu'il s'agit d'un élément particulier
                self.DrawSpecEl(self.NewVertiList,cubeEdge,self.Edg_OGL[3][cpt_edge],Length,self.MinimumSize,self.SizeMax,self.SizMax)
            cpt_edge=cpt_edge+1
        glColor3f(0.0, 0.0, 0.0)
        if(Test_Node!=2):
            glBegin(GL_POINTS)
        cpt_edge=0
        cpt_node=0
        r=0.01
        rcircle=0.05
        rsquare=2.0*r
        segments=50
        if(Test_Node==2):
            Reduc_R=[0.0]*len(self.List_Nodes_OGL['Coord'])
            PartParam=[0.0]*len(self.List_Nodes_OGL['Coord'])
            for Type in TypeNode:
                for NameNode in Parent.Nodes[Type]:
                    Pos=Parent.Nodes[Type][NameNode]['IndPos']
                    Reduc_R[Pos]=Parent.Nodes[Type][NameNode]['Radius']
                    PartParam[Pos]=Parent.Nodes[Type][NameNode]['Part_Params']

        end = time.time()
        TTTime[3]=end-start
        start = time.time()
        #Affichage des noeuds
        for cubeVertex in self.NewVertiList:
            if(self.List_Nodes_OGL['SpecNode'][cpt_node]==1):
                #On va considérer l'affichage d'un élément récherché par l'utilisateur toujours de la même façon, via noeudrouge
                glColor3f(255.0,0.0,0.0)
            else:
                if(Test_Node==1):
                    val=len(Param_Color)
                    if(cpt_edge>val):
                        Test=1
                    glColor3f(Param_Color[cpt_edge][0],Param_Color[cpt_edge][1],Param_Color[cpt_edge][2])
                else:
                    glColor3f(0.0,0.0,0.0)
            if(Test_Node==2):
                self.drawpartialcircle(cubeVertex[0],cubeVertex[1],rcircle,Reduc_R[cpt_edge],segments,PartParam[cpt_edge],self.MinimumSize,self.SizeMax,self.SizMax,Param_Color)
                cpt_edge=cpt_edge+1
            else:
                if(self.List_Nodes_OGL['TypeNode'][cpt_node]!='Reservoirs'):
                    glVertex3dv(cubeVertex)
                cpt_edge=cpt_edge+1

            cpt_node=cpt_node+1
        if(Test_Node!=2):
            glEnd()
        cpt_node=0
        cpt_edge=0
        glColor3f(0.0, 0.0, 0.0)
        #On s'occupe ensuite des réservoirs
        for cubeVertex in self.NewVertiList:
            if(self.List_Nodes_OGL['SpecNode'][cpt_node]==1):
                #On va considérer l'affichage d'un élément récherché par l'utilisateur toujours de la même façon, via noeudrouge
                glColor3f(255.0,0.0,0.0)
            else:
                if(Test_Node==1):
                    glColor3f(Param_Color[cpt_edge][0],Param_Color[cpt_edge][1],Param_Color[cpt_edge][2])
                    cpt_edge=cpt_edge+1
                else:
                    glColor3f(0.0,0.0,0.0)
            if(self.List_Nodes_OGL['TypeNode'][cpt_node]=='Reservoirs'):
                self.draw_square(cubeVertex[0],cubeVertex[1],rsquare,self.MinimumSize,self.SizeMax,self.SizMax)
            cpt_node=cpt_node+1

        self.Movement=1
        end = time.time()
        TTTime[4]=end-start
        Test=1

    #Dessin adapté pour les jonctions incompressibles
    def DrawCircle(self,x,y,r,segments,MinSize,SizeMax,SizMax):
        Bords=0.1
        angle=2.0*pi/float(segments)

        prevX=x
        prevY=y-r*SizeMax[1]*MinSize/SizMax[1]
        nb_seg=segments+1
        for i in range(nb_seg):
            newX=x+r*SizeMax[0]*MinSize/SizMax[0]*sin(angle*float(i))
            newY=y-r*SizeMax[1]*MinSize/SizMax[1]*cos(angle*float(i))
            glBegin(GL_TRIANGLES)
            glVertex3f(x,y,0.0)
            glVertex3f(prevX,prevY,0.0)
            glVertex3f(newX,newY,0.0)
            glEnd()
            prevX=newX
            prevY=newY
        return
    def drawpartialcircle(self,x,y,r,Reduc_r,segments,PartParam,MinSize,SizeMax,SizMax,Param_Color):
        Bords=0.1
        angle=2.0*pi/float(segments)
        radius=r*Reduc_r
        prevX=x
        prevY=y-r*SizeMax[1]*MinSize/SizMax[1]
        nb_seg=segments+1
        Final_Parts=[]
        Final_Colors=[]
        if isinstance(PartParam, list):
            cpt_part=0
            for Part in PartParam:
                if(Part>0.0):
                    Part=int(Part*float(segments))
                    Final_Parts.append(Part)
                    Final_Colors.append(Param_Color[cpt_part])
                cpt_part += 1
        else:
            radius=0.01*r
            Final_Parts.append(segments)
            Loc_Color=[0.0,0.0,0.0,0.0]
            Final_Colors.append(Loc_Color)


        cpt_seg=0
        cpt_pos=0
        for i in range(nb_seg):
            glColor3f(Final_Colors[cpt_pos][0],Final_Colors[cpt_pos][1],Final_Colors[cpt_pos][2])
            newX=x+radius*SizeMax[0]*MinSize/SizMax[0]*sin(angle*float(i))
            newY=y-radius*SizeMax[1]*MinSize/SizMax[1]*cos(angle*float(i))
            glBegin(GL_TRIANGLES)
            glVertex2f(x,y)
            glVertex2f(prevX,prevY)
            glVertex2f(newX,newY)
            glEnd()
            cpt_seg += 1
            if(cpt_seg>Final_Parts[cpt_pos]):
                cpt_pos += 1
                cpt_pos = min(cpt_pos,len(Final_Parts)-1)
                cpt_seg =0
            prevX=newX
            prevY=newY
        return
    #Dessin adapté pour les carrés utilisés pour représenter les réservoirs
    def draw_square(self,x, y, width,MinSize,SizeMax,SizMax):
        glBegin(GL_QUADS)
        widthx=width*SizeMax[0]*MinSize/SizMax[0]
        widthy=width*SizeMax[1]*MinSize/SizMax[1]
        glVertex2f(x + widthx/2.0, y+widthy/2.0)
        glVertex2f(x + widthx/2.0, y-widthy/2.0)
        glVertex2f(x - widthx/2.0, y-widthy/2.0)
        glVertex2f(x - widthx/2.0, y+widthy/2.0)
        glEnd()

    #Sous-routine générale pour le dessin d'éléments particuliers de type connecteur
    def DrawSpecEl(self,NewVertiList,cubeEdge,Case,Length,MinSize,SizeMax,SizMax):
        Pos1=cubeEdge[0]-1
        Pos2=cubeEdge[1]-1
        x=(NewVertiList[Pos1][0]+NewVertiList[Pos2][0])/2.0
        y=(NewVertiList[Pos1][1]+NewVertiList[Pos2][1])/2.0
        OppCase=False
        if(Case==1):
            color=[0.5,0.0,0.0]
            self.draw_triangle(x,y,Length,MinSize,SizeMax,SizMax,OppCase,color)
        if(Case==2):
            color=[0.4,0.6,0.0]
            self.draw_triangle(x,y,Length,MinSize,SizeMax,SizMax,OppCase,color)
            OppCase=True
            self.draw_triangle(x,y,Length,MinSize,SizeMax,SizMax,OppCase,color)
    #Dessin adapté pour les triangles utilisés pour représenter les triangles équilatéraux
    def draw_triangle(self,x,y,length,MinSize,SizeMax,SizMax,OppCase,color):
        c=6.0*length/sqrt(3)
        cx=c*SizeMax[0]*MinSize/SizMax[0]
        height=c*sqrt(3)/2.0*SizeMax[1]*MinSize/SizMax[1]
        lengthy=c*sqrt(3)/4.0*SizeMax[1]*MinSize/SizMax[1]
        Node1=[x,y+height]
        if(OppCase):
            Node1=[x,y-height]
        Node2=[x-cx/2.0,y-lengthy]
        Node3=[x+cx/2.0,y-lengthy]
        glBegin(GL_TRIANGLES)
        glColor3f(color[0],color[1],color[2])
        glVertex3f(Node1[0],Node1[1],0.0)
        glVertex3f(Node2[0],Node2[1],0.0)
        glVertex3f(Node3[0],Node3[1],0.0)
        glEnd()

    def refresh2d(self,width,height):
        #glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #glOrtho(0.0, width, 0.0, height, 0.0, 6.0)
        gluOrtho2D(0.0, 1.0,0.0,1.0)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity()


    def InitGL(self):
        # set viewing projection

        self.mypal=wolfpalette(None,"Palette of colors")
        glPointSize(5)
        glEnable(GL_POINT_SMOOTH)


    def OnDraw(self):
        # clear color and depth buffers
        glClearColor(1,1,1,0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #glClearColor(0,0,1,0)
        glLoadIdentity()
        self.refresh2d(width,height)
        glColor3f(0.0, 0.0, 0.0)
        self.wireCube()

        #glTranslatef(0.0, 0.0, -5)


        self.SwapBuffers()


class NewNodeFrame(wx.Frame):
    """
    Frame utilisée pour permettre la mise en place du nouveau noeud
    """
    def __init__(self, title, parent):
        super(NewNodeFrame, self).__init__(parent, title = title,size = (300,200),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
        #Ajout d'un nouveau noeud entraîne à l'activiation du mode d'édition du réseau
        parent.Edition_Mode_Local=True

        #Initialisation du panel
        MainW=parent
        Index=int(MainW.LocalNode[0])

        self.Main_Attr=['Name','Type(R or J)','Coordinate X','Coordinate Y','Coordinate Z','Nb_Patterns']
        #On vient afficher l'ensemble des données utiles pour le noeud
        cpt_row=0

        #On vient également compléter par défaut chaque colonne afin que l'utilisateur puisse rapidement uniquement modifier ce qu'il souhaite
        if(hasattr(MainW,'List_Nodes_OGL')):
            if(bool(MainW.List_Nodes_OGL)):
                    #On considère qu'à ce stade-là, la structure attendue est bien respectée et qu'au moins un noeud a déjà été implémenté
                    Nb_Nodes=len(MainW.List_Nodes_OGL['InitNode'])
                    Dflt_Name='Node_'+str(Nb_Nodes+1)
                    Dft_CoordX=str(0.0)
                    Dft_CoordY=str(0.0)
                    Dft_CoordZ=str(0.0)
                    if(Nb_Nodes>0):
                        Dft_CoordX=str(float(MainW.List_Nodes_OGL['Coord'][0][0])+1.0)
                        Dft_CoordY=str(float(MainW.List_Nodes_OGL['Coord'][0][1])+1.0)
                        Dft_CoordZ=str(float(MainW.List_Nodes_OGL['Coord'][0][2])+1.0)
                    self.Default_Values=[Dflt_Name,'J',Dft_CoordX,Dft_CoordY,Dft_CoordZ,'0']
            else:
                self.Default_Values=['Node_1','J','0.0','0.0','0.0','0']
        else:
            self.Default_Values=['Node_1','J','0.0','0.0','0.0','0']

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.Centre()
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        #frame_sizer.Add(panel, 1, wx.EXPAND| wx.LEFT | wx.RIGHT, wx.ALIGN_CENTER)

        #Message d'annonce pour savoir ce qui est à réaliser
        Message='Characteristics of the new node'
        self.message = wx.StaticText(self, -1, Message)
        frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)

       #Partiée à la grille des coordonnées du noeud
        self.panel = PanelGeneral(self)
        frame_sizer.Add(self.panel, 1, wx.EXPAND)
       #Partie liée aux choix de validation ou d'annulation
        sz2 = wx.BoxSizer(wx.HORIZONTAL)
        self.btn=wx.Button(self,-1,"Add")
        sz2.Add(self.btn,0, wx.ALL, 10)
        self.btn.Bind(wx.EVT_BUTTON,self.Saved_Node)

        self.btn2=wx.Button(self,-1,"Close")
        sz2.Add(self.btn2,0, wx.ALL, 10)
        self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

        self.btn3=wx.Button(self,-1,"Browse")
        sz2.Add(self.btn3,0, wx.ALL, 10)
        self.btn3.Bind(wx.EVT_BUTTON,self.BrowseFile)

        frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
        self.SetAutoLayout(True)
        self.SetSizerAndFit(frame_sizer)
        self.Show()
        Test=1

    #Sous-routine utilisée dans le but d'ajouter un noeud supplémentaire au réseau déjà présent
    def Saved_Node(self, e):

        Main=self.GetParent()
        #Il faut rechercher les valeurs dans la grille pour ajouter un nouveau noeud en faisant test sur le type de noeud
        MyPanel=self.panel
        Nb_Rows=MyPanel.thegrid.GetNumberRows()
        Valid_Test=True
        #Sauvegarde des valeurs de la grille
        MyPanel.GridValues=[]
        for Row in range(Nb_Rows):
            MyPanel.GridValues.append( MyPanel.thegrid.GetCellValue(Row,0))
        for Row in range(Nb_Rows):
            Value=MyPanel.GridValues[Row]
            if(MyPanel.Main_Attr[Row]==self.Main_Attr[1]):
                Type_Node=Value.lower()
                if(Type_Node!='j' and Type_Node!='r'):
                    #Problème de format proposé par l'utilisateur, un évènement doit être appelé
                    dlg = wx.MessageDialog(
                        None, "The proposed format for the type of Node is not good. Impose the J Format ?", "Incorrect format", wx.YES_NO | wx.CANCEL | wx.CENTRE
                    )
                    result = dlg.ShowModal()
                    self.Centre()
                    self.Show()
                    Valid_Test=False
                    if result == wx.ID_YES:
                        Type_Node='j'
                        Valid_Test=True
                    else:
                        pass
                    Test=1
        if(Valid_Test):

            #Evaluation des paramètres importants
            NameNode=MyPanel.GridValues[0]
            CoordX=float(MyPanel.GridValues[2])
            CoordY=float(MyPanel.GridValues[3])
            CoordZ=float(MyPanel.GridValues[4])
            NbRelPatterns=int(MyPanel.GridValues[5])
            self.NbRelPatterns=NbRelPatterns
            #D'abord vérification que les attributs de réservoir et de patterns sont correctement adressés avant d'ajouter effectivement le noeud dans la liste
            #Frame liée à obtenir les caractéristiques des noeuds
            self.Type_Node=Type_Node
            self.NameNode=NameNode
            TypeN='Reservoirs'
            if(Type_Node=='j'):
                TypeN='IncJunctions'
            self.TypeN=TypeN
            Valid_Node=True
            if(self.TypeN=='Reservoirs' or NbRelPatterns>0):
                self.NewAttrToObtain=False
                NewFrameR=NewSubNodeFrame('Characteristics of the node '+NameNode,self)
            else:
                self.Save_Valid_Node()

        Test=1
        return Test
            #Remplacement via les données réelles

    #L'annulation étant choisie par l'utilisateur, l'option est donc levée et la fenêtre est simplement fermée
    def CloseFrame(self, e):
        Test=1
        Main=self.GetParent()
        if(Main.NewNetwork):
            NewEdgeFrame=Main.Edge_To_add(e)
        self.Close()
        self.Destroy()

    #Ouverture de fichier pour aller identifier de façon directe la liste des noeuds (fichier .jun ou .vecr)
    def BrowseFile(self, e):
        Test=1
        pathfile='X'
        pathfile=self.OnOpen()
        Type_Analysis=2
        TypeN=['Reservoirs','IncJunctions']
        if(pathfile!='X'):
            #On a bien un fichier valide à lire
            Main=self.GetParent()
            Main.Nodes,Main.AttrNode,Main.ListedAttr,Main.DftAttrNode,Main.FoundAttr=Import_Nodes_Attributes(pathfile,Main.List_Nodes_OGL,Main.Param,Type_Analysis)
            Test=1
            if(bool(Main.Nodes['Reservoirs']) or bool(Main.Nodes['IncJunctions'])):
                Main.NewNetwork=True
                #On doit vérifier avant d'aller à la suite de bien ajouter les différents paramètres selon des valeurs standardisées
                Type='Reservoirs'
                if(bool(Main.Nodes[Type])):
                    if(0 in Main.FoundAttr[Type]):
                        #Au moins un des attributs est manquant, il faut donc ouvrir sous-fenêtre d'attributs du type de noeud
                        self.TypeN=Type
                        self.PrepareNewFrame()
                else:
                    Type='IncJunctions'
                    if(0 in Main.FoundAttr[Type]):
                        self.TypeN=Type
                        self.PrepareNewFrame()
            else:
                Message='There is no node in the network. Repeat again the procedure with the right directory.'
                logging.info(Message)

    #Recherche du dossier pour partager les données sur les noeuds
    def OnOpen(self):
        namepath='X'
        dlg = wx.DirDialog(self, "Choose the Nodes directory")
        if dlg.ShowModal() == wx.ID_OK:
            namepath=dlg.GetPath()
            t=1
        dlg.Destroy()
        return namepath

    #Préparation de la nouvelle frame pour aller rechercher les attributs manquants pour chaque élément du type
    def PrepareNewFrame(self):
        Main=self.GetParent()
        cpt_attr=0
        self.MissingAttr=[]
        self.DftValue=[]
        for Attr in Main.FoundAttr[self.TypeN]:
            if(Attr==0):
                self.MissingAttr.append(Main.AttrNode[self.TypeN][cpt_attr])
                self.DftValue.append(Main.DftAttrNode[self.TypeN][cpt_attr])
            cpt_attr+=1
        self.IndLocNode=0
        cpt_attr=0
        for Node in Main.Nodes[self.TypeN]:
            if(cpt_attr==0):
                self.NameNode=Node
            cpt_attr+=1
        self.LaunchNewFrame()

    #Lancer nouvelle figure uniquement si celle d'avant a été finalisée
    def LaunchNewFrame(self):
        Main=self.GetParent()
        Test=2
        cpt_node=0
        for Node in Main.Nodes[self.TypeN]:
            if(self.IndLocNode==cpt_node):
                self.NameNode=Node
                NewFrame=NewAttrNodeFrame('Attributes of the node',self)
            cpt_node+=1
        Test=1

    #Procedure finale permettant de sauvegarder un noeud valide
    def Save_Valid_Node(self):
        Main=self.GetParent()
        MyPanel=self.panel
        #On passe cette fois à l'ajout du noeud dans le réseau
        Nb_Nodes=len(Main.List_Nodes_OGL['InitNode'])
        Loc_Node=Nb_Nodes
        #Evaluation des paramètres importants
        NameNode=MyPanel.GridValues[0]
        CoordX=float(MyPanel.GridValues[2])
        CoordY=float(MyPanel.GridValues[3])
        CoordZ=float(MyPanel.GridValues[4])
        NbRelPatterns=int(MyPanel.GridValues[5])
        #On complète List_nodes également et Nodes
        Current_Coord=(CoordX,CoordY)
        Coord=(CoordX,CoordY,CoordZ)
        NbNodes=len(Main.Nodes[self.TypeN])+1
        Nb_total_Time=int(Main.Param['Time']['Number of time used steps'][0])
        Main.Nodes[self.TypeN][NameNode]={}
        Main.Nodes[self.TypeN][NameNode]['CoordPlan']=(CoordX,CoordY)
        Main.Nodes[self.TypeN][NameNode]['CoordZ']=CoordZ
        Main.Nodes[self.TypeN][NameNode]['IndPos']=Loc_Node
        Main.Nodes[self.TypeN][NameNode]['ShowVal']=[0.0]*Nb_total_Time
        Main.Nodes[self.TypeN][NameNode]['ValueH']=[0.0]*Nb_total_Time
        Main.Nodes[self.TypeN][NameNode]['NbPatterns']=NbRelPatterns
        Main.Nodes[self.TypeN][NameNode]['Patterns']=['X']
        if(self.TypeN=='IncJunctions'):
            Main.Nodes[self.TypeN][NameNode]['Consumers']=['X']
        Main.List_Nodes_OGL['NbrEl'].append(NbNodes)
        Main.List_Nodes_OGL['CoordPlan'].append((CoordX,CoordY))
        Main.List_Nodes_OGL['Coord'].append(Coord)
        Main.List_Nodes_OGL['InitNode'].append(0)
        Main.List_Nodes_OGL['TypeNode'].append(self.TypeN)
        Main.List_Nodes_OGL['NameNode'].append(NameNode)
        Main.List_Nodes_OGL['SpecNode'].append(0)
        Main.Modif_Nodes=True

        #S'il s'agit d'un réservoir, on complète également les attributs selon des valeurs standardisées
        if(self.Type_Node=='r'):
            List_Attr=['SECTION','Max_H','Min_H','IC_V']
            Standard_Values=[100,10,0,80]
            cpt=0
            for Attr in List_Attr:
                Main.Nodes[self.TypeN][NameNode][Attr]=Standard_Values[cpt]
                cpt=cpt+1
        #On vient reset du coup également la grille pour que la valeur par défaut repasse au noeud suivant
        Nb_Nodes=len(Main.List_Nodes_OGL['InitNode'])
        Loc_Node=Nb_Nodes
        Loc_Node+=1
        DfltName='Node_'+str(Loc_Node)
        #On modifie également la coordonnée X afin de pouvoir rajouter rapidement des noeuds
        DfltXCoord=str(CoordX+1.0)
        cpt_val=0
        for Dft_Val in self.Default_Values:
            MyPanel.thegrid.SetCellValue(cpt_val,0, Dft_Val)
            cpt_val+=1
        MyPanel.thegrid.SetCellValue(2,0, DfltXCoord)
        MyPanel.thegrid.SetCellValue(0,0, DfltName)

class NewSubNodeFrame(wx.Frame):
    """
    Frame utilisée pour ajouter les paramètres propres à chaque catégorie d'élément connecteur
    """
    def __init__(self, title, parent):
       super(NewSubNodeFrame, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)

       #Initialisation de la grille = évaluation du nombre d'attributs à afficher
       #Les attributs dépendent du type d'élément qui est ajouté par l'utilisateur
       self.MainW=parent.GetParent()
       self.parent=parent
       Type_Node=parent.Type_Node
       self.Main_Attr=[]
       self.Default_Values=[]
       if(Type_Node=='r'):
           self.Main_Attr=['Section[m²]','Max. Height[m]','Min. Height[m]','Init_Cond[m³]','Nb Patterns[-]']
           self.Default_Values=['50.0','10.0','0.0','300','0']
       cpt_ptrn=1
       #for IdPat in range(self.MainW.Nodes[parent.TypeN][parent.NameNode]['NbPatterns']):
       for IdPat in range(self.parent.NbRelPatterns):
           self.Main_Attr.append('Name pattern '+str(cpt_ptrn))
           self.Default_Values.append('X')
           cpt_ptrn+=1
       cpt_ptrn=1
       #for IdPat in range(self.MainW.Nodes[parent.TypeN][parent.NameNode]['NbPatterns']):
       for IdPat in range(self.parent.NbRelPatterns):
           self.Main_Attr.append('Nb cons. pattern '+str(cpt_ptrn))
           self.Default_Values.append('XX')
           cpt_ptrn+=1

       self.Centre()
       frame_sizer = wx.BoxSizer(wx.VERTICAL)

       #Message d'annonce pour savoir ce qui est à réaliser
       Message='Characteristics of the node '+parent.NameNode
       self.message = wx.StaticText(self, -1, Message)
       #frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
       frame_sizer.Add(self.message, 0, wx.EXPAND)
       #Partiée à la grille des coordonnées du noeud
       self.panel = PanelGeneral(self)
       frame_sizer.Add(self.panel, 1, wx.EXPAND)
       #Partie liée aux choix de validation ou d'annulation
       sz2 = wx.BoxSizer(wx.HORIZONTAL)
       self.btn=wx.Button(self,-1,"Ok")
       sz2.Add(self.btn,0, wx.ALL, 10)
       self.btn.Bind(wx.EVT_BUTTON,self.Saved_char_Node)

       self.btn2=wx.Button(self,-1,"Close")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

       frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
       self.SetAutoLayout(True)
       self.SetSizerAndFit(frame_sizer)
       self.Show()
       Test=1

    #L'annulation étant choisie par l'utilisateur, l'option est donc levée et la fenêtre est simplement fermée
    def CloseFrame(self, e):
       Test=1
       Message='The node is not added because all the parameters are not properly identified.'
       logging.info(Message)
       self.Close()
       self.Destroy()

       #On va donc replacer l'ensemble des informations obtenues pour le réseau
    def Saved_char_Node(self,e):
        self.parent.Save_Valid_Node()
        Nb_Rows=self.panel.thegrid.GetNumberRows()
        NbNodes=len(self.MainW.Nodes)-1
        NameNode=self.parent.NameNode
        TypeN=self.parent.TypeN
        cpt=0
        if(TypeN=='Reservoirs'):
            R_Attrib=['SECTION','Max_H','Min_H','IC_V']
            for Attrib in R_Attrib:
                self.MainW.Nodes[TypeN][NameNode][Attrib]=self.panel.GridValues[cpt]
                cpt+=1
        self.MainW.Nodes[TypeN][NameNode]['Patterns']=['X']
        for IdPat in range(self.MainW.Nodes[TypeN][NameNode]['NbPatterns']):
            self.MainW.Nodes[TypeN][NameNode]['Patterns'].append(self.panel.GridValues[cpt])
            cpt+=1
        if(TypeN=='IncJunctions'):
            self.MainW.Nodes[TypeN][NameNode]['Consumers']=['X']
            Dft_Value='X'
            for IdPat in range(self.MainW.Nodes[TypeN][NameNode]['NbPatterns']):
                if(self.panel.GridValues[cpt]==Dft_Value):
                    self.panel.GridValues[cpt]='1'
                    Message='The number of consumers is put to 1 for Pattern '+str(IdPat+1)
                    logging.info(Message)
                self.MainW.Nodes[TypeN][NameNode]['Consumers'].append(self.panel.GridValues[cpt])
                cpt+=1

        if(self.parent.NewAttrToObtain):
            self.parent.IndLocNode+=1
            if(self.parent.IndLocNode<=NbNodes):
                NewFrame=self.parent.LaunchNewFrame()
            else:
                if(TypeN=='Reservoirs'):
                    self.parent.TypeN='IncJunctions'
                    NewFrame=self.parent.PrepareNewFrame()
        self.Close()
        self.Destroy()

class NewAttrNodeFrame(wx.Frame):
    """
    Ajout des paramètres absents selon catégorie de noeuds
    """
    def __init__(self, title, parent):
       super(NewAttrNodeFrame, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)

       #Initialisation de la grille = évaluation du nombre d'attributs à afficher
       #Les attributs dépendent du type d'élément qui est ajouté par l'utilisateur
       self.MainW=parent.GetParent()
       self.parent=parent
       self.Main_Attr=[]
       self.Default_Values=[]
       self.Main_Attr=parent.MissingAttr
       self.Default_Values=parent.DftValue

       self.Centre()
       frame_sizer = wx.BoxSizer(wx.VERTICAL)

       #Message d'annonce pour savoir ce qui est à réaliser
       Message='Missing attributes of the node '+parent.NameNode
       self.message = wx.StaticText(self, -1, Message)
       #frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
       frame_sizer.Add(self.message, 0, wx.EXPAND)
       #Partiée à la grille des coordonnées du noeud
       self.panel = PanelGeneral(self)
       frame_sizer.Add(self.panel, 1, wx.EXPAND)
       #Partie liée aux choix de validation ou d'annulation
       sz2 = wx.BoxSizer(wx.HORIZONTAL)
       self.btn=wx.Button(self,-1,"Ok")
       sz2.Add(self.btn,0, wx.ALL, 10)
       self.btn.Bind(wx.EVT_BUTTON,self.Saved_char_Node)

       self.btn2=wx.Button(self,-1,"Close")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

       frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
       self.SetAutoLayout(True)
       self.SetSizerAndFit(frame_sizer)
       self.Show()
       Test=1

    #L'annulation étant choisie par l'utilisateur, on va reprendre les valeurs par défaut
    def CloseFrame(self, e):
       Test=1
       self.Saved_char_Node(e)

    #On va donc replacer l'ensemble des informations obtenues pour le réseau
    def Saved_char_Node(self,e):
        Test=1
        Spec_Attrib='NbPatterns'
        parent=self.parent
        TypeN=parent.TypeN
        NbNodes=len(self.MainW.Nodes[TypeN])-1
        NameNode=parent.NameNode
        TypeN=self.parent.TypeN
        parent.Type_Node='r'
        cpt=0
        parent.NewAttrToObtain=False
        self.MainW.Saved_Network=False
        if(TypeN=='IncJunctions'):
            parent.Type_Node='j'
        for Attrib in self.MainW.ListedAttr[TypeN]:
            if(Attrib==Spec_Attrib):
                NbPatterns=int(self.panel.GridValues[cpt].upper())
                self.MainW.Nodes[TypeN][NameNode][Attrib]=NbPatterns
                parent.NbRelPatterns=NbPatterns
                if(NbPatterns>0):
                    parent.NewAttrToObtain=True
                    NewFrame=NewSubNodeFrame('Patterns of the node '+NameNode,parent)
                else:
                    #Même si le nombre de pattern est nul, on vient attribuer des valeurs par défaut afin de laisser toujours l'affichage
                    self.MainW.Nodes[TypeN][NameNode]['Patterns']=['X']
                    if(TypeN=='IncJunctions'):
                        self.MainW.Nodes[TypeN][NameNode]['Consumers']=['X']
            else:
                if(self.MainW.FoundAttr[TypeN][cpt]==0):
                    self.MainW.Nodes[TypeN][NameNode][Attrib]=self.panel.GridValues[cpt].upper()
            cpt+=1
        #On va évaluer ensuite le noeud suivant éventuel
        if(not(parent.NewAttrToObtain)):
            parent.IndLocNode+=1
            if(parent.IndLocNode<=NbNodes):
                NewFrame=parent.LaunchNewFrame()
            else:
                if(TypeN=='Reservoirs'):
                    self.parent.TypeN='IncJunctions'
                    NewFrame=self.parent.PrepareNewFrame()
        self.Close()
        self.Destroy()

class Draw_Options(wx.Frame):
    """
    Ouverture d'une nouvelle fenêtre permettant de laisser le choix à l'utilisateur de sélectionner ce qu'il souhaite afficher
    """
    def __init__(self, parent, title,MainW):
      super(Draw_Options, self).__init__(parent, title = title,size = (300,200),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
      #panel = MyPanel(self,MainW)
      #panel = wx.Panel(self)
      vbox = wx.BoxSizer(wx.VERTICAL)

      self.Centre()
      frame_sizer = wx.BoxSizer(wx.VERTICAL)
      #frame_sizer.Add(panel, 1, wx.EXPAND| wx.LEFT | wx.RIGHT, wx.ALIGN_CENTER)
      #Message d'annonce pour savoir ce qui est à réaliser
      Message='What do you want to draw ?'
      self.message = wx.StaticText(self, -1, Message)
      frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
      Choices=['HeadNodes','Altimetry','Discharge','Diameter']
      Name_Box='Draw_Box'
      self.CheckBox = wx.CheckListBox(self, choices=Choices, name=Name_Box)
      frame_sizer.Add(self.CheckBox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT)
      self.SetSizerAndFit(frame_sizer)

      sz2 = wx.BoxSizer(wx.HORIZONTAL)
      #dlg1=sz2.Add(wx.Button(self, wx.ID_OK, ""), 0, wx.ALL, 10)
      self.btn=wx.Button(self,-1,"Ok")
      sz2.Add(self.btn,0, wx.ALL, 10)
      self.btn.Bind(wx.EVT_BUTTON,self.Param_Read)

      #dlg2=sz2.Add(wx.Button(self, wx.ID_CANCEL, ""), 0, wx.ALL, 10)
      self.btn2=wx.Button(self,-1,"Annuler")
      sz2.Add(self.btn2,0, wx.ALL, 10)
      self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

      frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
      self.SetAutoLayout(True)
      self.SetSizerAndFit(frame_sizer)
      self.Show()
      self.CenterOnScreen()
      #self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
      Test=1
      #fdRet = dlgF.ShowModal()
      List_Params=[]

    #L'utilisateur choisit ok, mais on doit bien également s'assurer que des cases ont été cochées pour être capable d'afficher les résultats
    def Param_Read(self, e):
       Test=1
       Parent=self.GetParent()
       Parent.Parent.Items=self.CheckBox.GetCheckedItems()
       #On analyse les items en venant donc extraire les différentes informations disponibles
       if(bool(Parent.Parent.Items)):
            Param_Simul=[0,0,0,0]
            NbTypeResults=len(Parent.Parent.Items)
            for Option in Parent.Parent.Items:
                Param_Simul[Option]=1

            #if(self.Show_Results):
            title='Time step'
            Max_Val=int(Parent.Parent.Param['Time']['Number of time save steps'][0])
            Parent.Parent.Time_Step=1
            Parent.Parent.Param_Simul=Param_Simul
            Parent.Parent.frame = MyFrame_Slider(parent=Parent.Parent, title=title,Max_Val=Max_Val)
            Parent.Parent.canvas2.NewDraw=False
       else:
            Test=1

       Test=1
       self.Close()
       self.Destroy()

    #L'annulation étant choisie par l'utilisateur, l'option est donc levée et la fenêtre est simplement fermée
    def CloseFrame(self, e):
       Test=1
       self.Close()
       self.Destroy()

class ParamToShow(wx.Frame):
    def __init__(self, parent, title):
      super(ParamToShow, self).__init__(parent, title = title,size = (300,200),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
      vbox = wx.BoxSizer(wx.VERTICAL)
      self.Centre()
      frame_sizer = wx.BoxSizer(wx.VERTICAL)
      #frame_sizer.Add(panel, 1, wx.EXPAND| wx.LEFT | wx.RIGHT, wx.ALIGN_CENTER)
      #Message d'annonce pour savoir ce qui est à réaliser
      Message='Which parameters do you want to show ?'
      MainW=parent
      Choices=[]
      NbParam=MainW.cptParam
      for i in range(NbParam):
          Text='Param'+' '+str(i+1)
          Choices.append(Text)
      self.message = wx.StaticText(self, -1, Message)
      frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
      Name_Box='Draw_Box'
      self.CheckBox = wx.CheckListBox(self, choices=Choices, name=Name_Box)
      frame_sizer.Add(self.CheckBox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT)
      self.SetSizerAndFit(frame_sizer)

      sz2 = wx.BoxSizer(wx.HORIZONTAL)
      self.btn=wx.Button(self,-1,"Ok")
      sz2.Add(self.btn,0, wx.ALL, 10)
      self.btn.Bind(wx.EVT_BUTTON,self.Param_Read)

      self.btn2=wx.Button(self,-1,"Annuler")
      sz2.Add(self.btn2,0, wx.ALL, 10)
      self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

      frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
      self.SetAutoLayout(True)
      self.SetSizerAndFit(frame_sizer)
      self.Show()
    #L'utilisateur choisit ok, mais on doit bien également s'assurer que des cases ont été cochées pour être capable d'afficher les résultats
    def Param_Read(self, e):
       Parent=self.GetParent()
       Parent.ItemsParams=self.CheckBox.GetCheckedItems()
       Parent.Nodes['ActivParams']=[0]*(Parent.cptParam)
       for Param in Parent.ItemsParams:
            Parent.Nodes['ActivParams'][Param]=1
            Parent.Show_Param_Results=True
       self.Close()
       self.Destroy()

    #L'annulation étant choisie par l'utilisateur, l'option est donc levée et la fenêtre est simplement fermée
    def CloseFrame(self, e):
       self.Close()
       self.Destroy()

#
class NewEdgeFrame(wx.Frame):
    """
    Frame utilisée pour permettre la mise en place du nouveau élément connecteur
    """
    def __init__(self, title, parent):
       super(NewEdgeFrame, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)

       #Ajout d'un nouveau noeud entraîne à l'activiation du mode d'édition du réseau
       parent.Edition_Mode_Local=True
       #Préparation des données par défaut et des attributs principaux
       MainW=parent
       Index=int(MainW.LocalNode[0])

       self.Main_Attr=['First Node Name','Second Node Name','Name Edge','Type Element(P,V or T)']

       #On vient également compléter par défaut chaque colonne afin que l'utilisateur puisse rapidement uniquement modifier ce qu'il souhaite
       Nb_Edges=1
       if(hasattr(MainW,'Edg_OGL')):
           Nb_Edges=len(MainW.Edg_OGL[1])+1
       Edge_Name='Edge_'+str( Nb_Edges)
       NbNodes=len(MainW.List_Nodes_OGL['NameNode'])
       if(NbNodes<2):
           logging.info('The number of nodes in the network is not sufficient to create links')
       else:
           NameNode1=MainW.List_Nodes_OGL['NameNode'][0]
           NameNode2=MainW.List_Nodes_OGL['NameNode'][1]
           if(hasattr(MainW,'Ident_Nodes')):
               if(bool(MainW.Ident_Nodes)):
                   NameNode1=MainW.Ident_Nodes[0]
                   NameNode2=MainW.Ident_Nodes[1]
           self.Default_Values=[NameNode1,NameNode2,Edge_Name,'P']

           self.Centre()
           frame_sizer = wx.BoxSizer(wx.VERTICAL)
           #frame_sizer.Add(panel, 1, wx.EXPAND| wx.LEFT | wx.RIGHT, wx.ALIGN_CENTER)

           #Message d'annonce pour savoir ce qui est à réaliser
           Message='Characteristics of the new edge'
           self.message = wx.StaticText(self, -1, Message)
           #frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
           frame_sizer.Add(self.message, 0, wx.EXPAND)
           self.parent=parent
           #Partiée à la grille des coordonnées du noeud
           #self.panel = PanelEdge(self,parent)
           self.panel = PanelGeneral(self)
           frame_sizer.Add(self.panel, 1, wx.EXPAND)
           #Partie liée aux choix de validation ou d'annulation
           sz2 = wx.BoxSizer(wx.HORIZONTAL)
           self.btn=wx.Button(self,-1,"Add")
           sz2.Add(self.btn,0, wx.ALL, 10)
           self.btn.Bind(wx.EVT_BUTTON,self.Save_Grid)

           self.btn2=wx.Button(self,-1,"Close")
           sz2.Add(self.btn2,0, wx.ALL, 10)
           self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

           self.btn3=wx.Button(self,-1,"Browse")
           sz2.Add(self.btn3,0, wx.ALL, 10)
           self.btn3.Bind(wx.EVT_BUTTON,self.Browse_Edge)

           frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
           self.SetAutoLayout(True)
           self.SetSizerAndFit(frame_sizer)
           self.Show()
           Test=1

    #Sous-routine utilisée pour extraire de la grille les informations utiles pour la sauvegarde de l'élément
    def Save_Grid(self,e):
        self.Sav_Edge=[]
        self.Sav_Edge.append(self.panel.GridValues[0])
        self.Sav_Edge.append(self.panel.GridValues[1])
        self.Sav_Edge.append(self.panel.GridValues[2])
        self.Sav_Edge.append(self.panel.GridValues[3].upper())
        self.Edge_Extract_Option=1
        self.Saved_Edge()
    #Sous-routine générale utilisée dans le but d'ajouter un élément connecteur supplémentaire au réseau déjà présent
    def Saved_Edge(self):

       Parent=self.GetParent()
       Parent.Browse_Method=False
       Parent.First_Node=[]
       Parent.Last_Node=[]
       #Il faut rechercher les valeurs dans la grille pour ajouter un nouveau noeud en faisant test sur le type de noeud

       self.Main_Attr=['First Node Name','Second Node Name']
       Valid_Test=True
       Node_pos=[]
       Node_pos.append(self.Sav_Edge[0])
       Node_pos.append(self.Sav_Edge[1])
       self.Node_pos=Node_pos
       Info_Edge=[]
       Info_Edge.append(self.Sav_Edge[2])
       self.Type_Edge=['P','T','V','D']
       Name_Edge=['pipe','turbine/pump','valve','deversoir']
       Empl_Node=['Upstream','Downstream']
       Loc_ID=self.Sav_Edge[3]
       Ident_Type=0
       for i in range(len(self.Type_Edge)):
           Loc_ID=Loc_ID.upper()
           if(Loc_ID==self.Type_Edge[i]):
               Info_Edge.append(i)
               Ident_Type=1
       Test=1
       self.Info_Edge=Info_Edge
       if(Ident_Type==1):
           #On va analyser les deux valeurs obtenues pour identifier s'il s'agit bien d'un noeud présent dans le réseau
           #Première analyse est effectuée vis-à-vis des noms disponibles
           TypeNode=['Reservoirs','IncJunctions']
           Func_Expres=['Name']
           Pos_Node=[]
           Attr_Node=[0,0]
           for Attr in range(len(Attr_Node)):
                for Node_Type in TypeNode:
                    Loc_lgth=len(Parent.Nodes[Node_Type])
                    for NameNode in Parent.Nodes[Node_Type]:
                        if(Node_pos[Attr]==NameNode):
                            Attr_Node[Attr]=1
                            Pos_Node.append([])
                            Pos_Node[len(Pos_Node)-1].append(Node_Type)
                            Pos_Node[len(Pos_Node)-1].append(Parent.Nodes[Node_Type][NameNode]['IndPos'])
                            break
                    if(Attr_Node[Attr]==1):
                        break
           if(Attr_Node[0]==1 and Attr_Node[1]==1):
                self.Pos_Nodo=Pos_Node
                #On doit en réalité un nouveau subPanel pour permettre à l'utilisateur de renseigner l'ensemble des paramètres liés
                #à la catégorie d'éléments (pipes, pump ou valve)
                if(self.Edge_Extract_Option==1):
                    self.Name_Edge=Name_Edge
                    self.Info_Edge=Info_Edge
                    self.Type_Simulation=1
                    New_frame=NewSubEdgeFrame('Characteristics of the'+Name_Edge[Info_Edge[1]],self)
                else:
                    self.Ident_Coordinates()
                    self.SaveValidEdge()
           else:
                #Noms proposés par l'utilisateur ne sont pas conformes : on vérifie lesquels en premier lieu
                for Id_Node in range(2):
                    if(Attr_Node[Id_Node]==0):
                        Message=Empl_Node[Id_Node]+' Node is not présent in '+Node_pos[0]
                        logging.info(Message)

                self.Centre()
                self.Show()
                Valid_Test=False
       else:
           logging.info('Le type de l élément n est pas valide')
       return Test
            #Remplacement via les données réelles

    #Sous-routine ayant pour but de récupérer les coordonnées des noeuds extrême d'un élément connecteur du réseau
    def Ident_Coordinates(self):
        Parent=self.GetParent()
        self.CoordNodes=[]
        Coord_Tot=[0,0]
        Coordinates=[0.0,0.0]
        for cpt_pos in range(len(self.Pos_Nodo)):
            Node_Type=self.Pos_Nodo[cpt_pos][0]
            Coordinates[0]=Coordinates[0]+Parent.Nodes[Node_Type][self.Node_pos[cpt_pos]]['CoordPlan'][0]/2.0
            Coordinates[1]=Coordinates[1]+Parent.Nodes[Node_Type][self.Node_pos[cpt_pos]]['CoordPlan'][1]/2.0
            CoordX=Parent.Nodes[Node_Type][self.Node_pos[cpt_pos]]['CoordPlan'][0]
            CoordY=Parent.Nodes[Node_Type][self.Node_pos[cpt_pos]]['CoordPlan'][1]
            CoordZ=Parent.Nodes[Node_Type][self.Node_pos[cpt_pos]]['CoordZ']
            Coord_Tot[cpt_pos]=(CoordX,CoordY,CoordZ)
        self.Coord_Tot=Coord_Tot
        self.Coordinates=Coordinates

    #On fait l'ajout si uniquement toutes les conditions sont respectées pour le faire
    def SaveValidEdge(self):
        Test=1
        Parent=self.GetParent()
        Nb_Zones=4
        if(hasattr(Parent,'Edg_OGL')):
            Nb_Zones=4
            if(len(Parent.Edg_OGL[2])<Nb_Zones):
                Nb_Missing_Zones=Nb_Zones-len(Parent.Edg_OGL[2])
                for i in range(Nb_Missing_Zones):
                    Parent.Edg_OGL[2].append(0)
            #Nb de vecteurs liés à la catégorie du nouvel élément connecteur ajouté
            Coord=(self.Coordinates[0],self.Coordinates[1])
            Nb_cat_edges=Parent.Edg_OGL[2][self.Info_Edge[1]]
            Parent.Edg_OGL[2][self.Info_Edge[1]]+=1

            #On a aussi un compteur d'élément au sein du réseau
            if(bool(Parent.List_Nodes_OGL['PosVec'])):
                Nb_Vec=Parent.List_Nodes_OGL['PosVec'][-1]+1
            else:
                Nb_Vec=0
            for cpt_pos in range(len(self.Pos_Nodo)):
                Parent.List_Nodes_OGL['NbrElVec'].append(Nb_cat_edges)
                Parent.List_Nodes_OGL['IdZone'].append(self.Info_Edge[1])
                Parent.List_Nodes_OGL['VecCoord'].append(Coord)
                Parent.List_Nodes_OGL['PosVec'].append(Nb_Vec)
                Parent.Modif_Nodes=True
        else:
            Parent.Edg_OGL=[[],[],[],[],[]]
            Nb_cat_edges=0
            for i in range(Nb_Zones):
                Parent.Edg_OGL[2].append(0)
            Parent.Edg_OGL[2][self.Info_Edge[1]]+=1
        Posit_Node=(self.Pos_Nodo[0][1]+1,self.Pos_Nodo[1][1]+1)
        Parent.Edg_OGL[0].append(Posit_Node)
        Parent.Edg_OGL[1].append(Nb_cat_edges)
        Parent.Edg_OGL[3].append(self.Info_Edge[1])
        Parent.Edg_OGL[4].append(0)
        Parent.Modif_Edges=True
        #Il y a également la partie liée aux Zones qu'il faut donc également compléter
        NB_vertex=2
        Id_Zone=self.Info_Edge[1]
        Parent.Zones[Id_Zone]['NbrVec']+=1
        Parent.Zones[Id_Zone]['Name'].append(self.Info_Edge[0])
        Parent.Zones[Id_Zone]['NbrVertex'].append(NB_vertex)
        Parent.Zones[Id_Zone]['Coord'][0].append([])
        Parent.Zones[Id_Zone]['Coord'][1].append([])
        Parent.Zones[Id_Zone]['Coord'][2].append([])
        if('Value' in Parent.Zones[Id_Zone]):
            Parent.Zones[Id_Zone]['Value'].append(['0.0'])
        Length=len(Parent.Zones[Id_Zone]['Coord'][0])-1
        for j in range(NB_vertex):

            Parent.Zones[Id_Zone]['Coord'][0][Length].append(str(self.Coord_Tot[j][0]))
            Parent.Zones[Id_Zone]['Coord'][1][Length].append(str(self.Coord_Tot[j][1]))
            Parent.Zones[Id_Zone]['Coord'][2][Length].append(str(self.Coord_Tot[j][2]))
        test=1
        Parent.First_Node=[]
        Parent.Last_Node=[]
        #On vient reset du coup également la grille pour que la valeur par défaut repasse au noeud suivant
        DfltName='Edge_'+str(Nb_cat_edges+2)
        MyPanel=self.panel
        MyPanel.thegrid.SetCellValue(2,0, DfltName)

    #L'annulation étant choisie par l'utilisateur, l'option est donc levée et la fenêtre est simplement fermée
    def CloseFrame(self, e):
       Test=1
       Main=self.GetParent()
       if(Main.NewNetwork):
           #On lance l'affichage du réseau vu que noeud et lien ont été établis
           Main.Zones,Main.Nodes=Add_Main_Attributes(Main.Zones,Main.Nodes)
           Main.NewNetwork=False
           Main.Network_To_Show()
           Test=1
       self.Close()
       self.Destroy()

    #Permet de plutôt implémenter les tronçon via la structure des noeuds plutôt que les coordonnées
    def Browse_Edge(self, e):

        Test=1
        ext='.txt'
        pathfile=self.OnOpen(ext)
        Main=self.GetParent()
        TypeNode=['Reservoirs','IncJunctions']
        Message=['Upstream','Downstream']
        IERR=0
        if(pathfile!='X'):
            #On a bien un fichier valide à lire
            Test=1
            if(os.path.isfile(pathfile)):
                NbNodes=len(Main.Nodes)
                self.Edge_Extract_Option=0
                Ind_Name=[]
                for IndexName in range(NbNodes):
                    Ind_Name.append(str(IndexName+1))
                #file = open(pathfile,'r')
                with open(pathfile) as f:
                    content = f.readlines()
                #La structure du fichier est la suivante avec chaque ligne : type élément, nom élément, nom du noeud amont, nom du noeud aval
                for New_Word in content:
                    Loc_Type=['X','X']
                    New_Word=New_Word.rstrip('\n')
                    Words=re.split(r'\,', New_Word)
                    if(len(Words)!=4):
                        logging.info('Wrong number of arguments')
                        IERR=-1
                        break
                    self.Sav_Edge=['X','X','X','X']
                    self.Sav_Edge[3]=Words[0].upper()
                    self.Sav_Edge[2]=Words[1]
                    self.Sav_Edge[0]=Words[2]
                    self.Sav_Edge[1]=Words[3]
                    self.Saved_Edge()
        #Deuxième partie liée à la lecture des attributs si la première partie s'est bien déroulée
        if(IERR==0):
            Parent=self.GetParent()
            Parent.Browse_Method=True
            pathAttrib=self.OnOpenAttributes()
            pathAttrib=pathAttrib+'\\'
            if(pathAttrib!='X\\'):
                #On va chercher les attributs dans le dossier
                Test=1
                List_Attr=[[],[],[],[]] #Liste des catégories d'attributs à utiliser
                Subm_Attr=[[],[],[],[]] #Liste des catégories d'attributs potentiellement proposées à l'utilisateur
                Subm_Attr[0]=['Length[m]','Diameter[m]','Material','Coef_Rough[-]','Init_Cond[m³/s]']
                Subm_Attr[1]=['Length[m]','Type law','Nb_Coefficients','Init_Cond[m³/s]']
                Subm_Attr[2]=['Length[m]','Height[m]','Width[m]','Type Valve','Init_Cond[m³/s]']
                List_Attr[0]=['Length','Diameter','Material','Rough_Coeff','IC_Cond']
                List_Attr[1]=['Length','Type_Law','Nb_Coefficients','IC_Cond']
                List_Attr[2]=['Length','Height','Width','Type_Valve','IC_Cond']
                self.Dft_Categ=[[],[],[]]
                self.Dft_Categ[0]=['1.0','0.5','Steel','1.E-5','0.0']
                self.Dft_Categ[1]=['1.0','1','3','0.0']
                self.Dft_Categ[2]=['2,0','1.0','1.0','Aiguille','0.0']
                Attr_File=[[],[],[]]
                Attr_File[0]=['Length.D','Diameter.D','Material.S','Rugosity.D','IC_Vector.D']
                Attr_File[1]=[]
                Attr_File[2]=['Length_valve.D','Height.D','Width.D','Type_of_Valve.S','IC_Vector.D']
                Found_Files=[[],[],[],[]]
                Zones=Main.Zones
                #Analyse pour les canalisations
                Zones,Found_Files[0]=Add_Vector_Attributes(Zones,pathAttrib,List_Attr[0],Attr_File[0])
                #Analyse pour les pompes
                Zones,Found_Files[1]=Add_Spec_Vec_Attributes(Zones,pathAttrib)
                #Analyse pour les valves
                Zones,Found_Files[2]=Add_Vector_Attributes(Zones,pathAttrib,List_Attr[2],Attr_File[2])
                Found_Files[3]=[1]
                #On va également rechercher à sauvegarder l'ensemble des résultats sur les différents pas de temps du réseau
                Zones=Add_Vector_Time(Zones,pathAttrib,Main.Param)
                #On s'intéresse notamment à la partie found_files pour ajouter l'ensemble des attributs ne se trouvant pas dans le dossier d'attributs pour que l'auteur ajoute
                #progressivement chaque attribut manquant
                self.Main_Attr=[[],[],[],[]]
                self.Info_Edge=[0,0]
                cpt_attrib=0
                self.Type_Simulation=2
                self.Found_Files=Found_Files
                #On ajoute les attributs automatiques qui n'auraient pas été identifiés dans le dossier fourni par l'utilisateur
                for IdZone in range(len(Zones)):
                    cpt_attrib=0
                    self.Main_Attr[IdZone].append('Name')
                    for Attr in Found_Files[IdZone]:
                        if(Attr==0):
                            self.Main_Attr[IdZone].append(Subm_Attr[IdZone][cpt_attrib])
                        cpt_attrib+=1
                Test=1
                #Première étape liée à l'initialisation des éléments
                self.Attr_El=[[],[],[]]
                for IdZone in range(len(Zones)):
                    for NameVec in Zones[IdZone]['Name']:
                        self.Attr_El[IdZone].append(0)
                cpt_elem=0
                for IdZone in range(len(Zones)):
                    self.Default_Values=[]
                    for NameVec in Zones[IdZone]['Name']:
                        if(cpt_elem==0):
                            self.Attr_El[IdZone][cpt_elem]=1
                            cpt_elem+=1
                            self.Info_Edge[1]=IdZone
                            self.Name_Edge=NameVec
                            self.Default_Values.append(NameVec)
                            cpt_attrib=0
                            Unknown_Param=False
                            for Attr in Found_Files[IdZone]:
                                if(Attr==0):
                                    self.Default_Values.append(self.Dft_Categ[IdZone][cpt_attrib])
                                    Unknown_Param=True
                                cpt_attrib+=1
                            self.Type_Edge=IdZone
                            if(Unknown_Param):
                                New_frame=NewSubEdgeFrame('Characteristics of the '+NameVec,self)



    def OnOpen(self,ext):
        Message='Choose the '+ext+' file'
        namepath='X'
        dlg = wx.FileDialog(self, Message,
                           defaultDir = "",
                           defaultFile = "",
                           wildcard = "*")
        if dlg.ShowModal() == wx.ID_OK:
            namepath=dlg.GetPath()
            t=1
        dlg.Destroy()
        return namepath

    def OnOpenAttributes(self):
        namepath='X'
        dlg = wx.DirDialog(self, "Choose the directory of attributes")
        if dlg.ShowModal() == wx.ID_OK:
            namepath=dlg.GetPath()
            t=1
        dlg.Destroy()
        return namepath
    def OnClickNewNode(self, e):
        type_event=e.button
        xdata=e.xdata
        ydata=e.ydata
        self.LocNode=(e.xdata,e.ydata)
        self.type_click=e.button
    #Procédure liée à la mise en place d'un nouveau edge
    def Prepare_New_Frame(self):
        New_Elem_To_Define=True
        Main=self.GetParent()
        Zones=Main.Zones
        Found_Files=self.Found_Files

        for IdZone in range(len(Zones)):
            self.Default_Values=[]
            cpt_elem=0
            for NameVec in Zones[IdZone]['Name']:
                if(self.Attr_El[IdZone][cpt_elem]==0 and New_Elem_To_Define):
                    New_Elem_To_Define=False
                    self.Attr_El[IdZone][cpt_elem]=1
                    self.Info_Edge[1]=IdZone
                    self.Name_Edge=NameVec
                    self.Default_Values.append(NameVec)
                    cpt_attrib=0
                    Unknown_Param=False
                    for Attr in Found_Files[IdZone]:
                        if(Attr==0):
                            Unknown_Param=True
                            self.Default_Values.append(self.Dft_Categ[IdZone][cpt_attrib])
                        cpt_attrib+=1
                    self.Type_Edge=IdZone
                    if(Unknown_Param):
                        New_frame=NewSubEdgeFrame('Characteristics of the '+NameVec,self)
                cpt_elem+=1
        if(New_Elem_To_Define):
            Parent=self.GetParent()
            Parent.Browse_Method=False

#
class NewSubEdgeFrame(wx.Frame):
    """
    Frame utilisée pour ajouter les paramètres propres à chaque catégorie d'élément connecteur
    """
    def __init__(self, title, parent):
       super(NewSubEdgeFrame, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)

        #Initialisation de la grille = évaluation du nombre d'attributs à afficher
        #Les attributs dépendent du type d'élément qui est ajouté par l'utilisateur
       self.parent=parent
       Type_Simulation=parent.Type_Simulation
       if(Type_Simulation==1):
           self.Name_Edge=parent.Name_Edge[parent.Info_Edge[1]]
           self.Type_Edge=parent.Info_Edge[1]
           Type_El=self.Type_Edge
       else:
           self.Name_Edge=parent.Name_Edge
           Type_El=parent.Type_Edge
       self.MainW=parent.GetParent()
       if(Type_Simulation==1):
           if(Type_El==0):
                self.Main_Attr=['Length[m]','Diameter[m]','Material','Coef_Rough[-]','Init_Cond[m³/s]']
                self.Default_Values=['0.0','0.5','Steel','1.E-5','0.0']
           if(Type_El==1):
                self.Main_Attr=['Length[m]','Type law','Nb_Coefficients','Init_Cond[m³/s]']
                self.Default_Values=['1.0','1','3','0.0']
           if(Type_El==2):
                self.Main_Attr=['Length[m]','Height[m]','Width[m]','Type Valve','Init_Cond[m³/s]']
                self.Default_Values=['2,0','0.0','1.0','Aiguille','0.0']
       else:
            self.Main_Attr=parent.Main_Attr[parent.Type_Edge]
            self.Default_Values=parent.Default_Values
       #L'attribut de longueur peut être évalué sur base de la distance entre les deux noeuds reliés
       self.parent.Ident_Coordinates()
       #Current_El=self.MainW.Zones[Type_El]
       #Last_El=len(Current_El['Name'])-1
       #NbVertex=len(Current_El['Coord'][0][Last_El])-1
       Length=0.0
       for i in range(2):
           Coord1=self.parent.Coord_Tot[0][i]#float(Current_El['Coord'][i][Last_El][0])
           Coord2=self.parent.Coord_Tot[1][i]#float(Current_El['Coord'][i][Last_El][NbVertex])
           Length+=(Coord1-Coord2)**2
       Length=Length**0.5
       cpt_attrib=0
       for Attr in self.Main_Attr:
           if(Attr=='Length[m]'):
                self.Default_Values[cpt_attrib]=str(Length)
           cpt_attrib+=1

       self.Centre()
       frame_sizer = wx.BoxSizer(wx.VERTICAL)

       #Message d'annonce pour savoir ce qui est à réaliser
       Message='Characteristics of the '+self.Name_Edge
       self.message = wx.StaticText(self, -1, Message)
       #frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
       frame_sizer.Add(self.message, 0, wx.EXPAND)
       #Partiée à la grille des coordonnées du noeud
       self.panel = PanelGeneral(self)
       frame_sizer.Add(self.panel, 1, wx.EXPAND)
       #Partie liée aux choix de validation ou d'annulation
       sz2 = wx.BoxSizer(wx.HORIZONTAL)
       self.btn=wx.Button(self,-1,"Ok")
       sz2.Add(self.btn,0, wx.ALL, 10)
       self.btn.Bind(wx.EVT_BUTTON,self.Saved_char_Edge)

       self.btn2=wx.Button(self,-1,"Close")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

       frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
       self.SetAutoLayout(True)
       self.SetSizerAndFit(frame_sizer)
       self.Show()
       Test=1

    #L'annulation étant choisie par l'utilisateur, l'option est donc levée et la fenêtre est simplement fermée
    def CloseFrame(self, e):
       Test=1
       self.Close()
       self.Destroy()

       #On va donc replacer l'ensemble des informations obtenues pour le réseau
    def Saved_char_Edge(self,e):
        if(self.parent.Edge_Extract_Option==1):
            self.parent.SaveValidEdge()
        Test=1
        List_Attr=[[],[],[],[]] #Liste des catégories d'attributs à utiliser
        Subm_Attr=[[],[],[],[]] #Liste des catégories d'attributs potentiellement proposées à l'utilisateur
        Link_Attr=[[],[],[],[]] #Procédé de numérotation indirecte pour directement faire le lien entre 2 parties
        Subm_Attr[0]=['Diameter[m]','Length[m]','Coef_Rough[-]','Material','Init_Cond[m³/s]']
        Subm_Attr[1]=['Length[m]','Type law','Nb_Coefficients','Init_Cond[m³/s]']
        Subm_Attr[2]=['Length[m]','Height[m]','Width[m]','Type Valve','Init_Cond[m³/s]']
        Link_Attr[0]=[1,0,3,2,4]
        Link_Attr[1]=[0,1,2,3]
        Link_Attr[2]=[0,1,2,3,4,5,6]
        List_Attr[0]=['Length','Diameter','Material','Rough_Coeff','IC_Cond']
        List_Attr[1]=['Length','Type_Law','Nb_Coefficients','IC_Cond']
        List_Attr[2]=['Length','Height','Width','Type_Valve','IC_Cond']
        self.MainW.Saved_Network=False
        Auto_Destroy=True
        for IDList in range(len(List_Attr)):
            NbAttributes=self.panel.thegrid.GetNumberRows()
            Prop_Attr=[]
            for Loc_Attrib in range(NbAttributes):
                Prop_Attr.append(self.panel.thegrid.GetRowLabelValue(Loc_Attrib))
            #GetRowLabelValue
            if(self.parent.Info_Edge[1]==IDList):
               #Il s'agit bien d'un pipe
               PosElem=len(self.MainW.Zones[IDList]['Name'])-1
               cpt_val=0
               for Loc_Attrib in Prop_Attr:
                   ID=Subm_Attr[IDList].index(Loc_Attrib)
                   NameAttr=List_Attr[IDList][Link_Attr[IDList][ID]]
                   if(Loc_Attrib in Subm_Attr[IDList] and NameAttr in self.MainW.Zones[IDList]):
                       self.MainW.Zones[IDList][NameAttr].append(self.panel.GridValues[cpt_val])
                   cpt_val+=1
               if(IDList==1):
                    #Ajout de la partie supplémentaire liée à la pompe/turbine pour ajouter ensemble des paramètres selon type de loi
                    Test=1
                    self.Name_Edge=self.MainW.Zones[IDList]['Name'][PosElem]
                    self.Info_Edge=self.parent.Info_Edge
                    New_frame=NewSubPumpFrame('Coefficients of the pump '+self.Name_Edge,self)
                    Auto_Destroy=False
               if(IDList==2):
                    self.MainW.Zones[IDList]['Type_Valve'][-1]=self.MainW.Zones[IDList]['Type_Valve'][-1].lower()
                    self.MainW.Zones[IDList]['Coeff_Valve'].append([])
                    if(self.MainW.Zones[IDList]['Type_Valve'][-1]=='aiguille'):
                        #Ajout de la partie supplémentaire liée à la valve pour ajouter les paramètres liés à la loi de fonctionnement de valve
                        Test=1
                        self.Name_Edge=self.MainW.Zones[IDList]['Name'][PosElem]
                        self.Info_Edge=self.parent.Info_Edge
                        New_frame=NewSubValveFrame('Coefficients of the valves '+self.Name_Edge,self)
                        Auto_Destroy=False


        #self.Close()
        #Dans le cadre d'une "Procédure browse" amenant l'implémentation de multiples éléments, on est amené à relancer
        if(self.MainW.Browse_Method):
            self.parent.Prepare_New_Frame()
        Test=1
        if(Auto_Destroy):
            self.Close()
            self.Destroy()

#
class NewSubPumpFrame(wx.Frame):
    """
    Frame utilisée pour ajouter les coefficients propres à une nouvelle pompe placée dans le réseau selon type de pompe
    """
    def __init__(self, title, parent):
       super(NewSubPumpFrame, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
       #Préparation de l'initialisation du panel
       self.parent=parent
       MainEdge=parent.GetParent()
       self.MainW=MainEdge.parent

       #Initialisation de la grille = évaluation du nombre d'attributs à afficher
       #Les attributs dépendent du type d'élément qui est ajouté par l'utilisateur
       self.ID_Pump=len(self.MainW.Zones[1]['Name'])-1
       Type_Law=int(self.MainW.Zones[1]['Type_Law'][self.ID_Pump])
       if(Type_Law==2):
            #Loi de type H=A-B*Q^C
           self.Main_Attr=[]
           self.Default_Values=[]
       if(Type_Law<0):
           #Loi avec utilisation de sigmoïde H=1/(1+exp(-kh*Q/Qb)+(A*(Q/Qb)^x+B*Q^(x-1)+...
           self.Main_Attr=['Qb[m³/s]','kH','kP']
           self.Default_Values=['1.0','1.0','3.0']
        #On ajoute des valeurs de base aux coefficients
       Nb_Coeffs=int(self.MainW.Zones[1]['Nb_Coefficients'][self.ID_Pump])
       for i in range(Nb_Coeffs):
            self.Main_Attr.append('Coeff_H'+str(i+1))
            self.Default_Values.append('0.0')
       for i in range(Nb_Coeffs):
            self.Main_Attr.append('Coeff_P'+str(i+1))
            self.Default_Values.append('0.0')

       self.Centre()
       frame_sizer = wx.BoxSizer(wx.VERTICAL)
       #frame_sizer.Add(panel, 1, wx.EXPAND| wx.LEFT | wx.RIGHT, wx.ALIGN_CENTER)
       self.Name_Edge=parent.Name_Edge
       #Message d'annonce pour savoir ce qui est à réaliser
       Message='Coefficients of the pump '+parent.Name_Edge
       self.message = wx.StaticText(self, -1, Message)
       #frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
       frame_sizer.Add(self.message, 0, wx.EXPAND)
       #Partiée à la grille des coordonnées du noeud
       self.panel = PanelGeneral(self)
       frame_sizer.Add(self.panel, 1, wx.EXPAND)
       #Partie liée aux choix de validation ou d'annulation
       sz2 = wx.BoxSizer(wx.HORIZONTAL)
       self.btn=wx.Button(self,-1,"Ok")
       sz2.Add(self.btn,0, wx.ALL, 10)
       self.btn.Bind(wx.EVT_BUTTON,self.Saved_Coef_Pumps)

       self.btn2=wx.Button(self,-1,"Close")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

       frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
       self.SetAutoLayout(True)
       self.SetSizerAndFit(frame_sizer)
       self.Show()
       Test=1

    #L'annulation étant choisie par l'utilisateur, l'option est donc levée et la fenêtre est simplement fermée
    def CloseFrame(self, e):
       Test=1
       self.Close()
       self.Destroy()

       #On va donc replacer l'ensemble des informations obtenues pour la pompe étudiée
    def Saved_Coef_Pumps(self,e):
        Test=1
        Nb_Coeffs=int(self.MainW.Zones[1]['Nb_Coefficients'][self.ID_Pump])
        self.MainW.Zones[1]['Coeff_H']=[]
        for IDCoeff in range(Nb_Coeffs):
            self.MainW.Zones[1]['Coeff_H'].append(self.panel.GridValues[IDCoeff])
        self.MainW.Zones[1]['Coeff_P']=[]
        for IDCoeff in range(Nb_Coeffs):
            self.MainW.Zones[1]['Coeff_P'].append(self.panel.GridValues[Nb_Coeffs+IDCoeff])

        self.parent.Close()
        self.parent.Destroy()

        #Frame utilisée pour ajouter les coefficients propres à une nouvelle pompe placée dans le réseau selon type de pompe

#
class NewSubValveFrame(wx.Frame):
    """
    Sous-routine liée à la mise en place des coefficients de fonctionnement de chaque valve
    """
    def __init__(self, title, parent):
       super(NewSubValveFrame, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
       #Préparation de l'initialisation du panel
       self.parent=parent
       MainEdge=parent.GetParent()
       self.MainW=MainEdge.parent

       #Initialisation de la grille = évaluation du nombre d'attributs à afficher
       #Les attributs dépendent du type d'élément qui est ajouté par l'utilisateur
       self.ID_Valve=len(self.MainW.Zones[2]['Name'])-1
       Type_Valve=self.MainW.Zones[2]['Type_Valve'][self.ID_Valve]
       Type_Valve=Type_Valve.lower()
       if(Type_Valve=='aiguille'):
           #Loi avec utilisation de DeltaH=a*(C_Ouv)**b
           self.Main_Attr=['a','b']
           self.Nb_Coeffs=2
           self.Default_Values=['1.0','2.0']

       self.Centre()
       frame_sizer = wx.BoxSizer(wx.VERTICAL)
       #frame_sizer.Add(panel, 1, wx.EXPAND| wx.LEFT | wx.RIGHT, wx.ALIGN_CENTER)
       self.Name_Edge=parent.Name_Edge
       #Message d'annonce pour savoir ce qui est à réaliser
       Message='Coefficients of the valve '+parent.Name_Edge
       self.message = wx.StaticText(self, -1, Message)
       #frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
       frame_sizer.Add(self.message, 0, wx.EXPAND)
       #Partiée à la grille des coordonnées du noeud
       self.panel = PanelGeneral(self)
       frame_sizer.Add(self.panel, 1, wx.EXPAND)
       #Partie liée aux choix de validation ou d'annulation
       sz2 = wx.BoxSizer(wx.HORIZONTAL)
       self.btn=wx.Button(self,-1,"Ok")
       sz2.Add(self.btn,0, wx.ALL, 10)
       self.btn.Bind(wx.EVT_BUTTON,self.Saved_Coef_Valves)

       self.btn2=wx.Button(self,-1,"Close")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

       frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
       self.SetAutoLayout(True)
       self.SetSizerAndFit(frame_sizer)
       self.Show()
       Test=1

    #L'annulation étant choisie par l'utilisateur, l'option est donc levée et la fenêtre est simplement fermée
    def CloseFrame(self, e):
       Test=1
       self.Close()
       self.Destroy()

       #On va donc replacer l'ensemble des informations obtenues pour la pompe étudiée
    def Saved_Coef_Valves(self,e):
        Test=1
        for IDCoeff in range(self.Nb_Coeffs):
            self.MainW.Zones[2]['Coeff_Valve'][-1].append(self.panel.GridValues[IDCoeff])

        self.parent.Close()
        self.parent.Destroy()

 #Création de la grille permettant l'implémentation des coefficients de la pompe selon type de loi

class PanelGeneral(wx.Panel):

    def __init__(self, parent):
        super(PanelGeneral, self).__init__(parent)

        self.Main_Attr=parent.Main_Attr
        Default_Values=parent.Default_Values
        Nb_attrib=len(self.Main_Attr)

        #Mise en place de la grille + colonne
        mygrid = grid.Grid(self)
        mygrid.CreateGrid( Nb_attrib, 1)
        mygrid.SetColLabelValue(0, "Value")
        #On vient afficher l'ensemble des données utiles pour le noeud
        cpt_row=0

        #Remplissage du tableau
        cpt_row=0
        self.GridValues=[]
        for Attr in self.Main_Attr:
            mygrid.SetRowLabelValue(cpt_row,Attr)
            mygrid.SetCellAlignment(cpt_row, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            mygrid.SetCellValue(cpt_row,0, Default_Values[cpt_row])
            self.GridValues.append(Default_Values[cpt_row])
            cpt_row=cpt_row+1
        #mygrid.AutoSizeColumns(False)
        mygrid.SetRowLabelSize(150)
        mygrid.EnableDragGridSize(True)
        mygrid.SetColSize(0,100)
        #mygrid.AutoSize()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(mygrid, 1, wx.EXPAND)
        self.thegrid=mygrid
        self.SetSizer(sizer)
        #self.SetSizerAndFit(sizer)
        Test=1
        self.modified_grid=False
        self.thegrid.Bind(grid.EVT_GRID_CELL_CHANGED, self.Saved_Modifications)

    def Saved_Modifications(self,e):
        self.modified_grid=True
        #Sauvegarde des valeurs de la grille
        Nb_Rows=self.thegrid.GetNumberRows()
        self.GridValues=[]
        for Row in range(Nb_Rows):
            self.GridValues.append(self.thegrid.GetCellValue(Row,0))


#
class NewPatternFrame2(wx.Frame):
    """
    Frame utilisée pour permettre la mise en place du nouveau pattern
    """
    def __init__(self, title, parent):
       super(NewPatternFrame2, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
       #Ajout d'un nouveau noeud entraîne à l'activiation du mode d'édition du réseau
       parent.Edition_Mode_Local=True

       self.Centre()
       frame_sizer = wx.BoxSizer(wx.VERTICAL)
       #frame_sizer.Add(panel, 1, wx.EXPAND| wx.LEFT | wx.RIGHT, wx.ALIGN_CENTER)

       #Message d'annonce pour savoir ce qui est à réaliser
       Message='Characteristics of the new Pattern'
       self.message = wx.StaticText(self, -1, Message)
       #frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
       frame_sizer.Add(self.message, 0, wx.EXPAND)

       #Partie liée à l'ajout des informations du Pattern
       self.panel = PanelPattern(self,parent)
       frame_sizer.Add(self.panel, 1, wx.EXPAND)
       #Partie liée aux choix de validation ou d'annulation
       sz2 = wx.BoxSizer(wx.HORIZONTAL)
       self.btn=wx.Button(self,-1,"Ok")
       sz2.Add(self.btn,0, wx.ALL, 10)
       self.btn.Bind(wx.EVT_BUTTON,self.Saved_Pattern)

       self.btn2=wx.Button(self,-1,"Annuler")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

       frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
       self.SetAutoLayout(True)
       self.SetSizerAndFit(frame_sizer)
       self.Show()
       Test=1

    #Sous-routine utilisée dans le but d'ajouter un élément connecteur supplémentaire au réseau déjà présent
    def Saved_Pattern(self, e):
        Test=1
    #L'annulation étant choisie par l'utilisateur, l'option est donc levée et la fenêtre est simplement fermée
    def CloseFrame(self, e):
       Test=1
       self.Close()
       self.Destroy()
 #Création de la grille permettant l'affichage des principaux attributs pour un vecteur

class PanelPattern(wx.Panel):
    def __init__(self, parent,MainW):
        super(PanelPattern, self).__init__(parent)

#
class GenParamFrame(wx.Frame):
    """
    Frame utilisée pour permettre la mise en évidence des paramètres généraux actuels de résolution
    """
    def __init__(self, title, parent):
       super(GenParamFrame, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
       #Ajout d'un nouveau noeud entraîne à l'activiation du mode d'édition du réseau
       parent.Edition_Mode_Local=True

       vbox = wx.BoxSizer(wx.VERTICAL)

       self.Centre()
       frame_sizer = wx.BoxSizer(wx.VERTICAL)
       #frame_sizer.Add(panel, 1, wx.EXPAND| wx.LEFT | wx.RIGHT, wx.ALIGN_CENTER)

       #Message d'annonce pour savoir ce qui est à réaliser
       Message='General parameters of the Network'
       self.message = wx.StaticText(self, -1, Message)
       frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)

       #Partiée liée à l'affichage des informations du pattern (menu défilant ?)
       self.panel = PanelParams(self,parent)
       frame_sizer.Add(self.panel, 1, wx.EXPAND)
       #Partie liée aux choix de validation ou d'annulation
       sz2 = wx.BoxSizer(wx.HORIZONTAL)

       self.btn2=wx.Button(self,-1,"Save Modifications")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.SaveModifications)

       self.btn2=wx.Button(self,-1,"Annuler")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

       frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
       self.SetAutoLayout(True)
       self.SetSizerAndFit(frame_sizer)
       self.Show()


   #L'annulation étant choisie par l'utilisateur, la fenêtre est simplement fermée
    def CloseFrame(self, e):
       self.Close()
       self.Destroy()
   #La sauvegarde des modifications réalisées au sein des paramètres généraux sont effectuées
    def SaveModifications(self, e):
       MainW=self.Parent
       #Si modifications enregistrées, on va les remplacer
       cpt_type=0
       for NameParam in MainW.Param:
           cpt_subparam=0
           for NameSubParam in MainW.Param[NameParam]:
                Entry=self.panel.list_ctrl_params[cpt_type].GetItem(cpt_subparam,0)
                Val=self.panel.list_ctrl_params[cpt_type].GetItem(cpt_subparam,1)
                Value=Val.Text
                cpt_special=0
                Entry=Entry.Text
                for Loc_Comment in Special_Entries:
                    if(Loc_Comment==Entry):
                        cpt_entry=0
                        Attr_Entry=False
                        for Entries in Translation_Entry[cpt_special][1]:
                            #On modifie également la valeur afin qu'elle colle à la forme voulue
                            if(Entries == Value):
                                Attr_Entry=True
                                Value=Translation_Entry[cpt_special][0][cpt_entry]
                                break
                            cpt_entry += 1
                        if(not(Attr_Entry)):
                            Value=Dft_Param[cpt_special]
                            #L'entrée soumise n'est donc pas valide : il faut prévenir l'utilisateur
                            Dial='The following entry :'+Entry+' is wrong. Default parameter is applied'
                            dlg = wx.MessageDialog(
                                None, Dial, "Wrong Entry", wx.OK | wx.CENTRE
                            )
                            result = dlg.ShowModal()
                            self.Centre()
                            self.Show()
                            if result == wx.ID_YES:
                                Test=1
                                self.Destroy()
                            Test=1
                    cpt_special += 1
                MainW.Param[NameParam][NameSubParam][0]=Value
                test=1
                cpt_subparam += 1
           cpt_type += 1
       test=1

#
class PanelParams(wx.Panel):
    """
    Création de la grille permettant l'affichage des principaux attributs du réseau
    """

    def __init__(self, parent,MainW):
        super(PanelParams, self).__init__(parent)

        #Initialisation des grilles liées à chaque dossier important : paramètres généraux, temps et optimisation
        self.list_ctrl_params = [0,0,0]
        for i in range(len(self.list_ctrl_params)):
            self.list_ctrl_params[i] = EditableListCtrl(self, MainWindow=MainW, style=wx.LC_REPORT)
            self.list_ctrl_params[i].InsertColumn(0, "Param")
            self.list_ctrl_params[i].InsertColumn(1, "Value")
            self.list_ctrl_params[i].InsertColumn(2, "Comment")
        #Compléter première colonne selon les différents paramètres généraux qui sont repris dans la liste
        row_position=[1,2]
        cpt_type=0
        for NameParam in MainW.Param:
            index=0
            for NameSubParam in MainW.Param[NameParam]:
                self.list_ctrl_params[cpt_type].InsertItem(index,NameSubParam)
                ValParam=MainW.Param[NameParam][NameSubParam][0]
                Comment=MainW.Param[NameParam][NameSubParam][1]
                ValParam,Comment=self.Apply_ValueTreatment(ValParam,Comment,NameSubParam)
                self.list_ctrl_params[cpt_type].SetItem(index, row_position[0], ValParam)
                self.list_ctrl_params[cpt_type].SetItem(index, row_position[1], Comment)
                index += 1
            cpt_type += 1
        #Pour les valeurs
        sizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(len(self.list_ctrl_params)):
            sizer.Add(self.list_ctrl_params[i], 0, wx.ALL|wx.EXPAND)
            for j in range(3):
                self.list_ctrl_params[i].SetColumnWidth(j, wx.LIST_AUTOSIZE)
        self.SetSizer(sizer)
    #Sous-routine ayant pour but d'analyser une entrée pour la rendre plus lisible pour l'utilisateur
    def Apply_ValueTreatment(self,Value,Comment,NameSubParam):
        #Premier traitement est appliqué sur le type de la valeur proposée
        Test_Words=['integer','double']
        Valid_Word=[0,0]
        cpt_word=0
        for Word in Test_Words:
            Val_Test=Comment.find(Word)
            if(Val_Test>0):
                Valid_Word[cpt_word]=1
                break
            else:
                Test=1
            cpt_word += 1
        if(Valid_Word[0]==1):
            Value=str(int(Value))
        else:
            if(Valid_Word[1]==1):
                Value=str(float(Value))
        #Deuxième traitement est proposé comme valeur affichée à l'écran pour certaines entrées
        cpt_special=0
        for Loc_Comment in Special_Entries:
            if(Loc_Comment==NameSubParam):
                Comment += '.Authorized entries :'
                for Entries in Translation_Entry[cpt_special][1]:
                    Comment += Entries
                    Comment += ','
                size = len(Comment)
                Comment = Comment[:size-1]+'.'
                #On modifie également la valeur afin qu'elle colle à la forme voulue
                cpt_entry=0
                Attr_Entry=False
                for Entries in Translation_Entry[cpt_special][0]:
                    if(Entries == Value):
                        Value=Translation_Entry[cpt_special][1][cpt_entry]
                        Attr_Entry=True
                        break
                    cpt_entry += 1
                if(not(Attr_Entry)):
                    #L'entrée soumise n'est donc pas valide : il faut prévenir l'utilisateur via ouverture fenêtre
                    Test=1
                break

            cpt_special += 1
        return Value,Comment

#
class NewPatternFrame(wx.Frame):
    """
    Frame utilisée pour permettre la mise en place du pattern
    """
    def __init__(self, title, parent):
       super(NewPatternFrame, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
       #Ajout d'un nouveau noeud entraîne à l'activiation du mode d'édition du réseau
       parent.Edition_Mode_Local=True

       vbox = wx.BoxSizer(wx.VERTICAL)

       self.Centre()
       frame_sizer = wx.BoxSizer(wx.VERTICAL)
       #frame_sizer.Add(panel, 1, wx.EXPAND| wx.LEFT | wx.RIGHT, wx.ALIGN_CENTER)

       #Message d'annonce pour savoir ce qui est à réaliser
       Message='Characteristics of the Pattern'
       self.message = wx.StaticText(self, -1, Message)
       frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)

       #Partiée liée à l'affichage des informations du pattern (menu défilant ?)
       self.panel = PanelPattern(self,parent)
       frame_sizer.Add(self.panel, 1, wx.EXPAND)
       #Partie liée aux choix de validation ou d'annulation
       sz2 = wx.BoxSizer(wx.HORIZONTAL)
       self.btn=wx.Button(self,-1,"Show Pattern")
       sz2.Add(self.btn,0, wx.ALL, 10)
       self.btn.Bind(wx.EVT_BUTTON,self.Show_Pattern)

       self.btn2=wx.Button(self,-1,"Save")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.SaveModPattern)

       self.btn2=wx.Button(self,-1,"Annuler")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

       frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
       self.SetAutoLayout(True)
       self.SetSizerAndFit(frame_sizer)
       self.Show()


   #L'annulation étant choisie par l'utilisateur, la fenêtre est simplement fermée
    def CloseFrame(self, e):
       self.Close()
       self.Destroy()
   #La sauvegarde des modifications réalisées au sein du Pattern sont effectuées
    def SaveModPattern(self, e):
       MainW=self.Parent
       #Si modification du Pattern concerné, on va le remplacer par les valeurs présentes dans la liste
       PosPattern=MainW.PosPattern
       for i in range(len(MainW.Patterns[PosPattern]['Values'])):
           for j in range(len(MainW.Patterns[PosPattern]['Values'][i])):
            Val=self.panel.list_ctrl.GetItem(j,i)
            MainW.Patterns[PosPattern]['Values'][i][j]=Val.Text

       test=1
   #Ouverture d'une nouvelle fenêtre Matplotlib pour afficher le Pattern selon sa construction (sur 24H)
    def Show_Pattern(self, e):
        MainW=self.Parent
        PosPattern=MainW.PosPattern
        NamePattern=PosPattern
        self.Show_Pattern=PatternShow(NamePattern,self)

#
class MyDialog(wx.Dialog):
    """
    Méthode d'ajout du pattern
    """

    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(600, 500), style=wx.DEFAULT_DIALOG_STYLE)
        pnl1 = wx.Panel(self, -1, style=wx.SIMPLE_BORDER)
        pnl2 = wx.Panel(self, -1, style=wx.SIMPLE_BORDER)

        self.lc = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.lc.InsertColumn(0, 'Name')
        self.lc.InsertColumn(1, 'Time')
        self.lc.InsertColumn(2, 'Value')
        self.lc.InsertColumn(3, 'Position')
        self.lc.SetColumnWidth(0, 100)
        self.lc.SetColumnWidth(1, 60)
        self.lc.SetColumnWidth(2, 100)
        self.lc.SetColumnWidth(3, 60)
        self.lc.SetBackgroundColour("#eceade")

        self.tc1 = wx.TextCtrl(pnl1, -1)
        self.tc2 = wx.TextCtrl(pnl1, -1)
        self.tc3 = wx.TextCtrl(pnl1, -1)
        self.tc4 = wx.TextCtrl(pnl1, -1)

        hbox  = wx.BoxSizer(wx.HORIZONTAL)
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        vbox3 = wx.GridSizer(8,1,0,0)
        vbox4 = wx.BoxSizer(wx.VERTICAL)

        vbox1.Add(pnl1, 1, wx.EXPAND | wx.ALL, 3)
        vbox1.Add(pnl2, 1, wx.EXPAND | wx.ALL, 3)
        vbox2.Add(self.lc, 1, wx.EXPAND | wx.ALL, 3)

        vbox3.AddMany([(wx.StaticText(pnl1, -1, 'Name of pattern :'),0, wx.ALIGN_CENTER),
                       (self.tc4, 0, wx.ALIGN_CENTER),
                       (wx.StaticText(pnl1, -1, 'Time value :'),0, wx.ALIGN_CENTER),
                       (self.tc1, 0, wx.ALIGN_CENTER),
                       (wx.StaticText(pnl1, -1, 'Value :'),0, wx.ALIGN_CENTER_HORIZONTAL),
                       (self.tc2,0, wx.ALIGN_CENTER),
                       (wx.StaticText(pnl1, -1, 'Position :'),0, wx.ALIGN_CENTER_HORIZONTAL),
                       (self.tc3,0,wx.ALIGN_CENTER)])

        vbox4.Add(wx.Button(pnl2, 14, '&Automatic Read'),   0, wx.ALIGN_CENTER| wx.TOP, 30)
        vbox4.Add(wx.Button(pnl2, 10, '&Add'),   0, wx.ALIGN_CENTER| wx.TOP, 15)
        vbox4.Add(wx.Button(pnl2, 11, '&Remove'), 0, wx.ALIGN_CENTER|wx.TOP, 15)
        vbox4.Add(wx.Button(pnl2, 12, '&Clear'), 0, wx.ALIGN_CENTER| wx.TOP, 15)
        vbox4.Add(wx.Button(pnl2, 13, '&Quit'), 0, wx.ALIGN_CENTER| wx.TOP, 15)

        hbox.Add(vbox1, 1, wx.EXPAND)
        hbox.Add(vbox2, 1, wx.EXPAND)

        pnl1.SetSizer(vbox3)
        pnl2.SetSizer(vbox4)
        self.SetSizer(hbox)
        self.Bind (wx.EVT_BUTTON, self.OnAdd, id=10)
        self.Bind (wx.EVT_BUTTON, self.OnRemove, id=11)
        self.Bind (wx.EVT_BUTTON, self.OnClear, id=12)
        self.Bind (wx.EVT_BUTTON, self.OnClose, id=13)
        self.Bind (wx.EVT_BUTTON, self.AutRead, id=14)

    def OnAdd(self, event):
        if not self.tc1.GetValue() or not self.tc2.GetValue():
            return
        num_items = self.lc.GetItemCount()
        self.lc.InsertItem(num_items, self.tc4.GetValue())
        self.lc.SetItem(num_items, 1, self.tc1.GetValue())
        self.lc.SetItem(num_items, 2, self.tc2.GetValue())
        self.lc.SetItem(num_items, 3, self.tc3.GetValue())
        self.tc1.Clear()
        self.tc2.Clear()
        self.tc3.Clear()

    def OnRemove(self, event):
        index = self.lc.GetFocusedItem()
        self.lc.DeleteItem(index)

    def OnClose(self, event):
        #On récupère les éléments éventuels si le nombre de ligne est plus grande que 0
        num_items = self.lc.GetItemCount()
        if(num_items>0):
            for i in range(num_items):
                NamePattern=self.lc.GetItem(i, 0).Text
                #Première recherche à faire sur le nom de l'élément
                if (NamePattern in self.Parent.Patterns):
                    Test=1
                else:
                    if(not(bool(self.Parent.Patterns))):
                        self.Parent.Patterns={}
                    self.Parent.Patterns[NamePattern]={}
                    self.Parent.Patterns[NamePattern]['Calendar']=[]
                    self.Parent.Patterns[NamePattern]['Exch_Opt']='-1'
                    self.Parent.Patterns[NamePattern]['Meth_Interp']='0'
                    self.Parent.Patterns[NamePattern]['Ptrn_Link']=[]
                    self.Parent.Patterns[NamePattern]['Values']=[[],[],[]]
                for j in range(4):
                    if(j>0):
                        Value=self.lc.GetItem(i, j).Text
                        self.Parent.Patterns[NamePattern]['Values'][j-1].append(Value)
        #Seconde partie dédiée à revoir la partie "Calendar des nouveaux échanges"
        AddMenu = wx.Menu()
        NewNode=[]
        menuBarPos = self.Parent.menubar.FindMenu('&Patterns')
        if menuBarPos >= 0:
           self.Parent.menubar.Remove(menuBarPos)
        for NamePattern in self.Parent.Patterns:
            if(not(bool(self.Parent.Patterns[NamePattern]['Calendar']))):
                Loc_List=[]
                Val_List=[]
                for Elem in self.Parent.Patterns[NamePattern]['Values'][0]:
                    Loc_List.append(float(Elem))
                    Val_List.append(Elem)
                Indices=np.argsort(Loc_List)
                for j in range(3):
                    Loc_List=self.Parent.Patterns[NamePattern]['Values'][j]
                    for k in range(len(Loc_List)):
                        self.Parent.Patterns[NamePattern]['Values'][j][k]=Loc_List[Indices[k]]
                    Test=1
                Test=1
                #On vient finalement récupérer la dernière valeur pour savoir le nombre de journées
                Max_Time=self.Parent.Patterns[NamePattern]['Values'][0][len(Loc_List)-1]
                Nb_Days=ceil(float(Max_Time)/86400.0)
                for Loc in range(Nb_Days):
                    self.Parent.Patterns[NamePattern]['Calendar'].append(Loc+1)

        #On fait également une étape liée à l'ajout du pattern au sein du menu Pattern de la fenêtre principale

        self.Parent.Patterns_Exchange_Menu()
        self.Close()

    def OnClear(self, event):
        self.lc.DeleteAllItems()

    def AutRead(self, event):
        namepath='X'
        #On va recherche l'élément
        dlg = wx.FileDialog(self, "Choose the Pattern file",
                           defaultDir = "",
                           defaultFile = "",
                           wildcard = "*")
        #On récupère le chemin d'accord au fichier
        if dlg.ShowModal() == wx.ID_OK:
            namepath=dlg.GetPath()
            t=1
        dlg.Destroy()
        if(namepath!='X'):
            #le format indique le nom en premier puis à chaque ligne, les nouvelles valeurs à ajouter avec valeur croissante selon le temps
            file = open(namepath,'r')
            #On fait alors la lecture
            cpt_line=0
            for New_Word in file:
                cpt_line+=1
                if(cpt_line==1):
                    NamePattern=New_Word.rstrip('\n')
                else:
                    Value=New_Word.rstrip('\n')
                    Value=Value.split()
                    #On regarde notamment à la structure des données
                    if(len(Value)>1 and len(Value)<4):
                        #On a structure qui convient et qui peut donc être récupérée
                        num_items = self.lc.GetItemCount()
                        self.lc.InsertItem(num_items, NamePattern)
                        for i in range(len(Value)):
                            self.lc.SetItem(num_items, i+1, Value[i])
                    else:
                        break

#
class NewPumpFrame(wx.Frame):
    """
    Frame utilisée pour permettre la mise en place d'une pompe
    """
    def __init__(self, title, parent):
       super(NewPumpFrame, self).__init__(parent, title = title,size = (700,700),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
       #Ajout d'un nouveau noeud entraîne à l'activiation du mode d'édition du réseau
       parent.Edition_Mode_Local=True

       vbox = wx.BoxSizer(wx.VERTICAL)

       self.Centre()
       frame_sizer = wx.BoxSizer(wx.VERTICAL)
       #frame_sizer.Add(panel, 1, wx.EXPAND| wx.LEFT | wx.RIGHT, wx.ALIGN_CENTER)

       #Message d'annonce pour savoir ce qui est à réaliser
       Message='Characteristics of the Pump'
       self.message = wx.StaticText(self, -1, Message)
       frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)

       #Partiée liée à l'affichage des informations du pattern (menu défilant ?)
       self.panel = PanelPump(self,parent)
       frame_sizer.Add(self.panel, 1, wx.EXPAND)
       #Partie liée aux choix de validation ou d'annulation
       sz2 = wx.BoxSizer(wx.HORIZONTAL)
       self.btn=wx.Button(self,-1,"Show Pump")
       sz2.Add(self.btn,0, wx.ALL, 10)
       self.btn.Bind(wx.EVT_BUTTON,self.Show_Pump)

       self.btn2=wx.Button(self,-1,"Save")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.SaveModPump)

       self.btn2=wx.Button(self,-1,"Annuler")
       sz2.Add(self.btn2,0, wx.ALL, 10)
       self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

       frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
       self.SetAutoLayout(True)
       self.SetSizerAndFit(frame_sizer)
       self.Show()


   #L'annulation étant choisie par l'utilisateur, la fenêtre est simplement fermée
    def CloseFrame(self, e):
       self.Close()
       self.Destroy()
   #La sauvegarde des modifications réalisées au sein de la pompe sont effectuées
    def SaveModPump(self, e):
       MainW=self.Parent
       #Si modification de la pompe concernée, on va remplacer le type de pompe ainsi que les coefficients
       PosPattern=MainW.PosPattern
       for i in range(len(MainW.Patterns['Values'][PosPattern])):
           for j in range(len(MainW.Patterns['Values'][PosPattern][i])):
            Val=self.panel.list_ctrl.GetItem(j,i)
            MainW.Patterns['Values'][PosPattern][i][j]=Val.Text

       test=1
   #Ouverture d'une nouvelle fenêtre Matplotlib pour afficher le Pattern selon sa construction (sur 24H)
    def Show_Pump(self, e):
        MainW=self.Parent
        PosPump=MainW.PosPump
        NamePump=MainW.Zones[1]['Name'][PosPump]
        self.Show_Pattern=PumpShow(NamePump,self)


#
class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    """
    Objet permettant l'édition des colonnes de la liste pour l'utilisateur
    """
    def __init__(self, parent, MainWindow, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndLabelEdit)
    def OnBeginLabelEdit(self, event):
            event.Skip()
    #On doit sauvegarder les modifications liées au Pattern
    def OnEndLabelEdit(self, event):
        Column=event.Column
        Index=event.Index

#
class PanelPattern(wx.Panel):
    """
    Création de la grille permettant l'affichage des principaux attributs pour un vecteur
    """
    def __init__(self, parent,MainW):
        super(PanelPattern, self).__init__(parent)

        #Initialisation de la grille = évaluation du nombre d'attributs à afficher

        #Mise en place de la liste de contrôle
        IDPattern=MainW.IDLocPattern
        for i in range(len(MainW.IDPattern)):
            if(MainW.IDPattern[i]==IDPattern):
                IDPattern=MainW.PatternName[i]
        MainW.Modified_Pattern=False
        self.list_ctrl = EditableListCtrl(self, MainWindow=MainW, style=wx.LC_REPORT)
        MainW.PosPattern=IDPattern
        for i in range(len(MainW.Patterns[IDPattern]['Values'])):
            if(i==0):
                self.list_ctrl.InsertColumn(i, "Time")
            elif(i==1):
                    self.list_ctrl.InsertColumn(i, "Value")
            else:
                self.list_ctrl.InsertColumn(i, "Ctrl Position")

        index = 0
        row_position = 0
        for row in MainW.Patterns[IDPattern]['Values']:
            for line_pattern in range(len(row)):
                    if(row_position==0):
                        self.list_ctrl.InsertItem(index, row[line_pattern])
                    else:
                        self.list_ctrl.SetItem(index, row_position, row[line_pattern])
                    index += 1
            self.list_ctrl.SetColumnWidth(row_position, wx.LIST_AUTOSIZE)
            row_position += 1
            index = 0

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)

#
class PatternShow(wx.Frame):
    """
    Frame utilisée pour permettre la mise en place du nouveau noeud
    """
    def __init__(self, title, parent):
       super(PatternShow, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
       #Ajout d'un nouveau noeud entraîne à l'activiation du mode d'édition du réseau

       self.Centre()
       MainW=self.Parent.Parent
       IDPattern=MainW.PosPattern

       frame_sizer = wx.BoxSizer(wx.VERTICAL)
       #Implémentation de la Figure
       self.figure = Figure(figsize=(5, 4), dpi=100)

       self.axes = self.figure.add_subplot(111)
       #Première étape est d'identifier si on peut effectivement bien réévaluer le Pattern de façon horaire afin d'améliorer la lisibilité du Pattern
       NbLines=len(MainW.Patterns[IDPattern]['Values'][0])-1
       TimeLoc=float(MainW.Patterns[IDPattern]['Values'][0][NbLines])
       HourlyPattern=False #Le pas de temps fixé est une heure
       DayPattern=False #Le Pattern est uniquement représenté selon une journée
       if(TimeLoc>86400.0):
           HourlyPattern=True
           DayPattern=False #Le Pattern est uniquement représenté selon une journée
           #if(TimeLoc>=86400.0):
            #   DayPattern=True

       FactDiv=1.0
       Xlabel='Time[s]'
       Ylabel='Discharge[m³/s]'
       if(HourlyPattern):
           Xlabel='Hours[h]'
           FactDiv=3600.0
       #On vient rechercher les informations utiles
       TimeVal=[]
       ValPtrn=[]
       for i in range(len(MainW.Patterns[IDPattern]['Values'][0])):
           TimeLoc=float(MainW.Patterns[IDPattern]['Values'][0][i])/FactDiv
           if(DayPattern):
               if(TimeLoc<=24.0):
                   TimeVal.append(TimeLoc)
                   Val=float(MainW.Patterns[IDPattern]['Values'][1][i])
                   ValPtrn.append(Val)
               else:
                   break
           else:
                TimeVal.append(TimeLoc)
                Val=float(MainW.Patterns[IDPattern]['Values'][1][i])
                ValPtrn.append(Val)
       #Evaluation du Pattern selon le type de Pattern
       if(MainW.Patterns[IDPattern]['Meth_Interp']=='2' or MainW.Patterns[IDPattern]['Meth_Interp']=='0'):
           #Echange de type optimisation avec donc valeurs d'échanges constantes sur chaque pas de temps
           Test=1
           #Il faut exprimer les valeurs comme des plateaux
           RealValues=[]
           RealTime=[]
           Length=len(ValPtrn)-1
           for i in range(len(ValPtrn)):
               if(i==Length):
                   RealTime.append(TimeVal[i])
               else:
                   RealTime.append(TimeVal[i])
                   RealTime.append(TimeVal[i])
               if(i==0):
                   RealValues.append(ValPtrn[i])
               else:
                   RealValues.append(ValPtrn[i])
                   RealValues.append(ValPtrn[i])
       else:
           #Il faut exprimer les valeurs linéairement (interpolation linéaire)
           RealValues=[]
           RealTime=[]
           Length=len(ValPtrn)-1
           for i in range(len(ValPtrn)):
                   RealTime.append(TimeVal[i])
                   RealValues.append(ValPtrn[i])

       self.axes.plot(RealTime, RealValues)
       self.axes.set_xlabel(Xlabel)
       self.axes.set_ylabel(Ylabel)
       if(DayPattern):
           self.axes.set_xlim(0.0,24.0)
       else:
           MaxTime=max(RealTime)
           self.axes.set_xlim(0.0,MaxTime)
       #Réalisation du canvas pour ainsi réévaluer taille de la fenêtre
       self.canvas = FigureCanvas(self, -1, self.figure)
       frame_sizer.Add(self.canvas, 1,   wx.EXPAND)
       self.SetSizer(frame_sizer)
       self.Fit()
       self.Show()
       Test=1

#
class PanelPump(wx.Panel):
    """
    Affichage à la fois du type de fonction pour la pompe ainsi que des coefficients utilisés pour évaluer loi de la pompe
    """
    def __init__(self, parent,MainW):
        super(PanelPump, self).__init__(parent)

        #Initialisation de la grille = évaluation du nombre d'attributs à afficher
        Index=len(MainW.Zones[1]['Name'])
        #Mise en place de la liste de contrôle
        IDPump=MainW.IDLocPump
        MainW.Modified_Pattern=False
        for i in range(Index):
            if(MainW.IDPump[i]==IDPump):
                Test=1
                PosPump=i
                self.TypePump=MainW.Zones[1]['Type'][i]-2
                break
        self.list_ctrl_pump = EditableListCtrl(self, MainWindow=MainW, style=wx.LC_REPORT)
        MainW.PosPump=PosPump
        #Ecriture des informations visibles dans la liste
        #Présentation générale du type de loi de pompe
        TypePumps=[[],[],[],[]]

        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"

        TypePumps[0]='Three nodes method (EPANET) : H(Q)=C-BQᴬ'
        TypePumps[1]='Simplified polynomial methodology : H(Q)=AQ³+BQ²+CQ+D'
        TypePumps[2]='General polynomial methodology : H(Q)=AQˣ+BQˣ⁻¹+CQˣ⁻²+...+X'
        TypePumps[3]='Logistic function approach'
        InfoPumps=[0,0,0,0]
        Gen_Pumps=['ID Pump','Type','ID Type']
        Elements=[MainW.Zones[1]['Name'][PosPump],TypePumps[self.TypePump],str(self.TypePump)]

        self.list_ctrl_pump.InsertColumn(i, "Element")
        self.list_ctrl_pump.InsertColumn(i, "Value/Explanation")
        index=0
        row_position=1

        for Elem in Gen_Pumps:
            self.list_ctrl_pump.InsertItem(index, Elem)
            self.list_ctrl_pump.SetItem(index, row_position, Elements[index])
            #self.list_ctrl_pump.SetColumnWidth(index, wx.LIST_AUTOSIZE)
            index += 1
        pos=1
        id_coeff=0
        for Coeff in MainW.Zones[1]['Coefficients'][PosPump]:
            Name='Pump coeff.'+normal[id_coeff]
            self.list_ctrl_pump.InsertItem(index, Name)
            self.list_ctrl_pump.SetItem(index, row_position, str(float(MainW.Zones[1]['Coefficients'][PosPump][id_coeff])))
            pos += 1
            id_coeff +=1
            index += 1
        index=0
        for Elem in Gen_Pumps:
            self.list_ctrl_pump.SetColumnWidth(index, wx.LIST_AUTOSIZE)
            index +=1
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl_pump, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)

#
class PumpShow(wx.Frame):
    """
    Frame utilisée pour permettre d'afficher la courbe de pompe utilisée
    """
    def __init__(self, title, parent):
       super(PumpShow, self).__init__(parent, title = title,size = (400,300),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
       #Ajout d'un nouveau noeud entraîne à l'activiation du mode d'édition du réseau

       self.Centre()
       MainW=self.Parent.Parent
       IDPump=MainW.IDLocPump

       frame_sizer = wx.BoxSizer(wx.VERTICAL)
       #Implémentation de la Figure
       self.figure = Figure(figsize=(5, 4), dpi=100)

       self.axes = self.figure.add_subplot(111)
       #Première étape est d'identifier si on peut effectivement bien réévaluer le Pattern de façon horaire afin d'améliorer la lisibilité du Pattern
       HourlyPattern=True #Le pas de temps fixé est une heure
       DayPattern=True #Le Pattern est uniquement représenté selon une journée
       FactDiv=1.0
       Xlabel='Discharge[m³/s]'
       Ylabel='Head[m]'

       #On vient rechercher la valeur des coefficients pour représenter la courbe
       HeadVal=[]
       CoeffList=[]
       for Coeff in MainW.Zones[1]['Coefficients'][MainW.PosPump]:
            CoeffList.append(float(Coeff))
       #Prochaine étape est de reconstruire la loi sur base des coefficients proposés
       HeadVal=[]
       ValPtrn=[]
       #Evaluation du Pattern selon le type de Pattern
       if(MainW.Zones[1]['Type'][MainW.PosPump]==2):
           #Pompe de type "3 points" avec H(Q)=C-BQ^A
           if(len(CoeffList)==3):
               Q = np.arange(0.0, 300.0, 1.0)
               H = CoeffList[2]-CoeffList[1]*Q**CoeffList[0]

       self.axes.plot(Q, H)
       self.axes.set_xlabel(Xlabel)
       self.axes.set_ylabel(Ylabel)
        #self.axes.set_xlim(0.0,24.0)
       #Réalisation du canvas pour ainsi réévaluer taille de la fenêtre
       self.canvas = FigureCanvas(self, -1, self.figure)
       frame_sizer.Add(self.canvas, 1,   wx.EXPAND)
       self.SetSizer(frame_sizer)
       self.Fit()
       self.Show()

#
class Mywin(wx.Frame):
    """
    Nouvelle fenêtre pour la mise en valeur de données liées à un vecteur ou tout type de noeud
    """

    def __init__(self, parent, title, MainW, Type_Element):
        super(Mywin, self).__init__(parent, title = title,size = (300,200),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
        self.Type_Element=Type_Element
        if(Type_Element==0):
            panel = MyVectorPanel(self,MainW)
        else:
            panel = MyNodePanel(self,MainW)
      #panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
      #On vient donc afficher dans le petit tableau d'exportation le nom de l'attribut ainsi que sa valeur
        Test=1
        self.Centre()
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizerAndFit(frame_sizer)
      #self.SetWindowStyle(wx.FRAME_FLOAT_ON_PARENT)
        self.Show()
      #self.Fit()
        Test=1
        self.OrigFrame=MainW
        self.locpanel=panel
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def OnClicked(self, event):
        btn = event.GetEventObject().GetLabel()

   #Vérification à la sortie de la fenêtre si des valeurs ont été modifiées et si c'est le cas, demande pour enregistrer les modifications
    def OnCloseWindow(self, event):
       #On va rechercher si un évènement de modification a été identifié
        if(self.modified_grid):
            logging.info('Grid is modified')
        else:
            logging.info('Grid is not modified')
        if(self.modified_grid):
           #Actions à réaliser afin de permettre la sauvegarde ou non des changements en initiant en premier lieu l'ouverture d'une fenêtre
            dlg = wx.MessageDialog(
                None, "Do you want to save the modifications ?", "Save the results", wx.YES_NO | wx.CANCEL | wx.CENTRE
            )
            result = dlg.ShowModal()
            self.Centre()
            self.Show()
            if result == wx.ID_YES:
                Test=1
                self.Save_Modifications()
                self.Destroy()
            if result != wx.ID_CANCEL:
                self.Destroy()
            Test=1
        else:
            self.Destroy()
   #Ajout des différentes modifications proposées par l'utilisateur
    def Save_Modifications(self):
        Test=1
        MainW=self.OrigFrame
        if(self.Type_Element==0):
            cpt_val=0
           #On modifie les propriétés de l'élément connecteur
            Index=int(MainW.LocalNode[0])
            size_list=len(MainW.List_Nodes_OGL['IdZone'])
            NumZone=MainW.List_Nodes_OGL['IdZone'][Index]
            NumVec=MainW.List_Nodes_OGL['NbrElVec'][Index]
            Main_Attr=MainW.Zones[NumZone]['Princ_Attrib']
            for Attrib in Main_Attr:
                if(Attrib in MainW.Zones[NumZone]):
                    if(bool(MainW.Zones[NumZone][Attrib])):
                        if(isinstance(MainW.Zones[NumZone][Attrib][NumVec],list)):
                            Local_val=len(MainW.Zones[NumZone][Attrib][NumVec])
                            for j in range(Local_val):
                                MainW.Zones[NumZone][Attrib][NumVec][j]=self.GridValues[cpt_val]
                                cpt_val+=1
                        else:
                            MainW.Zones[NumZone][Attrib][NumVec]=self.GridValues[cpt_val]
                            cpt_val+=1
        else:
            cpt_val=1
           #On modifie les propriétés du noeud
            IndexNode=int(MainW.LocalNode[0])
            TypeNode=MainW.LocalNode[1]
            NameNode=MainW.LocalNode[2]
            cpt_pos=0
           #On affiche selon le nombre d'attributs dans chaque cas
            for SubAttr in MainW.Nodes['Type_Attrib'][TypeNode]:
                SubAttr = SubAttr.split(',')
                if(len(SubAttr)==1):
                    Test=self.Test_Case(MainW,TypeNode,NameNode,SubAttr,cpt_val,cpt_pos)
               #MainW.Nodes[TypeNode][NameNode][SubAttr[0]]=self.GridValues[cpt_val]
                else:
                    MainW.Nodes[TypeNode][NameNode][SubAttr[0]][int(SubAttr[1])]=self.GridValues[cpt_val]
                cpt_val+=1

       #On peut donc bien considérer que la grille n'est plus modifiée
        self.modified_grid=False
        self.Destroy()
    #Test_Case
    def Test_Case(self,MainW,TypeNode,NameNode,SubAttr,cpt_val,cpt_pos):
        Test=1
        if(isinstance(MainW.Nodes[TypeNode][NameNode][SubAttr[0]],list)):
            MainW.Nodes[TypeNode][NameNode][SubAttr[0]][cpt_pos]=self.GridValues[cpt_val]
        else:
            MainW.Nodes[TypeNode][NameNode][SubAttr[0]]=self.GridValues[cpt_val]
        return Test

#
class MyVectorPanel(wx.Panel):
    """
    Création de la grille permettant l'affichage des principaux attributs pour un vecteur
    """

    def __init__(self, parent,MainW):
        super(MyVectorPanel, self).__init__(parent)

        #Initialisation de la grille = évaluation du nombre d'attributs à afficher
        MyVectorPanel.MainW=MainW
        self.parent=parent
        Index=int(MainW.LocalNode[0])
        size_list=len(MainW.List_Nodes_OGL['IdZone'])
        NumZone=MainW.List_Nodes_OGL['IdZone'][Index]
        NumVec=MainW.List_Nodes_OGL['NbrElVec'][Index]
        Nb_attrib=0
        Name_Attrib=[]
        Val_Attr=[]
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
        Main_Attr=MainW.Zones[NumZone]['Princ_Attrib']
        for Attrib in Main_Attr:
            if(Attrib in MainW.Zones[NumZone]):
                PosEl=Main_Attr.index(Attrib)
                if(bool(MainW.Zones[NumZone][Attrib])):
                    if(isinstance(MainW.Zones[NumZone][Attrib][NumVec],list)):
                        Local_val=len(MainW.Zones[NumZone][Attrib][NumVec])
                        for j in range(Local_val):
                            Val_Attr.append(str(MainW.Zones[NumZone][Attrib][NumVec][j]))
                    else:
                        Local_val=1
                        Val_Attr.append(str(MainW.Zones[NumZone][Attrib][NumVec]))
                    Nb_attrib=Nb_attrib+Local_val
                    if(Local_val==1):
                        Name_Attrib.append(MainW.Zones[NumZone]['Name_Attrib'][PosEl])
                    else:
                        Loc_Name=MainW.Zones[NumZone]['Name_Attrib'][PosEl]
                        for j in range(Local_val):
                            Spec_Name=Loc_Name+'_'+normal[j]
                            Name_Attrib.append(Spec_Name)

        #Mise en place de la grille + colonne
        mygrid = grid.Grid(self)
        mygrid.CreateGrid( Nb_attrib, 1)
        mygrid.SetColLabelValue(0, "Value")
        #On vient afficher l'ensemble des informations pertinentes du vecteur selon les lignes en les complétant
        #NumVec=MainW.List_Nodes_OGL['NbrElVec'][Index]
        Main_Attr=MainW.Zones[NumZone]['Princ_Attrib']
        cpt_row=0
        self.Spec_case=1
        for Ind in range(len(Name_Attrib)):
            mygrid.SetRowLabelValue(cpt_row,Name_Attrib[Ind])
            mygrid.SetCellAlignment(cpt_row, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            mygrid.SetCellValue(cpt_row,0, Val_Attr[Ind])

            cpt_row=cpt_row+1
        mygrid.AutoSizeColumns(setAsMin=True)
        sizer = wx.BoxSizer(wx.VERTICAL)
        #Premier élément à ajouter est donc bien la grille permettant l'affichage des principaux attributs du noeud étudié
        sizer.Add(mygrid, 1, wx.EXPAND)
        #Second élément à ajouter est une possibilité d'afficher dans une nouvelle fenêtre les résultats spécifiques à l'élément sélectionné
        sz2 = wx.BoxSizer(wx.HORIZONTAL)
        self.btn=wx.Button(self,-1,"Spec. Results")
        sz2.Add(self.btn,0, wx.ALL, 10)
        self.btn.Bind(wx.EVT_BUTTON,self.Show_Spec_Results)
        sizer.Add(sz2, 0, wx.ALIGN_CENTER)
        #Elément supplémentaire est lié à la nature du vecteur et de la présence de variables supplémentaires additionnelles
        if(NumZone==2):
            Spec_Param='Opening_Factor'
            if(Spec_Param in MainW.Zones[NumZone]):
                if(bool(MainW.Zones[NumZone][Spec_Param][NumVec])):
                    #Si facteur d'ouverture est renseigné et qu'il y a bien des valeurs spécifiques liées à la valve considérée, on peut ajouter un bouton supplémentaire
                    sz3 = wx.BoxSizer(wx.HORIZONTAL)
                    self.btn=wx.Button(self,-1,"Open. Factor valve")
                    sz3.Add(self.btn,0, wx.ALL, 10)
                    self.Spec_case=2
                    self.btn.Bind(wx.EVT_BUTTON,self.Show_Spec_Results)
                    sizer.Add(sz3, 0, wx.ALIGN_CENTER)

        self.thegrid=mygrid
        self.SetSizer(sizer)
        Test=1
        self.parent.modified_grid=False
        self.thegrid.Bind(grid.EVT_GRID_CELL_CHANGED, self.Saved_Modifications)

    def Saved_Modifications(self,e):
        self.parent.modified_grid=True
        #Sauvegarde des valeurs de la grille
        Nb_Rows=self.thegrid.GetNumberRows()
        self.parent.GridValues=[]
        for Row in range(Nb_Rows):
            self.parent.GridValues.append(self.thegrid.GetCellValue(Row,0))
        Test=1
    #On vient ainsi lancer l'initialisation d'une nouvelle fenêtre afin de montrer les résultats
    def Show_Spec_Results(self,e):
        Test=1
        title='Node results'
        Type_Element=self.Spec_case
        MainW=self.MainW
        Index=int(MainW.LocalNode[0])
        size_list=len(MainW.List_Nodes_OGL['IdZone'])
        NumZone=MainW.List_Nodes_OGL['IdZone'][Index]
        Verif_Attrib='Value'
        if(Verif_Attrib in MainW.Zones[NumZone]):
            New_Results_Frame= Spec_Results(parent=self,title=title,Type_Element=Type_Element)
        else:
            Dial='The following vector does not provide any discharge data'
            dlg = wx.MessageDialog(
                None, Dial, "No available data", wx.OK | wx.CENTRE
            )
            result = dlg.ShowModal()
            self.Centre()
            self.Show()
            if result == wx.ID_YES:
                Test=1
                self.Destroy()

#
class MyNodePanel(wx.Panel):
    """
    Création de la grille permettant l'affichage des principaux attributs pour un noeud en distinguant les différents types
    """

    def __init__(self, parent,MainW):
        super(MyNodePanel, self).__init__(parent)

        #Initialisation de la grille = évaluation du nombre d'attributs à afficher
        self.MainW=MainW
        self.parent=parent
        IndexNode=int(MainW.LocalNode[0])
        TypeNode=MainW.LocalNode[1]
        NameNode=MainW.LocalNode[2]
        PropType=['Reservoirs','IncJunctions']

        #On affiche selon le nombre d'attributs dans chaque cas
        Nb_attrib=1
        Name_Attrib=[]
        #Loc_nb=[]
        Val_Attr=[]

        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
        #for Attrib in MainW.Nodes[PropType[TypeNode]][NameNode]:
            #Attribut de nom directement accessible
        Val_Attr.append(NameNode)
        MainW.Nodes['Type_Attrib']={}
        MainW.Nodes['Type_Attrib'][TypeNode]=[]
        Name_Attrib.append(MainW.Nodes['Name_Attrib'][TypeNode][0])
        for SubAttr in MainW.Nodes[TypeNode][NameNode]:
            Local_val=0
            if(SubAttr in MainW.Nodes['Princ_Attrib'][TypeNode]):
                PosEl=MainW.Nodes['Princ_Attrib'][TypeNode].index(SubAttr)
                if(isinstance(MainW.Nodes[TypeNode][NameNode][SubAttr],list)):
                    #Loc_nb.append(len(MainW.Nodes[TypeNode][NameNode][SubAttr]))
                    Local_val=len(MainW.Nodes[TypeNode][NameNode][SubAttr])
                    for j in range(Local_val):
                        Val_Attr.append(str(MainW.Nodes[TypeNode][NameNode][SubAttr][j]))
                else:
                    #Loc_nb.append(1)
                    Local_val=1
                    Val_Attr.append(str(MainW.Nodes[TypeNode][NameNode][SubAttr]))

                Nb_attrib+=Local_val
                if(Local_val==1):
                    Name_Attrib.append(MainW.Nodes['Name_Attrib'][TypeNode][PosEl])
                    MainW.Nodes['Type_Attrib'][TypeNode].append(SubAttr)
                else:
                    Loc_Name=MainW.Nodes['Name_Attrib'][TypeNode][PosEl]
                    for j in range(Local_val):
                        Spec_Name=Loc_Name+'_'+normal[j]
                        Name_Attrib.append(Spec_Name)
                        LocAttr=SubAttr+','+str(j)
                        MainW.Nodes['Type_Attrib'][TypeNode].append(LocAttr)
        #Nb_attrib=len(MainW.Nodes['Princ_Attrib'][TypeNode])
        #Mise en place de la grille + colonne
        mygrid = grid.Grid(self)
        mygrid.CreateGrid( Nb_attrib, 1)
        mygrid.SetColLabelValue(0, "Value")
        #On vient afficher l'ensemble des informations pertinentes du vecteur selon les lignes en les complétant

        Main_Attr=MainW.Nodes['Princ_Attrib'][TypeNode]
        Name_Attr=[]
        cpt_row=0
        for Id_Attrib in range(Nb_attrib):
            Row_Column=Name_Attrib[Id_Attrib]
            mygrid.SetRowLabelValue(Id_Attrib,Row_Column)
            mygrid.SetCellAlignment(Id_Attrib, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            mygrid.SetCellValue(Id_Attrib,0, Val_Attr[Id_Attrib])

        mygrid.AutoSizeColumns(setAsMin=True)
        sizer = wx.BoxSizer(wx.VERTICAL)
        #Premier élément à ajouter est donc bien la grille permettant l'affichage des principaux attributs du noeud étudié
        sizer.Add(mygrid, 1, wx.EXPAND)
        #Second élément à ajouter est une possibilité d'afficher dans une nouvelle fenêtre les résultats spécifiques à l'élément sélectionné
        sz2 = wx.BoxSizer(wx.HORIZONTAL)
        self.btn=wx.Button(self,-1,"Spec. Results")
        sz2.Add(self.btn,0, wx.ALL, 10)
        self.btn.Bind(wx.EVT_BUTTON,self.Show_Spec_Results)

        sizer.Add(sz2, 0, wx.ALIGN_CENTER)

        self.thegrid=mygrid
        self.SetSizer(sizer)
        Test=1
        self.parent.modified_grid=False
        self.thegrid.Bind(grid.EVT_GRID_CELL_CHANGED, self.Saved_Modifications)
    def Saved_Modifications(self,e):
        self.parent.modified_grid=True
        #Sauvegarde des valeurs de la grille
        Nb_Rows=self.thegrid.GetNumberRows()
        self.parent.GridValues=[]
        for Row in range(Nb_Rows):
            self.parent.GridValues.append(self.thegrid.GetCellValue(Row,0))
    #On vient ainsi lancer l'initialisation d'une nouvelle fenêtre afin de montrer les résultats
    def Show_Spec_Results(self,e):
        Test=1
        title='Node results'
        Type_Element=0
        MainW=self.MainW
        TypeNode=MainW.LocalNode[1]
        NameNode=MainW.LocalNode[2]
        Verif_Attrib='Value'
        if(Verif_Attrib in MainW.Nodes[TypeNode][NameNode]):
            New_Results_Frame= Spec_Results(parent=self,title=title,Type_Element=Type_Element)
        else:
            Dial='The following node does not provide any head data'
            dlg = wx.MessageDialog(
                None, Dial, "No available data", wx.OK | wx.CENTRE
            )
            result = dlg.ShowModal()
            self.Centre()
            self.Show()
            if result == wx.ID_YES:
                Test=1
                self.Destroy()

#
class Spec_Results(wx.Frame):
   """
   Nouvelle fenêtre pour la mise en valeur des résultats d'un noeud ou d'une canalisation
   """

   def __init__(self, parent, title, Type_Element):
      super(Spec_Results, self).__init__(parent, title = title,size = (600,500),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)

      frame_sizer = wx.BoxSizer(wx.VERTICAL)
      #Implémentation de la Figure
      self.figure = Figure(figsize=(5, 4), dpi=100)

      self.axes = self.figure.add_subplot(111)

      #On introduit l'élément à afficher
      MainW=parent.MainW
      Inertia=int(MainW.Param['General Parameters of the network']['Effect of Inertia'][0])
      DeltaT=MainW.Param['Time']['Time step'][0]
      Val_Saved=[]
      if(Type_Element==0): #Noeud
        IndexEl=int(MainW.LocalNode[0])
        TypeEl=MainW.LocalNode[1]
        NameEl=MainW.LocalNode[2]
        Value_El=MainW.Nodes[TypeEl][NameEl]['ValueH']
        Ylabel='Head[m]'
        if(TypeEl=='Reservoirs'):
            Ylabel='Volume[m³]'
            Val_Saved.append(float(MainW.Nodes[TypeEl][NameEl]['IC_V']))
        NameEl=MainW.LocalNode[2]
      else:
        Index=int(MainW.LocalNode[0])
        size_list=len(MainW.List_Nodes_OGL['IdZone'])
        NumZone=MainW.List_Nodes_OGL['IdZone'][Index]
        NumVec=MainW.List_Nodes_OGL['NbrElVec'][Index]
        if(Type_Element==1):
            Ylabel='Discharge[m³/s]'
            Value_El=MainW.Zones[NumZone]['Value'][NumVec]
            if(Inertia==1):
                Val_Saved.append(float(MainW.Zones[NumZone]['IC_Cond'][NumVec]))
        if(Type_Element==2):
            Ylabel='Opening factor[°]'
            Value_El=MainW.Zones[NumZone]['Opening_Factor'][NumVec]

      #Valeurs supplémentares
      for Loc_Val in Value_El:
        Val_Saved.append(float(Loc_Val))
      NbVal=len(Val_Saved)
      #On peut également retrouver via les paramètres généraux le pas de temps
      DeltaT=float(MainW.Param['Time']['Time step'][0])
      TotalTime=float(NbVal)*DeltaT
      Xlabel='Time step[s]'
      #Nombre de pas de temps est évalué selon nombre de valeurs présentes
      Value_T = np.arange(0.0, TotalTime, DeltaT)
      if(TotalTime>86400.0):
          Value_T=Value_T/3600.0
          Xlabel='Time step[h]'
      self.axes.plot(Value_T, Val_Saved)
      self.axes.set_xlabel(Xlabel)
      self.axes.set_ylabel(Ylabel)
      #Réalisation du canvas pour ainsi réévaluer taille de la fenêtre
      self.canvas = FigureCanvas(self, -1, self.figure)
      frame_sizer.Add(self.canvas, 1,   wx.EXPAND)
      self.SetSizer(frame_sizer)
      self.Fit()
      self.Show()

#
class MyFrame_Slider(wx.Frame):
    """
    Partie liée à l'utilisation d'un slider dans le cadre de l'affichage des résultats
    """

    def __init__(self, parent, title,Max_Val):
        super(MyFrame_Slider, self).__init__(parent, title =title, size = (400,200))


        self.panel = MyPanel_Slider(self,Max_Val,parent)
        self.Show()

class MyPanel_Slider(wx.Panel):
    def __init__(self, parent,Max_Val,MainW):
        super(MyPanel_Slider, self).__init__(parent)

        vbox = wx.BoxSizer(wx.VERTICAL)
        #Partie message d'introduction
        Message='Choice of the time step'
        self.message = wx.StaticText(self, -1, Message)
        vbox.Add(self.message, 0, wx.CENTER)
        #Partie liée à la revue automatique des différents pas de temps en permettant aussi un temps de lecture
        Choices=['Automatic Review']
        Name_Box='Draw_Box'
        #Ajout de la possibilité de faire
        #frame_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.CheckBox = wx.CheckListBox(self, choices=Choices, name=Name_Box)
        #frame_sizer.Add(self.CheckBox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT)
        #self.SetSizerAndFit(frame_sizer)
        #vbox.Add(frame_sizer, 0, wx.ALIGN_CENTER)
        #Partie slider
        self.SliderValue = 1
        self.MaxVal=Max_Val
        self.slider = wx.Slider(self, value=1, minValue=1, maxValue=Max_Val,
                             style=wx.SL_HORIZONTAL | wx.SL_LABELS)

        vbox.Add(self.slider,-1, flag = wx.EXPAND | wx.TOP, border = 5)

        self.btn=wx.Button(self,-1,"Ok")
        vbox.Add(self.btn,0, wx.CENTER)
        self.btn.Bind(wx.EVT_BUTTON,self.Slider_Read)

        self.Frame=MainW
        self.slider.Bind(wx.EVT_SLIDER, self.OnSliderScroll)
        self.SetSizerAndFit(vbox)
        self.Center()

    #On identifie de la sorte le nouveau réseau à afficher
    def Slider_Read(self, e):
       Test=1
       Parent=self.GetParent()
       Parent.Automatic=False
       #Parent.Automatic=self.CheckBox.GetCheckedItems()
       #self.Close()
       #self.Destroy()
       #Parent.Close()
       #Parent.Destroy()
       MainW=self.Frame

       Frame_loc=self.Frame
       Frame_loc.Time_Step=self.SliderValue
       if(bool(Parent.Automatic)):
           Nb_cases=int(self.MaxVal)-int(Frame_loc.Time_Step)+1
       else:
           Nb_cases=1
       for cpt_cases in range(Nb_cases):
           Loc_step=Frame_loc.Time_Step+cpt_cases
           #Frame_loc.Show_Results,Frame_loc.ExtrNodes,Frame_loc.ExtrVectors=Show_Results(Frame_loc.Param_Simul,Frame_loc.Zones,Frame_loc.Nodes,Loc_step)
           MainW.Show_Results,MainW.ExtrNodes,MainW.ExtrVectors=Show_Results(MainW.Param_Simul,MainW.Zones,MainW.Nodes,Loc_step)
           MainW.Show_Network()

           Test=1
           #Frame_loc.Show_Network()
           #Remplacement de la Figure originale par celle des résultats obtenus
           #Frame_loc.figure.clear()
           #Frame_loc.figure=Results_Fig
           #Frame_loc.canvas = FigureCanvas(Frame_loc, -1, Frame_loc.figure)

           #Remise à la taille correcte de la Figure suivant un agrandissement (à revoir pour la partie réduction)
           #Frame_loc.SetSizerAndFit(Frame_loc.sizer)
           #Frame_loc.Show_Results=False
           #time.sleep(2)

    def OnSliderScroll(self, event):
        obj = event.GetEventObject()
        value = obj.GetValue()
        self.SliderValue=self.slider.GetValue()



class LineBuilder:
    """
    Partie liée à la mise en place d'actions lorsque l'utilisateur souhaite obtenir des informations à propos du réseau ou souhaite le modifier/construire
    Construction de segments pour le réseau
    """

    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        #self.cid = line.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        logging.info('click', event)
        if event.inaxes!=self.line.axes: return
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()
        xdata=self.xs
        ydata=self.xs

#
class IdElementFrame(wx.Frame):
    """
    Partie liée à la construction
    """
    def __init__(self, title, parent):
        super(IdElementFrame, self).__init__(parent, title = title,size = (300,200),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
        #Ajout d'un nouveau noeud entraîne à l'activiation du mode d'édition du réseau
        parent.Edition_Mode_Local=True

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.Centre()
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        #Message d'annonce pour savoir ce qui est à réaliser
        Message='What are you looking for ? Node or Link ?'
        #Préparation du choix d'éléments
        #Choix disponibles selon les éléments présents au sein du réseau
        TypeNode=['Reservoirs','IncJunctions']
        TypeEl=['Pipe','Pump','Valve','Deversoir']
        ChoicesEleme=[]
        #Noeuds
        for Node in parent.Nodes:
            if(bool(parent.Nodes[Node])):
                for TypeN in TypeNode:
                    if(Node==TypeN):
                        ChoicesEleme.append(TypeN)
        #Links
        cpt_zone=0
        for Index in range(len(parent.Zones)):
            if(bool(parent.Zones[Index])):
                ChoicesEleme.append(TypeEl[cpt_zone])
            cpt_zone += 1
        NameBoxes=['Name:',"ID"]
        NameElement=True
        Init_Pos=0
        #Partie lié à la check list pour que l'utilisateur désigne quel type d'élément il recherche
        self.panel = ExtractElement(self,parent,Message,ChoicesEleme,NameBoxes,NameElement,Init_Pos)
        frame_sizer.Add(self.panel, 1, wx.EXPAND)
        #Partie liée àa la liste permettant d'écrire le nom de l'élément
        index=0
        row_position=1

        #Partie liée aux choix de validation ou d'annulation
        sz2 = wx.BoxSizer(wx.HORIZONTAL)
        self.btn=wx.Button(self,-1,"Ok")
        sz2.Add(self.btn,0, wx.ALL, 10)
        self.btn.Bind(wx.EVT_BUTTON,self.Recherche)


        self.btn2=wx.Button(self,-1,"Close")
        sz2.Add(self.btn2,0, wx.ALL, 10)
        self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

        frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
        self.SetAutoLayout(True)
        self.SetSizerAndFit(frame_sizer)
        self.Show()
        Test=1
   #L'annulation étant choisie par l'utilisateur, la fenêtre est simplement fermée
    def CloseFrame(self, e):
       self.Close()
       self.Destroy()
   #Procédure de recherche de l'élément sur base du nom et du type d'élément
    def Recherche(self,e):
        #Extraction des informations obtenus
        if(hasattr(self.panel,'IDName')):
            if(self.panel.IDName != 'NotAName'):
                Test=1
                Nodes=['Reservoirs','IncJunctions']
                MainW=self.Parent
                AttrEl=False
                for TypeNode in Nodes:
                    if(self.panel.TypeElement==TypeNode and not(AttrEl)):
                        if(self.panel.IDName in MainW.Nodes[TypeNode]):
                            AttrEl=True
                            MainW.LocalNode[0]=MainW.Nodes[TypeNode][self.panel.IDName]['IndPos']
                            MainW.LocalNode[1]=TypeNode
                            MainW.Print_NodeData()
                if(not(AttrEl)):
                    TypeEl=-1
                    for TypeZone in MainW.Zones:
                        TypeEl += 1
                        if(self.panel.IDName in TypeZone['Name']):
                            PosEl=TypeZone['Name'].index(self.panel.IDName)
                            AttrEl=True
                            MainW.LocalNode[0]=TypeZone['IndPos'][PosEl]
                            MainW.Print_VectorData()

        self.Close()
        self.Destroy()

#
class ExtractElement(wx.Panel):
    """
    Classe dédiée à proposer différents choix ayant pour but d'aiguiller l'utilisateur
    """

    def __init__(self, parent,MainW,Message,ChoicesEleme,NameBoxes,Name_Element,Init_Pos):
        super(ExtractElement, self).__init__(parent)

        self.Centre()
        self.Name_Element=Name_Element
        frame_sizer = wx.BoxSizer(wx.VERTICAL)

        self.message = wx.StaticText(self, -1, Message)
        frame_sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)

        #Partie liée à la box pour les choix d'éléments
        self.rbox = wx.RadioBox(self, label = 'Elements', pos = (80,10), choices = ChoicesEleme, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
        #self.rbox.Bind(wx.EVT_RADIOBOX, self.OnRadiogroup)
        #Partie pour définir l'élément de base sélectionné dans la RadioBox
        self.rbox.SetSelection(Init_Pos)
        #Ajout au sizer
        frame_sizer.Add(self.rbox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT)

        self.IDName='NotAName'
        #Partie pour nom élément si cela est nécessaire
        if(self.Name_Element):
            nm = wx.StaticBox(self, -1,NameBoxes[0])
            nmbox = wx.BoxSizer(wx.HORIZONTAL)
            fn = wx.StaticText(self, -1,NameBoxes[1])
            nmbox.Add(fn, 0, wx.ALL|wx.CENTER, 5)
            nm1 = wx.TextCtrl(self, -1, style = wx.ALIGN_LEFT)
            #nm2 = wx.TextCtrl(panel, -1, style = wx.ALIGN_LEFT)
            #ln = wx.StaticText(panel, -1, "Last Name")
            nm1.Bind(wx.EVT_TEXT,self.OnKeyTyped)
            nmbox.Add(nm1, 0, wx.ALL|wx.CENTER, 5)
            #nmbox.Add(nm2, 0, wx.ALL|wx.CENTER, 5)
            nmSizer = wx.StaticBoxSizer(nm, wx.VERTICAL)
            nmSizer.Add(nmbox, 0, wx.ALL|wx.CENTER, 10)
            frame_sizer.Add(nmSizer,0, wx.ALL|wx.CENTER, 5)
        self.SetSizerAndFit(frame_sizer)
        self.TypeElement=-1
    def OnKeyTyped(self, event):
        if(self.Name_Element):
            self.IDName=event.GetString()
        self.TypeElement = self.rbox.StringSelection
        r=1

#
class IdSimulationFrame(wx.Frame):
    """
    Identification du type de simulation désirées par l'utilisateur : capacité de modifier avant lancement
    """
    def __init__(self, title, parent):
        super(IdSimulationFrame, self).__init__(parent, title = title,size = (300,200),style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.parent=parent
        self.Centre()
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        #Message d'annonce pour savoir ce qui est à réaliser
        Message='Which simulation do you want to launch ?'
        #Préparation du choix d'éléments
        #Choix disponibles selon les différents types de simulation
        self.ChoicesEleme=['Simulation (NR)','Simulation (IPOPT)','Optimization (IPOPT)-Beta']
        NameElement=False
        #Paramètre principal à identifier le paramètre de basé sélectionné, sur base des paramètres de la simulation
        IPOPT_Category='IPOPT Optimization Parameters'
        IPOPT_Param=parent.Param[IPOPT_Category]['Associated_Opt_Problem']
        NameBoxes=[]
        if(IPOPT_Param==0):
            Init_Pos=0
        else:
            #Evaluation via le choix de Choice Time
            Tempo_Param=parent.Param[IPOPT_Category]['Associated_Opt_Problem']
            if(Tempo_Param==1):
                Init_Pos=1
            else:
                Init_Pos=2

        #Partie lié à la check list pour que l'utilisateur désigne quel type d'élément il recherche
        self.panel = ExtractElement(self,parent,Message,self.ChoicesEleme,NameBoxes,NameElement,Init_Pos)
        frame_sizer.Add(self.panel, 1, wx.EXPAND)
        #Partie liée àa la liste permettant d'écrire le nom de l'élément
        index=0
        row_position=1

        #Partie liée aux choix de validation ou d'annulation
        sz2 = wx.BoxSizer(wx.HORIZONTAL)
        self.btn=wx.Button(self,-1,"Ok")
        sz2.Add(self.btn,0, wx.ALL, 10)
        self.btn.Bind(wx.EVT_BUTTON,self.ApplyChoice)

        self.btn2=wx.Button(self,-1,"Close")
        sz2.Add(self.btn2,0, wx.ALL, 10)
        self.btn2.Bind(wx.EVT_BUTTON,self.CloseFrame)

        frame_sizer.Add(sz2, 0, wx.ALIGN_CENTER)
        self.SetAutoLayout(True)
        self.SetSizerAndFit(frame_sizer)
        self.Show()
        Test=1
   #L'annulation étant choisie par l'utilisateur, la fenêtre est simplement fermée
    def CloseFrame(self, e):
        self.Close()
        self.Destroy()
   #Procédure de recherche de l'élément sur base du nom et du type d'élément
    def ApplyChoice(self,e):
        ID_Choice=self.panel.rbox.GetSelection()
        RealChoices=[2,1,0]
        self.parent.type_simulation=RealChoices[ID_Choice]
        self.parent.Verified_Launch()
        self.Close()
        self.Destroy()
        Test=1

def Extract_SubStrings(String,Special_char):
    """
    Python code to sort a list by creating
    Extract_SubStrings : extraction de substrings séparés par des caractères spéciaux

    string : string complet auquel on va donc extraire la liste de substrings séparés par des caractères spéciaux
    special_char : caractère spécial utilisé pour séparer les substrings entre eux
    """
    List_Substrings=[]
    cpt_prev=0
    cpt_new=0
    End_Line_Char='\n'
    String=String.lstrip()
    for i in range(len(String)):
        if(String[i]==Special_char or String[i:i+1]==End_Line_Char or i+1==len(String)):
            if(i+1==len(String)):
                cpt_new=cpt_new+1
            List_Substrings.append(String[cpt_prev:cpt_new])
            cpt_new=cpt_new+1
            cpt_prev=cpt_new
        else:
            cpt_new=cpt_new+1
    return List_Substrings


def Nb_Vector_in_Zone(filename):
    """Lecture du nombre de vecteurs présents dans une zone"""
    j=0
    Nb_Vector=0
    for Addit_Word in filename:
        j=j+1
        if(j==1):
            #On a cette fois le nombre de vecteurs au sein de la zone
            Addit_Word=Addit_Word.rstrip('\n')
            Nb_Vector=int(Addit_Word)
            break
    return Nb_Vector

#
def read_complete_vectors(file,Zones,Nb_vec,Id_Zone):
    """Lecture des différents vecteurs présents dans une zone"""
    #Première ligne est le nom de l'élément
    for i in range(Nb_vec):
        name=file.readline().rstrip('\n')
        NB_vertex=int(file.readline())
        Zones[Id_Zone]['Name'].append(name)
        Zones[Id_Zone]['NbrVertex'].append(NB_vertex)
        Zones[Id_Zone]['Coord'][0].append([])
        Zones[Id_Zone]['Coord'][1].append([])
        Zones[Id_Zone]['Coord'][2].append([])
        Length=len(Zones[Id_Zone]['Coord'][0])-1
        for j in range(NB_vertex):
            Coordinates=file.readline().rstrip('\n')
            Coord=Coordinates.split()
            Zones[Id_Zone]['Coord'][0][Length].append(Coord[0])
            Zones[Id_Zone]['Coord'][1][Length].append(Coord[1])
            Zones[Id_Zone]['Coord'][2][Length].append(Coord[2])
            test=1
        #3 lignes sont alors à lire et ne présentent pas pour le moment un intérêt à être modifiées
        for i in range(3):
            name=file.readline()
    IERR=0
    return IERR

def Import_vecz(filename):
    """
    # Importation vise à prendre le fichier vecz afin de rendre en sortie le dictionnaire comprenant l'ensemble des vertex
    # Chaque Vertex est décrit via son numéro de zone, numéro de vecteur, nombre de vertex le décrivant et finalement chaque vertex
    """
    #Première phase, on vérifie que l'extension du fichier est la bonne
    Spec_char='.'
    #List_sbstr=Extract_SubStrings(filename,Spec_char)
    Extent='.vecz'
    extension = os.path.splitext(filename)[1]
    if(extension!=Extent):
        logging.info('Invalid file type')
        return False
    if(os.path.isfile(filename)):
        file = open(filename,'r')
        i=0
        j=0
        Nb_vec=0
        #Première étape avant d'entrer dans le fichier est d'abord de réaliser la structure de la sauvegarde d'informations
        #Le nom des arguments seront les suivants : nom, numéro du vecteur, nombre de vertex au sein du vertex et puis coordonnées
        Zones=[]
        Id_Zone=0
        for New_Word in file:
            #Première partie liée aux informations génériques pour compléter ainsi le dictionnaire de Vecteurs
            i=i+1
            New_Word=New_Word.rstrip('\n')
            if(i==2):
                #Il s'agit du nombre de zones présents
                Nb_zones=int(New_Word)
                loc_zone=0
                for a in range(Nb_zones):
                    Zones.append({})
                    Zones[loc_zone]['Name']=[]
                    Zones[loc_zone]['NbrVec']=0
                    Zones[loc_zone]['NbrVertex']=[]
                    Zones[loc_zone]['Coord']=[]
                    Zones[loc_zone]['Coord'].append([])
                    Zones[loc_zone]['Coord'].append([])
                    Zones[loc_zone]['Coord'].append([])
                    loc_zone=loc_zone+1
                name=file.readline().rstrip('\n') #On sait que c'est la première ligne liée à "zone" qui n'a pas d'influence sur le reste
                Nb_vec=Nb_Vector_in_Zone(file)
                r=1
                if(Nb_vec>0):
                    Zones[Id_Zone]['NbrVec']=Nb_vec
                    IERR=read_complete_vectors(file,Zones,Nb_vec,Id_Zone)
                    Id_Zone=Id_Zone+1
            if(i>2):
                Nb_vec=Nb_Vector_in_Zone(file)
                if(Nb_vec>0):
                    Zones[Id_Zone]['NbrVec']=Nb_vec
                    IERR=read_complete_vectors(file,Zones,Nb_vec,Id_Zone)
                Id_Zone=Id_Zone+1
        file.close()
    else:
        logging.info('The .vecz file is not found.')
        Zones=False
    return Zones


def Init_Zones():
    """Initialisation des zones quand on part d'un réseau complètement neuf"""
    Nb_zones=4
    Zones=[]
    for loc_zone in range(Nb_zones):
        Zones.append({})
        Zones[loc_zone]['Name']=[]
        Zones[loc_zone]['NbrVec']=0
        Zones[loc_zone]['NbrVertex']=[]
        Zones[loc_zone]['Coord']=[]
        Zones[loc_zone]['Coord'].append([])
        Zones[loc_zone]['Coord'].append([])
        Zones[loc_zone]['Coord'].append([])
        Zones[loc_zone]['Value']=[]
        Zones[loc_zone]['Length']=[]
        Zones[loc_zone]['IC_Cond']=[]
        Zones[loc_zone]['Length']=[]
        if(loc_zone==0 or loc_zone==2):
            Zones[loc_zone]['Material']=[]
            Zones[loc_zone]['Rough_Coeff']=[]
        if(loc_zone==0):
            Zones[loc_zone]['Diameter']=[]
        if(loc_zone==2):
            Zones[loc_zone]['Width']=[]
            Zones[loc_zone]['Height']=[]
            Zones[loc_zone]['Type_Valve']=[]
            Zones[loc_zone]['Opening_Factor']=[]
            Zones[loc_zone]['Coeff_Valve']=[]
        if(loc_zone==1):
            Zones[loc_zone]['Type_Law']=[]
            Zones[loc_zone]['Nb_Coefficients']=[]
    return Zones

#Sous-routine de calcul de distance entre deux noeuds
def distance(Node1,Node2):
    dist=((Node1[0]-Node2[0])**2+(Node1[1]-Node2[1])**2)**0.5
    return dist

# Exportation est basée sur le même type de format d'entrée utilisé pour la partie importaion : l'utilisation d'un autre format ne serait donc pas adéquat
# Chaque Vertex est décrit via son numéro de zone, numéro de vecteur, nombre de vertex le décrivant et finalement chaque vertex
def Export_vecz(Zones,filename):
    #Première phase, on vérifie que l'extension du fichier est la bonne
    Spec_char='.'
    #List_sbstr=Extract_SubStrings(filename,Spec_char)
    List_sbstr=re.split(r'\.', filename)
    Extent='.vecz'
    extension = os.path.splitext(filename)[1]
    if(extension!=Extent):
        logging.info('Invalid file type')
        IERR=1
        return False
    file = open(filename,'w')
    Next_line='\n'
    text_line='0 0'
    file.write(text_line+Next_line)

    NbZones=len(Zones)
    file.write(str(len(Zones))+Next_line)
    Blank='  '
    Line1='           0,           1,           0,#FALSE#,#FALSE#,#FALSE#,#FALSE#,           0,#FALSE#'
    Line2='"...",           5,       0.000000,       0.000000,#FALSE#,#FALSE#,"arial",          10,           0,#FALSE#'
    Line3='#TRUE#'
    IERR=0

    for i in range(NbZones):
        file.write('zone'+Next_line)
        NbVectors=0
        NbVectors=Zones[i]['NbrVec']
        if(bool(NbVectors)):
            file.write(str(NbVectors)+Next_line)
        else:
            file.write(str(0)+Next_line)
        if(bool(NbVectors)):
            for j in range(NbVectors):
                file.write(Zones[i]['Name'][j]+Next_line)
                NbrVertex=int(Zones[i]['NbrVertex'][j])
                file.write(str(Zones[i]['NbrVertex'][j])+Next_line)
                for k in range(NbrVertex):
                    CoordX=Zones[i]['Coord'][0][j][k]
                    CoordY=Zones[i]['Coord'][1][j][k]
                    CoordZ=Zones[i]['Coord'][2][j][k]
                    Coord=CoordX+Blank+CoordY+Blank+CoordZ
                    file.write(Coord+Next_line)
                test=1
                file.write(Line1+Next_line)
                file.write(Line2+Next_line)
                file.write(Line3+Next_line)
    file.close()
    return IERR

def Create_Network(Zones):
    """Creation du réseau en vue de l'affichage via networkx et également sauvegarde de l'ensemble des noeuds présents au sein du réseau"""

    #cp = cProfile.Profile()
    #cp.enable()
    myfig = plt.figure()
    ax = myfig.add_subplot(111)
    #plt.figure()
    NbZones=len(Zones)
    IERR=0

    List_Add_Nodes={}
    List_Add_Nodes['Coord']=[]
    List_Add_Nodes['CoordPlan']=[]
    List_Add_Nodes['InitNode']=[]
    List_Add_Nodes['NbrEl']=[]
    List_Add_Nodes['TypeEl']=[]
    List_Add_Nodes['VecCoord']=[]
    List_Add_Nodes['IdZone']=[]
    List_Add_Nodes['NbrElVec']=[]
    List_Add_Nodes['SpecNode']=[]
    List_Add_Nodes['TypeNode']=[]
    List_Add_Nodes['NameNode']=[]
    List_Add_Nodes['PosVec']=[]
    #Création d'un dictionnaire regroupant à la fois l'ensemble des coordonnées (X,Y) des noeuds mais également des CG de chaque vecteur + numéro vecteur/noeud + Type de noeud
    List_Nodes={}
    List_Nodes['Coord']=[]
    List_Nodes['IdZone']=[]
    List_Nodes['NbrEl']=[]
    List_Nodes['TypeEl']=[]
    List_Nodes['InitNode']=[]
    List_Nodes['VecCoord']=[]

    #Discr_Nodes={}
    #Discr_Nodes['Coord']=[]
    #Discr_Nodes['Pos_vertex']=[]


    Node_Prop=[0,0]
    Loc_Node=[0,0]
    cpt_node=0
    cpt_vertex=0
    cpt_loc_ver=0
    cpt_vec=1
    NbZones=0
    NbZones=len(Zones)
    Pos_Node=-1
    Attr2=True
    attrib=True
    Cpt_Total_Node=1
    First_Node=0
    Last_Node=0
    Pos_lox_Node=0
    Complete_Creation=False
    Default_Type_Node='IncJunctions'
    Big_List=0
    ListCoordX=[]
    edges=[[],[],[],[],[]]
    cpt_vect=-1
    for i in range(NbZones):
        NbVectors=Zones[i]['NbrVec']
        #NbVectors=15
        if(bool(NbVectors)):
            edges[2].append(NbVectors)
            for j in range(NbVectors):
                cpt_vect+=1
                cpt_node=cpt_node+1
                NbrVertex=int(Zones[i]['NbrVertex'][j])
                edges_to_add=[]
                for k in range(NbrVertex):
                    if(k>0):
                        Previous_Coord=(CoordX,CoordY)

                    CoordX=float(Zones[i]['Coord'][0][j][k])
                    CoordY=float(Zones[i]['Coord'][1][j][k])
                    CoordZ=float(Zones[i]['Coord'][2][j][k])

                    Current_Coord=(CoordX,CoordY)
                    if(k>0):
                        if(Attr2):
                            Node_Test=Current_Coord
                            Attr2 = False
                        #On ajoute également dans la liste l'ensemble des CG de chaque partie de vecteur
                        CG_Coord=((Current_Coord[0]+Previous_Coord[0])/2,(Current_Coord[1]+Previous_Coord[1])/2)
                        List_Add_Nodes['VecCoord'].append(CG_Coord)
                        List_Add_Nodes['IdZone'].append(i)
                        List_Add_Nodes['NbrElVec'].append(j)
                        List_Add_Nodes['PosVec'].append(cpt_vect)
                        #List_Nodes['TypeEl'].append('Vector')
                        #List_Nodes['InitNode'].append(-1)
                        Last_Node=Cpt_Total_Node


                    if(k==0 or (k==NbrVertex-1)):
                        New_Node=True
                        Node_Prop=(CoordX,CoordY)
                        if(len(List_Add_Nodes['CoordPlan'])>0):
                            if(Node_Prop[0] in ListCoordX):
                                Ind,dist=closest_node(Node_Prop,List_Add_Nodes['CoordPlan'][:])
                                if(dist<0.0001):
                                    New_Node=False
                                    Pos_lox_Node=Ind+1
                                    test=1

                        if(New_Node):
                            cpt_vertex=cpt_vertex+1
                            Pos_Node=Pos_Node+1
                            Pos_lox_Node=Pos_Node
                            ListCoordX.append(CoordX)
                            #List_Nodes['Coord'].append(Current_Coord)
                            #List_Nodes['IdZone'].append(-i)
                            #List_Nodes['NbrEl'].append(Pos_Node)
                            #List_Nodes['TypeEl'].append('Node')
                            #List_Nodes['InitNode'].append(-1)

                            List_Add_Nodes['Coord'].append((CoordX,CoordY,CoordZ))
                            List_Add_Nodes['CoordPlan'].append(Current_Coord)
                            List_Add_Nodes['NbrEl'].append(Pos_Node)
                            List_Add_Nodes['SpecNode'].append(0)
                            #List_Add_Nodes['InitNode'].append(-1)
                            #List_Add_Nodes['TypeEl'].append('Node')
                            loc_vertex=cpt_vertex
                        else:
                            #Recherche de la position de vertex associée
                            loc_vertex= Ind+1
                            test=1
                        if(k==0):
                            First_Node=loc_vertex
                        if((k==NbrVertex-1)):
                            Last_Node=loc_vertex
                            edges_to_add.append((First_Node,Last_Node))

                    else:
                        if(Complete_Creation):
                             cpt_vertex=cpt_vertex+1
                             Last_Node=cpt_vertex
                             List_Add_Nodes.append((CoordX,CoordY,CoordZ))
                             edges_to_add.append((First_Node,Last_Node))
                             First_Node=Last_Node

                cpt_vec=cpt_vec+1

                #plot=edges_to_add[0]
                # Vec_Name=Zones[i]['Name'][j]
                if(Complete_Creation):
                    List_Tuples=int(sum(map(len, edges_to_add))/2)
                    for s in range(List_Tuples):
                        edges[0].insert(Big_List,edges_to_add[s])
                        edges[1].insert(Big_List,j)
                        edges[3].insert(Big_List,i)
                        Big_List=Big_List+1
                else:
                    edges[0].insert(Big_List,edges_to_add[0])
                    edges[1].insert(Big_List,j)
                    edges[3].insert(Big_List,i)
                    Big_List=Big_List+1

                cpt_vec=cpt_vec+1
        else:
            edges[2].append(0)

    Edges_OpenGl=edges
    Edges_OpenGl[4]=[0]*len(Edges_OpenGl[3])
    #On met à la taille les vecteurs qui manquent
    NbNodes=len(List_Add_Nodes['Coord'])
    List_Add_Nodes['InitNode']=[-1]*NbNodes
    #List_Add_Nodes['TypeEl']=['Node']*NbNodes
    Edition=False
    #cp.disable()
    #cp.print_stats()
    #Il faut également finalement ajouter une nouvelle section liée cette fois à la numérotation des vecteurs, zone par zone
    IndexZone=[0,0,0,0]#Correspond au nombre de zones
    r=len(List_Add_Nodes['NbrElVec'])
    s=len(List_Add_Nodes['IdZone'])
    #for index in range(len(List_Add_Nodes['NbrEl'])):
    #    IdZone=List_Add_Nodes['IdZone'][index]

    return myfig,Edition,List_Add_Nodes,Edges_OpenGl

#Sous-routine  ayant pour but d'afficher les résultats selon le choix de paramètres effectué par l'utilisateur
def Show_Results(Param_Simul,Zones,Nodes,Timing):
    Choices=['HeadNodes','Altimetry','Discharge','Diameter']
    #plt.figure()
    cpt_choices=-1
    Attr_Node=False
    Attr_Vector=False
    To_show_Elements=[0,0]
    Extr_Nodes=[1000000,0]
    Extr_Vectors=[1000000,0]
    for Loc_Choice in Choices:
        cpt_choices=cpt_choices+1
        if(Param_Simul[cpt_choices]==1):

            #Réinitilisation des groupes
            #Réévaluation du Timing à prendre en compte
            #Méthode des valeurs aux noeuds
            if(cpt_choices<2):
                if(not(Attr_Node)):
                    Test=1
                    To_show_Elements[1]=1
                    Extr_Nodes=Set_Up_Node_Values(Nodes,'Reservoirs',cpt_choices,Timing,Extr_Nodes)
                    Extr_Nodes=Set_Up_Node_Values(Nodes,'IncJunctions',cpt_choices,Timing,Extr_Nodes)
                    Attr_Node=True
            else:
                if(not(Attr_Vector)):
                    To_show_Elements[0]=1
                    Extr_Vectors=Set_Up_Vector_Values(Zones,cpt_choices,Timing)
                    Attr_Vector=True

    return To_show_Elements,Extr_Nodes,Extr_Vectors

#Sous-routine en complément de Show_Results pour préparer selon chaque type de noeud : à compléter par la suite via les bons choix de valeur
def Set_Up_Node_Values(Nodes,Node_Type,Param_Simul,Timing,Extr_Nodes):
    Excl_Names=['Name_Attrib']
    Val_Shown=[]
    for NameNode in Nodes[Node_Type]:
        if(Param_Simul==0):
            Val_Shown.append(float(Nodes[Node_Type][NameNode]['ValueH'][Timing]))
            Value=float(Nodes[Node_Type][NameNode]['ValueH'][Timing])
            Nodes[Node_Type][NameNode]['ShowVal']=Nodes[Node_Type][NameNode]['ValueH'][Timing]
        if(Param_Simul==1):
            Val_Shown.append(float(Nodes[Node_Type][NameNode]['CoordZ']))
            Nodes[Node_Type][NameNode]['ShowVal']=Nodes[Node_Type][NameNode]['CoordZ']
        Test=1
    Loc=min(Val_Shown)
    if(Extr_Nodes[0]>Loc):
        Extr_Nodes[0]=Loc
    Loc=max(Val_Shown)
    if(Extr_Nodes[1]<Loc):
        Extr_Nodes[1]=Loc

    return Extr_Nodes

#Préparation finale pour la mise en place des informations
def Prepare_Node_Values(G_loc):
    values = []
    cpt_elem=0
    for u in G_loc.nodes():
        cpt_elem=cpt_elem+1
        Loc_Val=G_loc.nodes[u][key_Param.VALUE]+float(cpt_elem)/float(1000000000)
        values.append(Loc_Val)
        if(G_loc.nodes[u][key_Param.VALUE]==0):
            Test=1
    return values

#Sous-routine parallèle utilisée pour les tronçons cette fois
def Set_Up_Vector_Values(Zones,Param_Simul,Timing):

    cpt_elem=0
    if(Param_Simul==3):
        NameParam='Diameter'
    if(Param_Simul==2):
        NameParam='Value'
    Timing=Timing-1
    Extr=[1000000,0]
    for Loc_Zone in range(len(Zones)):
        if(NameParam in Zones[Loc_Zone]):
            NbVectors=Zones[Loc_Zone]['NbrVec']
            if(bool(NbVectors)):
                for Loc_Vec in range(NbVectors):
                    if(Param_Simul==3):
                        Zones[Loc_Zone]['ShowVal'][Loc_Vec]=float(Zones[Loc_Zone]['Diameter'][Loc_Vec])
                    if(Param_Simul==2):
                        Zones[Loc_Zone]['ShowVal'][Loc_Vec]=abs(float(Zones[Loc_Zone]['Value'][Loc_Vec][Timing]))

                Loc=min(Zones[Loc_Zone]['ShowVal'])
                if(Extr[0]>Loc):
                    Extr[0]=Loc
                Loc=max(Zones[Loc_Zone]['ShowVal'])
                if(Extr[1]<Loc):
                    Extr[1]=Loc
        else:
            NbVectors=Zones[Loc_Zone]['NbrVec']
            if(bool(NbVectors)):
                for Loc_Vec in range(NbVectors):
                    Zones[Loc_Zone]['ShowVal'][Loc_Vec]='X'
    return Extr

#Sous-routine permettant d'identifier l'index du noeud le plus proche d'une liste
#node tuple de type (x,y)
# nodes liste de tuple de type [(x1,y1),(x2,y2),...]
def closest_node(node, nodes):
    nodes = np.asarray(nodes)
    deltas = nodes - node
    dist_2 = np.einsum('ij,ij->i', deltas, deltas)
    return np.argmin(dist_2),min(dist_2)

#Lecture ligne à ligne du fichier de paramètres ayant été établi
def Read_Param_file(ParamFile):
    Param={}
    Category_Name=['Time','General Parameters of the network','Simulation Parameters','IPOPT Optimization Parameters']
    Param[Category_Name[0]]={}
    Param[Category_Name[1]]={}
    Param[Category_Name[2]]={}
    Param[Category_Name[3]]={}
    #Préparation des différentes catégories de paramètres proposés
    Max_categories=len(Category_Name)-1
    Category_Sentence=['Time :','General Parameters of the network :','Simulation Parameters :','IPOPT Optimization Parameters :']
    file = open(ParamFile,'r')
    ctgr=-1
    i=0
    Special_Character='%'
    NewCateg_char=':'
    for New_Word in file:
        #Première partie liée aux informations génériques pour compléter ainsi le dictionnaire de Vecteurs
        i=i+1
        New_Word=New_Word.rstrip('\n')
        New_Word=New_Word.lstrip()
        if(New_Word[0]!=Special_Character):
            loc_cat=ctgr+1
            if(loc_cat>Max_categories):
                loc_cat=0
            Spec_char=New_Word[-1]
            if(Spec_char==NewCateg_char):
                Identif_Category=False
                #On recherche la gatégorie à laquelle les informations appartiennent
                cpt_pos=0
                for Categ in Category_Sentence:
                    if(New_Word==Categ):
                        LocCate=Category_Name[cpt_pos]
                        Identif_Category=True
                    cpt_pos += 1
            else:
                if(Identif_Category):
                    New_Word = New_Word.split('\t')    # string.whitespace contains all whitespace.
                    Param[LocCate][New_Word[0]]=[]
                    Param[LocCate][New_Word[0]].append(New_Word[1])
                    if(len(New_Word)>2):
                        Param[LocCate][New_Word[0]].append(New_Word[2])
                    else:
                        Param[LocCate][New_Word[0]].append('No comment')
                Test=1
        else:
            Test=1
    return Param

#Sous-routine dédiée à obtenir l'ensemble des informations disponibles sur les noeuds présentes dans le dossier du réseau
def Import_Nodes_Attributes(namepath,List_Nodes,Param,Type_Analysis):
    ## Première étape est d'obtenir le réel chemin d'accès aux fichiers géométriques de noeuds
    #Dossier Principal
    MainDir = namepath+'\\'
    Nodes={}
    Nodes['Reservoirs']={}
    Nodes['IncJunctions']={}
    #Fichier géométrique
    NodeTime=[0.0,0.0,0.0,0.0]
    start=time.time()
    GeomNodes=MainDir+'Reservoirs.vecr'
    Nodes['Reservoirs']=Read_Geom_Nodes(GeomNodes)
    GeomNodes=MainDir+'Extra_data_Junctions.jun'
    Nodes['IncJunctions']=Read_Geom_Nodes(GeomNodes)
    end=time.time()
    NodeTime[0]=end-start
    if(Type_Analysis==2):
        Test=1
        #On doit également compléter List_Nodes à ce moment sur base des fichiers construits et qui ont construit Nodes
        List_Nodes=Build_List_Nodes(List_Nodes,Nodes)
    start=time.time()
    #Comparaison à effectuer entre la liste de noeuds et les différents noeuds pour numéroter
    i=0

    if(Type_Analysis==1):
        List_Nodes['TypeNode']=['X']*len(List_Nodes['InitNode'])
        List_Nodes['NameNode']=['X']*len(List_Nodes['InitNode'])
        Type_Node='Reservoirs'
        Test=Define_Node_Pos(Nodes,Type_Node,List_Nodes)
        Type_Node='IncJunctions'
        Test=Define_Node_Pos(Nodes,Type_Node,List_Nodes)
        #On ajoute à présent dans les noeuds définis l'ensemble des noeuds qui ne se trouvaient pas dans la liste géométrique des noeuds intéressants
        Test=Add_Common_Nodes(Nodes['IncJunctions'],List_Nodes)
    end=time.time()
    NodeTime[1]=end-start
    start=time.time()

    #Recherche des différents attributs importants pour les réservoirs
    Found_Node={}
    Found_Node['Reservoirs']=[]
    Found_Node['IncJunctions']=[]
    MainAttr={}
    DftAttr={}
    ListedAttr={}
    MainAttr['Reservoirs']=['Section[m²]','Max. Height[m]','Min. Height[m]','Init_Cond[m³]','NbPatterns']
    DftAttr['Reservoirs']=['50.0','10.0','0.0','300','0']
    MainAttr['IncJunctions']=['NbPatterns']
    DftAttr['IncJunctions']=['0']
    ListedAttr['Reservoirs']=['SECTION','Max_H','Min_H','IC_V','NbPatterns']
    ListedAttr['IncJunctions']=['NbPatterns']
    if(bool(Nodes['Reservoirs'])):
        RsrvDir=MainDir+'Reservoirs\\'
        JuncDir=MainDir+'Extra_data_Junctions\\'
        List_Attr=['SECTION','Max_H','Min_H','IC_V']
        Attr_File=['SECTION.D','Max_Height.D','Minimum_H.D','IC_Reservoir.D']
        Test,Found_Node['Reservoirs']=Add_Node_Attributes(Nodes['Reservoirs'],RsrvDir,List_Attr,Attr_File,0)
        Test,Loc_Found_Node=Add_Node_Attributes(Nodes['Reservoirs'],RsrvDir,List_Attr,Attr_File,0)
    List_Attr=['Patterns','Consumers']
    Attr_File=['BC_Water_Exchanges.S','ConsMeters.I']
    if(bool(Nodes['IncJunctions'])):
        Test,Found_Node['IncJunctions']=Add_Node_Attributes(Nodes['IncJunctions'],JuncDir,List_Attr,Attr_File,1)
        Found_Node['IncJunctions']=[Found_Node['IncJunctions'][0]]
    List_Attr=['Patterns']
    Attr_File=['BC_Water_Exchanges.S']
    if(bool(Nodes['Reservoirs'])):
        Test,Loc_Found_Node=Add_Node_Attributes(Nodes['Reservoirs'],RsrvDir,List_Attr,Attr_File,1)
    Test=Add_Pattern_Dft_Value(Nodes)
    end=time.time()
    NodeTime[2]=end-start
    start=time.time()
    #On ajoute également les données temporelles de résultat du réseau
    if(bool(Nodes['Reservoirs'])):
        Nodes=Add_Node_Time3(Nodes,'Reservoirs',RsrvDir,Param)
    if(bool(Nodes['IncJunctions'])):
        Nodes=Add_Node_Time3(Nodes,'IncJunctions',JuncDir,Param)
    end=time.time()
    NodeTime[3]=end-start
    Test=1
    return Nodes,MainAttr,ListedAttr,DftAttr,Found_Node

#Sous-routine
def Build_List_Nodes(List_Nodes,Nodes):
    Test=1
    TypeN=['Reservoirs','IncJunctions']
    NbNode=[0,0]
    Cpt_Node=0
    Cpt_Type=0
    for TypeNode in TypeN:
        for Node in Nodes[TypeNode]:
            NbNode[Cpt_Type]+=1
            List_Nodes['NbrEl'].append(NbNode[Cpt_Type])
            List_Nodes['CoordPlan'].append(Nodes[TypeNode][Node]['CoordPlan'])
            Coord=(Nodes[TypeNode][Node]['CoordPlan'][0],Nodes[TypeNode][Node]['CoordPlan'][1],Nodes[TypeNode][Node]['CoordZ'])
            List_Nodes['Coord'].append(Coord)
            List_Nodes['InitNode'].append(0)
            List_Nodes['TypeNode'].append(TypeNode)
            List_Nodes['NameNode'].append(Node)
            List_Nodes['SpecNode'].append(0)
            Nodes[TypeNode][Node]['IndPos']=Cpt_Node
            Cpt_Node+=1
        Cpt_Type+=1
    return List_Nodes

#Sous-routine dédiée à obtenir l'ensemble des informations disponibles sur les tronçons présents dans le dossier du réseau
def Import_Vector_Attributes(namepath,Zones,Param,List_Position):
    Test=1
    ## Première étape est d'obtenir le réel chemin d'accès aux fichiers géométriques de noeuds
    #Dossier Principal
    MainDir = namepath+'\\'
    LocDir=MainDir+'Network_Vectors\\'
    #Partie Pipes
    List_Attr=['Diameter','Length','Rough_Coeff','Material','IC_Cond','Type_Law']
    Attr_File=['Diameter.D','Length.D','Rugosity.D','Material.S','IC_Vector.D','Pump_Type.I']
    Zones,Found_Files=Add_Vector_Attributes(Zones,LocDir,List_Attr,Attr_File)
    #Partie valves
    List_Attr=['Length','Height','Width','Type_Valve','IC_Cond']
    Attr_File=['Length_valve.D','Height.D','Width.D','Type_of_Valve.S','IC_Vector.D']
    Zones,Found_Files=Add_Vector_Attributes(Zones,LocDir,List_Attr,Attr_File)
    #Partie valves : additionnel : ajout des coefficients de valves si c'est justifié
    Zones=Add_Spec_Vec_Attr_Valves(Zones,LocDir)
    #Partie Pompes : ajout d'attributs spéciaux basés sur la présence de fichiers et de leur éventuel remplissage
    Zones,Found_FilesB=Add_Spec_Vec_Attributes(Zones,LocDir)
    #On va également rechercher à sauvegarder l'ensemble des résultats sur les différents pas de temps du réseau
    Zones=Add_Vector_Time(Zones,LocDir,Param)
    #Dernière étape consacrée à apporter à chaque vecteur sa numérotation indirecte présente dans List_Position
    Zones=Add_Indirect_Position(Zones,List_Position)
    return Zones

def Define_Node_Pos(Nodes,Type_Node,List_Nodes):
    i=0
    ListCoord=[]
    for NodeName in Nodes[Type_Node]:
        Coord=Nodes[Type_Node][NodeName]['CoordPlan']

        #On fait la recherche dans la liste des noeuds établis en s'assurant que la relation soit bien acceptable
        Index,dist=closest_node(Coord, List_Nodes['CoordPlan'][:])
        if(dist<0.1):
            Nodes[Type_Node][NodeName]['IndPos']=Index
            test=1
            List_Nodes['InitNode'][Index]=0
            List_Nodes['TypeNode'][Index]=Type_Node
            List_Nodes['NameNode'][Index]=NodeName
        else:
            logging.info('Node %s is not connected to the network' % Nodes[Type_Node][NodeName]['IndPos'])

        i=i+1
    test=1
    return test

#Lecture d'un fichier géométrique de noeuds
def Read_Geom_Nodes(FilePath):
    #Initialisation : chaque noeud est un dictionnaire dont le nom d'entrée est bien le nom du noeud en questio
    Nodes={}

    #Lecture du fichier
    if(os.path.isfile(FilePath)):
        file = open(FilePath,'r')
        Special_char=','
        i=0
        for New_Word in file:
            #Première partie liée aux informations génériques pour compléter ainsi le dictionnaire de Vecteurs
            i=i+1
            New_Word=New_Word.rstrip('\n')
            if(i>1):
                Words=re.split(r'\,', New_Word)
                #Words=Extract_SubStrings(New_Word,Special_char)
                if(len(Words)==4):
                    Nodes[Words[3]]={}
                    Nodes[Words[3]]['CoordPlan']=(float(Words[0]),float(Words[1]))
                    Nodes[Words[3]]['CoordZ']=float(Words[2])
                    Nodes[Words[3]]['IndPos']=-1
                test=2
    else:
        Message='There is no following file in the specified path :'+FilePath
        logging.info(Message)

    return Nodes

#Ajout de l'ensemble des noeuds qui ne se retrouvent pas dans liste géométrique
def Add_Common_Nodes(Nodes,List_Nodes):
    New_Node='Add_Node'
    cpt_add_node=0
    i=0
    test=1
    cpt_node=0
    for i in range(len(List_Nodes['Coord'])):
        if(List_Nodes['InitNode'][i]==-1):
            cpt_add_node=cpt_add_node+1
            Loc_Name_Node=New_Node+str(cpt_add_node)
            Nodes[Loc_Name_Node]={}
            Nodes[Loc_Name_Node]['CoordPlan']=(float(List_Nodes['Coord'][i][0]),float(List_Nodes['Coord'][i][1]))
            Nodes[Loc_Name_Node]['CoordZ']=float(List_Nodes['Coord'][i][2])
            Nodes[Loc_Name_Node]['IndPos']=List_Nodes['NbrEl'][i]
    return test

#Ajout des différents attributs pertinents des réservoirs dans le réseau
def Add_Node_Attributes(El_List,MainDir,List_Attr,Attr_File,Spec_Case):
    Spec_char=','
    Cpt_attrib=-1
    #cp = cProfile.Profile()
    #cp.enable()
    Found_File=[1]*len(List_Attr)
    for Attr in List_Attr:
        Cpt_attrib=Cpt_attrib+1
        filename=MainDir+Attr_File[Cpt_attrib]
        File_To_Read=os.path.isfile(filename)
        if(File_To_Read):
            with open(filename) as f:
                content = f.readlines()
            content = [x.rstrip('\n') for x in content]

            if(Spec_Case==1):
                for NodeName in El_List:
                    El_List[NodeName][Attr]=['X']
            else:
                for NodeName in El_List:
                    El_List[NodeName][Attr]='X'
            i=0

            for New_Word in content:
                i += 1
                if(i>=2):
                    List_sbstr=re.split(r'\,', New_Word)
                    #List_sbstr=Extract_SubStrings(New_Word,Spec_char)
                    NameNode=List_sbstr[0]
                    if(NameNode in El_List):
                        if(isinstance(El_List[NameNode][Attr],list)):
                            if(len(El_List[NameNode][Attr])==1):
                                El_List[NameNode][Attr][0]=List_sbstr[1]
                            else:
                                El_List[NameNode][Attr].append(List_sbstr[1])
                        else:
                            El_List[NameNode][Attr]=List_sbstr[1]
                    else:
                        Test=1
        else:
            logging.info('The following file does not exist : %s' % filename)
            Found_File[Cpt_attrib]=0
    #cp.disable()
    #cp.print_stats()
    Test=1
    return Test,Found_File

#Partie liée à toujours ajouter à chaque jonction incompressible une valeur supplémentaire et de pattern et consumer afin de laisser la possibilité aux utilisateurs en édition d'en ajouter un
def Add_Pattern_Dft_Value(Nodes):
    TypeNode=['IncJunctions','Reservoirs']
    Spec_Attr={}
    Spec_Attr['IncJunctions']=['Patterns','Consumers']
    Spec_Attr['Reservoirs']=['Patterns']
    Dft_Val='X'
    Test=1
    for Type in TypeNode:
        if(bool(Nodes[Type])):
            for NameNode in Nodes[Type]:
                for Attr in Spec_Attr[Type]:
                    if(Attr in Nodes[Type][NameNode]):
                        if(Nodes[Type][NameNode][Attr][-1]!=Dft_Val):
                            Nodes[Type][NameNode][Attr].append(Dft_Val)
                    else:
                        Nodes[Type][NameNode][Attr]=['X']

    return Test

#Partie liée aux attributs cette fois pour les différents types de vecteurs
def Add_Vector_Attributes(Zones,MainDir,List_Attr,Attr_File):
    #cp = cProfile.Profile()
    #cp.enable()
    Found_File=[1]*len(List_Attr)
    Cpt_attrib=-1
    for Attr in List_Attr:
        Cpt_attrib=Cpt_attrib+1
        filename=MainDir+Attr_File[Cpt_attrib]
        File_To_Read=os.path.isfile(filename)
        if(File_To_Read):
            file = open(filename,'r')
            Nb_Zones=len(Zones)
            ValFix=[]
            for i in range(Nb_Zones):
                ValFix.append(-1)

            i=0
            for New_Word in file:
                #Première partie liée aux informations génériques pour compléter ainsi le dictionnaire de Vecteurs
                i=i+1
                New_Word=New_Word.rstrip('\n')
                #Ligne décomposée en trois parties : numéro de zone, vecteur puis valeur de l'attribut
                List_sbstr=New_Word.split()
                if(bool(List_sbstr)):
                    if(int(List_sbstr[1])==1257):
                        Test=1
                    Numero_Zone=int(List_sbstr[0])-1
                    if(ValFix[Numero_Zone]==-1): #Une seule phase d'initialisation à effectuer
                        ValFix[Numero_Zone]=0
                        Zones[Numero_Zone][Attr]=['X']*Zones[Numero_Zone]['NbrVec']

                    Numero_Vec=int(List_sbstr[1])-1
                    Zones[Numero_Zone][Attr][Numero_Vec]=List_sbstr[2]
        else:
            logging.info('The following file does not exist : %s' % filename)
            Found_File[Cpt_attrib]=0
    #cp.disable()
    #cp.print_stats()
    return Zones,Found_File

#On va ajouter cette fois les valeurs à chaque pas de temps afin de permettre la représentation des résultats à chaque pas de temps
def Add_Vector_Time(Zones,LocDir,Param):
    local_file=['PIPE_FIRST_DIS.pidb','PUMP_FIRST_DIS.pudb','VALVE_FIRST_DIS.vadb','DEVER_FIRST_DIS.dvdb','VALVE_OPEN.vaop']
    Id_Zone=[0,1,2,3,2]
    Arg_Attr=['Value','Value','Value','Value','Opening_Factor']
    Nb_Time=int(Param['Time']['Type of time network evaluation'][0])
    Nb_total_Time=int(Param['Time']['Number of time used steps'][0])
    Nb_Time_steps=int(Param['Time']['Number of time save steps'][0])

    Nb_Lines_to_read=Nb_total_Time
    Nb_remaining_Lines=Nb_Time_steps-Nb_total_Time
    if(Nb_total_Time>Nb_Time_steps):
        Nb_Lines_to_read=Nb_Time_steps
        Nb_remaining_Lines=Nb_total_Time-Nb_Time_steps

    cpt_file=0
    for loc_file in local_file:
        filename=LocDir+loc_file
        if(os.path.isfile(filename)):
            with open(filename) as f:
                content = f.readlines()
            content = [x.rstrip('\n') for x in content]
            NbVec=int(Zones[Id_Zone[cpt_file]]['NbrVec'])
            zeroArray = [0.0] * Nb_total_Time
            Zones[Id_Zone[cpt_file]][Arg_Attr[cpt_file]]=[zeroArray[:] for i in range(NbVec)]
            Zones[Id_Zone[cpt_file]]['ShowVal']=[0.0]*NbVec

            cpt_Entry=0
            Nb_Entries=len(content)
            for Nb_Entry in range(len(content)):
                #Lecture du nom
                New_Word=re.split(r'\,', content[cpt_Entry])
                cpt_Entry += 1
                NbVec=int(New_Word[1])-1
                Zones[Id_Zone[cpt_file]][Arg_Attr[cpt_file]][NbVec]=content[cpt_Entry:cpt_Entry+Nb_Lines_to_read]
                cpt_Entry += Nb_Lines_to_read

                if(Nb_total_Time<Nb_Time_steps):
                    cpt_Entry += Nb_remaining_Lines
                Test=1

                if(cpt_Entry>=Nb_Entries):
                    break
        cpt_file+=1
    Test=1
    return Zones

#Sous-routine utilisée pour ajouter numérotation indirecte à chaque vecteur
def Add_Indirect_Position(Zones,List_Position):
    for LocZone in Zones:
        NbVec=LocZone['NbrVec']
        if(bool(NbVec)):
            LocZone['IndPos']=[0]*NbVec
        Test=1
    for Index in range(len(List_Position['IdZone'])):
        NumZone=List_Position['IdZone'][Index]
        NumVec=List_Position['NbrElVec'][Index]
        if(NumZone==2):
            Test=1
        if(NumVec>len(Zones[NumZone]['IndPos'])):
            Test=1
        Zones[NumZone]['IndPos'][NumVec]=Index
    return Zones

#Sous-routine utilisée en vue de pouvoir inclure les lois de charge/power d'une pompe/turbine
def Add_Spec_Vec_Attributes(Zones,MainDir):
    List_Attr=['Coefficients','Coefficients']
    Attr_File=['Coeff_Pumps.coef','Pu_Tu_coeff.tcef']
    #On regarde déjà si au fait s'il y a ou non des pompes dans le réseau
    NbVectors=Zones[1]['NbrVec']
    Found_Files=[0,0]
    Special_char=','
    if(bool(NbVectors)):
        for ID in range(len(Zones[1]['Type_Law'])):
            Zones[1]['Type_Law']=int(Zones[1]['Type_Law'][ID])
        #Deux cas de fichiers sont pour le moment proposé : 1 simple basé sur loi H(Q) et l'autre sur loi de comportement plus complexes
        LocDir=MainDir+Attr_File[0]
        Attr_Pump=[]
        Zones[1]['Coefficients']=[]
        Zones[1]['Type']=[]
        for i in range(NbVectors):
            Attr_Pump.append(False)
            Zones[1]['Coefficients'].append([])
            Zones[1]['Type'].append(0)
        if(os.path.isfile(LocDir)):
            #Le fichier existe mais on doit vérifier que le fichier apport des informations utiles
            file = open(LocDir,'r')
            Found_Pump=False
            for New_Word in file:
                New_Word=New_Word.strip('\n')
                New_Word=New_Word.rstrip()
                for i in range(NbVectors):
                    if(Zones[1]['Name'][i]==New_Word):
                        Attr_Pump[i]=True
                        Found_Pump=True
                        #On fait alors la lecture
                        Value=file.readline().rstrip('\n')
                        #Value=Extract_SubStrings(Value,Special_char)
                        Value=re.split(r'\,', Value)
                        Zones[1]['Type'][i]=int(Value[0])
                        Nb_coeff=int(Value[1])
                        for k in range(Nb_coeff):
                            Value=file.readline().rstrip('\n')
                            if(Zones[1]['Type'][i]<0):
                                Value=re.split(r'\,', Value)
                                #Value=Extract_SubStrings(Value,Special_char)
                            else:
                                Zones[1]['Coefficients'][i].append(Value)
                if(not(Found_Pump)):
                    break
        else:
            Found_Files[0]=0
        LocDir=MainDir+Attr_File[1]
        if(os.path.isfile(LocDir)):
            #Le fichier existe mais on doit vérifier que le fichier apport des informations utiles
            file = open(LocDir,'r')
            Found_Pump=False
            Spec_Pump=False
            #Structure du fichier:
            #Type element,Numéro élément de son type, Nom Element
            #Param sigmoïde H(Q),Param sigmoïde P(Q)
            #Param sigmoïde Hbep(Q),Param sigmoïde Pbep(Q)
            #Nbr coeffs H(Q),Nbr coeffs P(Q),Nbr coeffs Hbep(Q),Nbr coeffs Hbep(Q)
            #Une ligne par coefficient pour des relations polynomiales en allant du plus faible coefficient au plus élevé
            for New_Word in file:
                New_Word=New_Word.strip('\n')
                New_Word=New_Word.rstrip()
                New_Word=re.split(r'\,', New_Word)
                #New_Word=Extract_SubStrings(New_Word,Special_char)
                for i in range(NbVectors):
                    if(Zones[1]['Type_Law']<0):
                        if(len(New_Word)>2):
                            if(Zones[1]['Name'][i]==New_Word[2] and New_Word[0]=='2' and Zones[1]['Type'][i]==0):
                                Attr_Pump[i]=True
                                Found_Pump=True
                                Zones[1]['Type'][i]='-1'
                                if(not(Spec_Pump)):
                                    Zones=Initialise_Sigm_Pump(Zones)
                                    Test=1
                                #Première ligne dédiée
                                Value=file.readline().rstrip('\n')
                                Value=re.split(r'\,', Value)
                                if(len(Value)==2):
                                    Zones[1]['KH'][i]=Value[0]
                                    Zones[1]['KP'][i]=Value[1]
                                else:
                                    Test=1 #Problème sur fichier ainsi proposé
                                Value=file.readline().rstrip('\n')
                                Value=re.split(r'\,', Value)
                                if(len(Value)==2):
                                    Zones[1]['KHBep'][i]=Value[0]
                                    Zones[1]['KPBep'][i]=Value[1]
                                else:
                                    Test=1 #Problème sur fichier ainsi proposé
                                NbrValue=file.readline().rstrip('\n')
                                NbrValue=re.split(r'\,', NbrValue)
                                if(len(Value)==4):
                                    for j in range(len(NbrValue)):
                                        for k in range(int(NbrValue[j])):
                                            Value=file.readline().rstrip('\n')
                                            if(j==0):
                                                Zones[1]['Coefficients'][i].append(Value)
                                            if(j==1):
                                                Zones[1]['CoefficientsP'][i].append(Value)
                                            if(j==2):
                                                Zones[1]['CoeffHBep'][i].append(Value)
                                            if(j==3):
                                                Zones[1]['CoeffPBep'][i].append(Value)

            file.close()
        else:
            Found_Files[1]=0


            Test=1
    return Zones,Found_Files

#Sous-routine pour initialiser l'ensemble des données utiles pour la mise en place de pompes/turbines de type "sigmoïdes" fonctionnant sur deux quadrants
def Initialise_Sigm_Pump(Zones):
    NbVectors=Zones[1]['NbrVec']
    New_Simpl_Attr=['KH','KP','KHBep','KPBep']
    for Attr in New_Simpl_Attr:
        Zones[1][Attr]=[]
        for i in range(NbVectors):
            Zones[1][Attr].append(0.0)
    New_List_attr=['CoefficientsP','CoeffHBep','CoeffPBep']
    for Attr in New_List_attr:
        Zones[1][Attr]=[]
        for i in range(NbVectors):
            Zones[1][Attr].append([])
    return Zones

#Sous-routine utilisée pour compléter les paramètres des valves
def Add_Spec_Vec_Attr_Valves(Zones,MainDir):

    List_Attr=['VALVE_COEF','VALVE_OPEN']
    Attr_File=['VALVE_COEF.vaco','VALVE_OPEN.vaop']
    #On regarde déjà si au fait s'il y a ou non des pompes dans le réseau
    Pos_Zone=2
    NbVectors=Zones[Pos_Zone]['NbrVec']
    Found_Files=[0,0]
    Special_char=','
    if(bool(NbVectors)):
        Names_ID=['vanne_aiguille','vanne_levante','vanne_robinet','vanne_papillon']
        New_Name=['aiguille','levante','robinet','papillon']
        Spec_Valve=False
        cpt_pos=0
        Zones[Pos_Zone]['Coeff_Valve']=[]
        for Type_Valve in Zones[Pos_Zone]['Type_Valve']:
            Zones[Pos_Zone]['Coeff_Valve'].append([])
            for Loc_Name in Names_ID:
                if(Type_Valve==Loc_Name):
                    Zones[Pos_Zone]['Type_Valve'][cpt_pos]=New_Name[cpt_pos]
            #On va ouvrir les fichiers supplémentaires nécessaires si type de valve est présent
            if(Zones[Pos_Zone]['Type_Valve'][cpt_pos]==New_Name[0]):
                Spec_Valve=True
            cpt_pos+=1
        #On vient ouvrir le fichier si une valve spéciale est au moins présente dans le réseau
        if(Spec_Valve):
            LocDir=MainDir+Attr_File[0]
            if(os.path.isfile(LocDir)):
                #Le fichier existe mais on doit vérifier que le fichier apport des informations utiles
                file = open(LocDir,'r')
                cpt_line=0
                for New_Word in file:
                    New_Word=New_Word.strip('\n')
                    New_Word=New_Word.rstrip()
                    if(cpt_line==0):
                        New_Word=re.split(r'\,', New_Word)
                        if(len(New_Word)==3):
                            Ind_Vector=New_Word[0]
                            Ind_Valve=int(New_Word[1])
                            Name_Vec=New_Word[2]
                        else:
                            break
                    if(cpt_line==1):
                        Nb_Coeff=int(New_Word)
                        for Loc_Coeff in range(Nb_Coeff):
                            Value=file.readline().rstrip('\n')
                            Value=Value.rstrip()
                            Zones[Pos_Zone]['Coeff_Valve'][Ind_Valve-1].append(Value)
                    cpt_line+=1
                    if(cpt_line==2):
                        cpt_line=0
                file.close()
    return Zones

#Sous-routine alternative pour chercher à augmenter la vitesse de la sous-routine
def Add_Node_Time3(Nodes,Type_Node,LocDir,Param):

    start=time.time()
    LocFile=LocDir+'CHR_FIRST_VAL.D'
    File_To_Read=os.path.isfile(LocFile)
    if(File_To_Read):
        with open(LocFile) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        end=time.time()
        NodeTime=end-start

        start=time.time()
        #On cherche uniquement à conserver la charge, il faut donc transformer le volume en charge
        p_atmospheric=10.3261977573904

        Special_char=','
        Nb_Time=int(Param['Time']['Type of time network evaluation'][0])
        Nb_total_Time=int(Param['Time']['Number of time used steps'][0])
        Nb_Time_steps=int(Param['Time']['Number of time save steps'][0])
        SECTION_Attrib='SECTION'
        Sect_Apply={}
        Sect_Apply['Reservoirs']=1.0
        Sect_Apply['IncJunctions']=0.0
        for NameNode in Nodes[Type_Node]:
            Nodes[Type_Node][NameNode]['ValueH']=[0.0]*Nb_total_Time
            Nodes[Type_Node][NameNode]['ShowVal']=[0.0]*Nb_total_Time

        Nb_Lines_to_read=Nb_total_Time
        Nb_remaining_Lines=Nb_Time_steps-Nb_total_Time
        if(Nb_total_Time>Nb_Time_steps):
            Nb_Lines_to_read=Nb_Time_steps
            Nb_remaining_Lines=Nb_total_Time-Nb_Time_steps
        #Première partie dédiée à la construction pour chaque noeud de sa propre liste

        Values=content
        Nb_Entries=len(Values)
        cpt_Entry=1
        end=time.time()
        NodeTime=end-start
        start=time.time()
        Nb_eval=Nb_Entries
        P_atm=10.3124
        if(bool(Nodes[Type_Node])):
            for Entry in range(Nb_Entries):
                #On accède à ce moment au nom de l'élément
                cpt_elem=0
                New_Word=Values[cpt_Entry]
                cpt_Entry += 1
                #On doit d'abord s'assurer d'identifier correctement l'information
                if(New_Word in Nodes[Type_Node]):
                    #TestValue=Values[cpt_Entry:cpt_Entry+Nb_Lines_to_read-1]
                    if(Sect_Apply[Type_Node]==1.0):
                        Sect_val=float(Nodes[Type_Node][New_Word][SECTION_Attrib])
                        cpt_pos=cpt_Entry
                        for Elem in Values[cpt_Entry:cpt_Entry+Nb_Lines_to_read]:
                            Values[cpt_pos]=str((float(Elem))/Sect_val+Nodes[Type_Node][New_Word]['CoordZ']+P_atm)
                            cpt_pos+=1
                    Nodes[Type_Node][New_Word]['ValueH'][0:Nb_Lines_to_read]=Values[cpt_Entry:cpt_Entry+Nb_Lines_to_read]
                else:
                    cpt_Entry=cpt_Entry-1
                cpt_Entry += Nb_Lines_to_read


                if(Nb_total_Time<Nb_Time_steps):
                    cpt_Entry += Nb_remaining_Lines

                if(cpt_Entry==Nb_eval):
                    break
        end=time.time()
        NodeTime=end-start
    else:
        logging.info('The following file does not exist : %s' % LocFile)
    return Nodes

#Ajout des différents attributs princopaux devant être montrés à l'utilisateur
def Add_Main_Attributes(Zones,Nodes):
    #Partie liée aux vecteurs
    Nb_Zones=len(Zones)

    Zones[0]['Princ_Attrib']=['Name','Diameter','Length','Rough_Coeff','Material','IC_Cond']
    Zones[0]['Name_Attrib']=['Name','Diameter[m]','Length[m]','Rough_Coeff','Material','IC_Cond[m³/s]']
    if(Nb_Zones>=2):#Zone des pompes
        Zones[1]['Princ_Attrib']=['Name','IC_Cond','Coefficients']
        Zones[1]['Name_Attrib']=['Name','IC_Cond[m³/s]','Coefficient']
    if(Nb_Zones>=3):#Zone des valves
        Zones[2]['Princ_Attrib']=['Name','Width','Height','Length','Type_Valve','Coeff_Valve','IC_Cond']
        Zones[2]['Name_Attrib']=['Name','Width[m]','Height[m]','Length[m]','Type_Valve','Coeff of valves','IC_Cond[m³/s]']

    #Partie liée aux noeuds
    Nodes['Name_Attrib']={}
    Nodes['Princ_Attrib']={}
    Nodes['Princ_Attrib']['Reservoirs']=['Name','IndPos','SECTION','IC_V','Max_H','CoordZ','Patterns']
    Nodes['Princ_Attrib']['IncJunctions']=['Name','IndPos','Type','CoordZ','Consumers','Patterns',]
    Nodes['Name_Attrib']['Reservoirs']=['Name','ID','Section[m²]','IC_V[m³]','Max_H[m]','CoordZ[m]','Patterns']
    Nodes['Name_Attrib']['IncJunctions']=['Name','ID','Type','CoordZ[m]','Consumers','Patterns']
    return Zones,Nodes

#Importation des différents patterns d'un réseau
def Import_Patterns(MainPath):
    Ptrn_Dir=MainPath+'\\Patterns'
    Patterns={}
    SubAttributes=['Values','Exch_Opt','Meth_Interp','Calendar','Prtn_Link']
    Dflt_Val=[[],'-1','0','1',[0,1]]
    #Lecture du fichier d'échanges sur variables d'optimisation pour lire en plus noms d'échanges
    Name_file='\\Exchange_var.I'
    New_Patterns=True
    Param_Case=1
    Patterns=Read_Pattern_Attributes(Patterns,Ptrn_Dir,Name_file,'Exch_Opt',Param_Case,SubAttributes,Dflt_Val)
    Name_file='\\Interpol_exchange.I'
    Param_Case=2
    Patterns=Read_Pattern_Attributes(Patterns,Ptrn_Dir,Name_file,'Meth_Interp',Param_Case,SubAttributes,Dflt_Val)
    #Deuxième étape consacrée à récupérer chaque dossier d'échange pour construire différents Patterns

    list_patterns_with_paths = [f.path for f in os.scandir(Ptrn_Dir) if f.is_dir()]
    for i in range(len(list_patterns_with_paths)):
        Patterns=Read_PatternsDir(Patterns,list_patterns_with_paths[i],SubAttributes)
    Test=1
    return Patterns

#Lecture d'une catégorie d'informations pour compléter
def Read_Pattern_Attributes(Patterns,Ptrn_Dir,Name_file,Attr_Name,Param_Case,SubAttributes,Dflt_Val):
    Attr_file=Ptrn_Dir+Name_file
    Special_char=','
    if(os.path.isfile(Attr_file)):
        file = open(Attr_file,'r')
        for New_Word in file:
            #On accède à ce moment pour chaque ligne aux informations pertinentes
            New_Word=New_Word.strip('\n')
            New_Word=re.split(r'\,', New_Word)
            #New_Word=Extract_SubStrings(New_Word,Special_char)
            if(New_Word[0] in Patterns):
                if(New_Word[0] in Patterns):
                    Patterns[New_Word[0]][Attr_Name]=New_Word[1]
                else:
                    Patterns[New_Word[0]]={}
                    cpt_attr=0
                    for Attr in SubAttributes:
                        Patterns[New_Word[0]][Attr]=Dflt_Val[cpt_attr]
                        cpt_attr += 1
                    Patterns[New_Word[0]][Attr_Name]=New_Word[1]

        file.close()

    return Patterns

#Lecture de chaque pattern afin d'accéder à ses données
def Read_PatternsDir(Patterns,Ptrn_Dir,SubAttributes):
    Special_char=','
    Dflt_Val=[[],'-1','0','1',[0,1]]
    #Extraction du nom de Pattern
    Loc_Dir = os.path.basename(Ptrn_Dir)
    Loc_Dir=re.split(r'\,', Loc_Dir)
    Ptrn_Name=Loc_Dir[0]
    Loc_Ptrn=Ptrn_Dir+'\\'
    Spec_file=['Prtn_Link.I','Calendar.I']
    Days=[[],[]]
    Calendar=[]
    Loc_Val=Dflt_Val
    #On vient remplir les valeurs
    if(not(Ptrn_Name in Patterns)):
        Patterns[Ptrn_Name]={}
        cpt_attr=0
        for Attr in SubAttributes:
            Patterns[Ptrn_Name][Attr]=Loc_Val[cpt_attr]
            cpt_attr += 1
    #Remplissage des informations
    for j in range(len(Spec_file)):
        Loc_file=Loc_Ptrn+Spec_file[j]
        if(os.path.isfile(Loc_file)):
            file = open(Loc_file,'r')
            if(j==0):
                Test=2
                for New_Word in file:
                    #On accède à ce moment pour chaque ligne aux informations pertinentes
                    New_Word=New_Word.strip('\n')
                    New_Word=re.split(r'\,', New_Word)
                    if(len(New_Word)>1):
                        Days[0].append(int(New_Word[0]))
                        Days[1].append(New_Word[1])
                Patterns[Ptrn_Name]['Prtn_Link']=[Days[0][-1],Days[1][-1]]
            else:
                for New_Word in file:
                    #On accède à ce moment pour chaque ligne aux informations pertinentes
                    New_Word=New_Word.strip('\n')
                    if(New_Word!=''):
                        Calendar.append(int(New_Word))
                Patterns[Ptrn_Name]['Calendar']=Calendar
            file.close()

    #On parcoure le calendrier pour compléter le Pattern concerné
    To_Attr_Columns=True
    for i in range(len(Calendar)):
        for j in range(len(Days[1])):
            if(Days[0][j]==Calendar[i]):
                #On va considérer la lecture du fichier
                Loc_file=Loc_Ptrn+Days[1][j]
                file = open(Loc_file,'r')
                #Ligne reprenant le nombre de lignes
                Value=file.readline().rstrip('\n')
                for New_Word in file:
                    #On accède à ce moment pour chaque ligne aux informations pertinentes
                    New_Word=New_Word.strip('\n')
                    #On doit identifier le nombre d'informations
                    New_Word = New_Word.split()
                    cpt_word=0
                    if(To_Attr_Columns):
                        for Word in New_Word:
                            Patterns[Ptrn_Name]['Values'].append([])
                            Patterns[Ptrn_Name]['Values'][cpt_word].append(Word)
                            cpt_word=cpt_word+1
                        To_Attr_Columns=False
                    else:
                        cpt_word=0
                        for Word in New_Word:
                            Patterns[Ptrn_Name]['Values'][cpt_word].append(Word)
                            cpt_word=cpt_word+1
                file.close()
                break

    Test=1
    return Patterns
    #Fonction permettant d'obtenir superscript
    def get_super(x):
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
        super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
        res = x.maketrans(''.join(normal), ''.join(super_s))
        return x.translate(res)

##Partie liée à l'exportation des informations
def Export_Vec_Attributes(Zones,Param,Path):
    #Première étape est la création du sous-dossier vecteur si celui-ci n'existe pas
    Directory=Path+'\\Network_Vectors'
    if(not(os.path.isdir(Directory))):
        try:
            os.mkdir(Directory)
        except OSError:
            logging.warning("Creation of the directory %s failed" % Directory)
    #Deuxième étape est donc d'ajouter les différents fichiers d'attributs
    Attributes=[[],[],[],[]]
    ListFilename=[[],[],[],[]]
    Attributes[0]=['Diameter','IC_Cond','Length','Material','Rough_Coeff']
    ListFilename[0]=['\\Diameter.D','\\IC_Vector.D','\\Length.D','\\Material.S','\\Rugosity.D']
    Attributes[1]=['IC_Cond']
    ListFilename[1]=['\\IC_Vector.D']
    Attributes[2]=['Length','Height','Width','Type_Valve','IC_Cond']
    ListFilename[2]=['\\Length_valve.D','\\Height.D','\\Width.D','\\Type_of_Valve.S','\\IC_Vector.D']
    Spec_Files=['IC_Cond']
    Init_Spec_File=[0]
    Nb_total_Time=int(Param['Time']['Number of time used steps'][0])
    for ID_Zone in range(len(Zones)):
        Nb_attr=0
        if(bool(Zones[ID_Zone]['NbrVec'])):
            for NewAttr in Attributes[ID_Zone]:
                Filename=Directory+ListFilename[ID_Zone][Nb_attr]
                Nb_attr += 1
                #On va d'abord retirer son contenu sauf s'il s'agit d'un fichier d'attribut spécifique
                if(NewAttr in Spec_Files):
                    #Vérification si le fichier a été ou non déjà initialisé
                    for i in range(len(Spec_Files)):
                        if(Spec_Files[i]==NewAttr):
                            if(Init_Spec_File[i]==0):
                                Init_Spec_File[i]=1
                                f = open(Filename, 'w')
                                f.truncate(0)
                            else:
                                f = open(Filename, 'a')
                else:
                    f = open(Filename, 'w')
                    f.truncate(0)
                #On vient donc ajouter ligne par ligne les informations pertinentes
                Loc_Zone=ID_Zone+1
                if(NewAttr in Zones[ID_Zone]):
                    for i in range(len(Zones[ID_Zone][NewAttr])):
                        Loc_Vec=i+1
                        Loc_Val=Zones[ID_Zone][NewAttr][i]
                        if(ID_Zone==2 and NewAttr=='Type_Valve'):
                            Loc_Val='vanne_'+Loc_Val
                        String=str(Loc_Zone)+" "+str(Loc_Vec)+" "+str(Loc_Val)+'\n'
                        f.write(String)
                f.close()
        test=1

    #Fichiers spéciaux à envoyer également comme les fichiers de type coefficients de pompes

    #Fichier de valeurs à chaque pas de temps à également sauvegarder
    local_file=['\\PIPE_FIRST_DIS.pidb','\\PUMP_FIRST_DIS.pudb','\\VALVE_FIRST_DIS.vadb','\\DEVER_FIRST_DIS.dvdb','\\VALVE_OPEN.vaop','\\VALVE_COEF.vaco']
    ID_Zone=[0,1,2,3,2,2]
    Arg_Attr=['Value','Value','Value','Value','Opening_Factor','Coeff_Valve']
    Time_File=[1,1,1,1,1,2]
    cpt_file=0
    for loc_file in local_file:
        NbVectors=Zones[ID_Zone[cpt_file]]['NbrVec']
        if(bool(NbVectors) and Arg_Attr[cpt_file] in Zones[ID_Zone[cpt_file]]):
            if(bool(Zones[ID_Zone[cpt_file]][Arg_Attr[cpt_file]])):
                Filename=Directory+loc_file
                f = open(Filename, 'w')
                Loc_Zone=ID_Zone[cpt_file]+1
                for i in range(NbVectors):
                    Loc_Vec=i+1
                    String=str(Loc_Zone)+','+str(Loc_Vec)+','+Zones[ID_Zone[cpt_file]]['Name'][i]+'\n'
                    f.write(String)
                    Nb_Val=0
                    if(Time_File[cpt_file]==1):
                        for Value in Zones[ID_Zone[cpt_file]][Arg_Attr[cpt_file]][i]:
                            String=str(Value)+'\n'
                            f.write(String)
                            Nb_Val+=1
                        #On est amené à exporter le nombre de valeurs attendues
                        if(Nb_Val<Nb_total_Time):
                            Nb_val=Nb_total_Time-Nb_Val
                            for Index in range(Nb_val):
                                f.write(String)
                    if(Time_File[cpt_file]==2):
                        if(bool(Zones[ID_Zone[cpt_file]]['Coeff_Valve'])):
                            Nb_Coeffs=len(Zones[ID_Zone[cpt_file]]['Coeff_Valve'][i])
                            String=str(Nb_Coeffs)+'\n'
                            f.write(String)
                            for Prop_Value in Zones[ID_Zone[cpt_file]]['Coeff_Valve'][i]:
                                String=Prop_Value+'\n'
                                f.write(String)
                f.close()

        cpt_file+=1
    Test=1

#Sous-routine dédiée à exporter coordonnées des noeuds
def Export_vecr(Nodes,Path):
    Type=['Reservoirs','IncJunctions']
    File=['\\Reservoirs.vecr','\\Extra_data_Junctions.jun']
    cpt_file=0
    for TypeNode in Type:
        Filename=Path+File[cpt_file]
        f = open(Filename, 'w')
        NbElem=len(Nodes[TypeNode])
        String=str(NbElem)+'\n'
        f.write(String)
        for NameNode in Nodes[TypeNode]:
            Coord=Nodes[TypeNode][NameNode]['CoordPlan']
            CoordZ=Nodes[TypeNode][NameNode]['CoordZ']
            String=str(Coord[0])+','+str(Coord[1])+','+str(CoordZ)+','+NameNode+'\n'
            f.write(String)
        f.close()
        cpt_file += 1
    Test=1

#Sous-routine dédiée à exporter les attributs des noeuds utilisés
def Export_Node_Attributes(Nodes,Path):
    #Première étape est la création du sous-dossier réservoirs ou jonctions incompressibles si celui-ci n'existe pas
    Directory=[]
    Directory.append(Path+'\\Reservoirs')
    if(not(os.path.isdir(Directory[0]))):
        try:
            os.mkdir(Directory[0])
        except OSError:
            logging.warning("Creation of the directory %s failed" % Directory[0])
    #On vérifie ensuite en second lieu si jonctions oncompressibles sont présentes dans le réseau
    if(bool(Nodes['IncJunctions'])):
        Directory.append(Path+'\\Extra_data_Junctions')
        if(not(os.path.isdir(Directory[1]))):
            try:
                os.mkdir(Directory[1])
            except OSError:
                logging.warning("Creation of the directory %s failed" % Directory[1])
    #Deuxième étape est donc d'ajouter les différents fichiers d'attributs
    Attributes=[[],[]]
    Type=['Reservoirs','IncJunctions']
    ListFilename=[[],[]]
    Attributes[0]=['SECTION','IC_V','Max_H','Min_H','Patterns']
    ListFilename[0]=['\\SECTION.D','\\IC_Reservoir.D','\\Max_Height.D','\\Minimum_H.D','\\BC_Water_Exchanges.S']
    Attributes[1]=['Patterns','Consumers']
    ListFilename[1]=['\\BC_Water_Exchanges.S','\\ConsMeters.I']
    #On s'assure de la validité
    Attr=Attributes[1][0]
    Dflt_Name='X'
    Filename=Dflt_Name
    for TypeNode in Type:
        for NameNode in Nodes[TypeNode]:
            if(Attr in Nodes[TypeNode][NameNode]):
                if(bool(Nodes[TypeNode][NameNode][Attr])):
                    if(isinstance(Nodes[TypeNode][NameNode][Attr],list)):
                        Nb_El=len(Nodes[TypeNode][NameNode][Attr])
                        for i in range(Nb_El):
                            Name=Nodes[TypeNode][NameNode][Attr][i]
                            List_sbstr=Name.split('.')
                            #Soit on divise le nom ou soit on récupérèe la première partie pour lui ajouter '.exch'
                            Nodes[TypeNode][NameNode][Attr][i]=List_sbstr[0]+'.exch'
                            Name=Nodes[TypeNode][NameNode][Attr][i]
                            Test=1
    Init_Spec_File=[0]
    cpt_node=0
    NbNodes=[len(Nodes['Reservoirs']),len(Nodes['IncJunctions'])]
    Dft_Values={}
    for TypeNode in Type:
            Dft_Values[TypeNode]={}
            Dft_Values[TypeNode]['NbPatterns']='X'
            Dft_Values[TypeNode]['Patterns']='X.exch'
    Dft_Values['IncJunctions']['Consumers']='X'
    for TypeNode in Type:
        cpt_attr=0
        for Attr in Attributes[cpt_node]:
            Existing_Attr=0
            cpt_elem=0
            for NameNode in Nodes[TypeNode]:
                 if(Attr in Nodes[TypeNode][NameNode]):
                     if(Existing_Attr==0):
                         #L'attribut existe au moins pour un élément de la catégorie, on crée le fichier
                         Existing_Attr=1
                         Filename=Directory[cpt_node]+ListFilename[cpt_node][cpt_attr]
                         cpt_attr += 1
                         f = open(Filename, 'w')
                         String=str(NbNodes[cpt_node])+'\n'
                     if(Existing_Attr>0):
                         #On écrit la ligne
                         if(isinstance(Nodes[TypeNode][NameNode][Attr],list)):
                            Nb_El=len(Nodes[TypeNode][NameNode][Attr])
                            cpt_elem+=Nb_El
                            for i in range(Nb_El):
                                Add_Line=True
                                if(Attr in Dft_Values[TypeNode]):
                                    if(str(Nodes[TypeNode][NameNode][Attr][i])==Dft_Values[TypeNode][Attr]):
                                       Add_Line=False
                                if(Add_Line):
                                    if(Existing_Attr==1):
                                        f.write(String)
                                        Existing_Attr+=1
                                    String=NameNode+','+str(Nodes[TypeNode][NameNode][Attr][i])+'\n'
                                    f.write(String)
                         else:
                            Add_Line=True
                            if(Attr in Dft_Values[TypeNode]):
                                if(str(Nodes[TypeNode][NameNode][Attr])==Dft_Values[TypeNode][Attr]):
                                   Add_Line=False
                            if(Add_Line):
                                if(Existing_Attr==1):
                                    f.write(String)
                                    Existing_Attr+=1
                                String=NameNode+','+str(Nodes[TypeNode][NameNode][Attr])+'\n'
                                cpt_elem+=1
                                f.write(String)
            if(Existing_Attr>0):
                f.close()
                if(Existing_Attr>1):
                    #On met en première ligne le nombre de lignes
                    f = open(Filename, 'r')
                    lines=f.readlines()
                    lines[0]=str(cpt_elem)+'\n'
                    f.close()
                    f = open(Filename, 'w')
                    f.writelines(lines)
                    f.close()
        cpt_node += 1
    #Fichier de valeurs à chaque pas de temps à également sauvegarder
    local_file=['\\CHR_FIRST_VAL.d','\\CHR_FIRST_VAL.d']
    Dft_Value={}
    Dft_Value['Reservoirs']='0.0'
    Dft_Value['IncJunctions']='0.0'
    cpt_node=0
    Attr='ValueH'
    Valid_File={}
    Valid_File['Reservoirs']=False
    Valid_File['IncJunctions']=False
    #Première analyse afin d'identifier si des résultats sont en réalité pertinents pour l'exportation
    for TypeNode in Type:
        for NameNode in Nodes[TypeNode]:
            if (Attr in Nodes[TypeNode][NameNode]):
                for Loc_Val in Nodes[TypeNode][NameNode][Attr]:
                    if(Loc_Val!=Dft_Value[TypeNode]):
                        Valid_File[TypeNode]=True
                        break
            if(Valid_File[TypeNode]):
                break

    for TypeNode in Type:
        Filename=Directory[cpt_node]+local_file[cpt_node]
        Existing_Attr=False
        if(Valid_File[TypeNode]):
            for NameNode in Nodes[TypeNode]:
                if (Attr in Nodes[TypeNode][NameNode]):
                    if(not(Existing_Attr)):
                        f = open(Filename, 'w')
                        String=str(NbNodes[cpt_node])+'\n'
                        f.write(String)
                        Existing_Attr=True
                    if(Existing_Attr):
                        String=NameNode+'\n'
                        f.write(String)
                        for Loc_Val in Nodes[TypeNode][NameNode][Attr]:
                            String=str(Loc_Val)+'\n'
                            f.write(String)
        cpt_node +=1
        if(Existing_Attr):
            f.close()

#Sous-routine visant à exporter les paramètres généraux du réseau en respectant le format donné
def General_Parameters(Params,Path):
    Test=1
    if(bool(Params)):
        Filename=Path+'\\General_Network.param'
        f = open(Filename, 'w')
        for Elems in Params:
            String=Elems+' '+':'+'\n'
            f.write(String)
            for SubElem in Params[Elems]:
                #Décomposition en premiers éléments eux même avec deux arguments
                String=SubElem+'\t'+Params[Elems][SubElem][0]+'\t'+Params[Elems][SubElem][1]+'\n'
                f.write(String)
        f.close()
        T=1

#Sous-routine visant à exporter les patterns utilisés
def Export_Patterns(Patterns,Path):
    Directory=Path+'\\Patterns'
    AttrFilename=['\\Interpol_exchange.I','\\Exchange_var.I']
    AttrPattern='\\Patterns_'
    InitPattern='Patterns_'
    ExtPattern='.prrn'
    f=[0,0,0]
    if(not(os.path.isdir(Directory))):
        try:
            os.mkdir(Directory)
        except OSError:
            logging.warning("Creation of the directory %s failed" % Directory)
    if(bool(Patterns)):
        cpt_Pattern=0
        for Pattern in Patterns:
            #Partie fichiers d'attributs
            if(cpt_Pattern==0):
                cpt_file=0
                for Attr in AttrFilename:
                    Filename=Directory+Attr
                    f[cpt_file] = open(Filename, 'a')
                    f[cpt_file].truncate(0)
                    cpt_file += 1
                cpt_Pattern+=1
            String=Pattern+','+Patterns[Pattern]['Meth_Interp']+'\n'
            f[0].write(String)
            String=Pattern+','+Patterns[Pattern]['Exch_Opt']+'\n'
            f[1].write(String)
            Test=1
        f[0].close()
        f[1].close()
    #On va cette fois s'intéresser aux patterns afin de réaliser un dossier par pattern
    for Pattern in Patterns:
        Filename=Directory+'\\'+Pattern+','+'0'

        if(not(os.path.isdir(Filename))):
            try:
                os.mkdir(Filename)
            except OSError:
                logging.warning("Creation of the directory %s failed" % Directory)
        Values=Patterns[Pattern]['Values']
        NbVal=len(Values[0])
        Loc_File=Filename+'\\Calendar.I'
        f[0] = open(Loc_File, 'w')
        Nb_Day='1'
        Loc_File=Filename+AttrPattern+Nb_Day+ExtPattern
        Crit_Value=86400
        f[1] = open(Loc_File, 'w')

        #Pattern link exportation
        Loc_File=Filename+'\\Prtn_Link.I'
        f[2] = open(Loc_File, 'w')

        #Première lecture pour connaître le nombre d'entrées par journées
        Cpt_entries=0
        Nb_entries=[]
        for TimeVal in Values[0]:
            TimeVal=float(TimeVal)
            if(TimeVal>Crit_Value):
                Nb_entries.append(Cpt_entries)
                Cpt_entries=1
                Crit_Value=Crit_Value+86400
            else:
                Cpt_entries+=1
        Nb_entries.append(Cpt_entries)
        String=str(Nb_entries[0])+'\n'
        Crit_Value=86400
        cpt_link=1
        Loc_String=InitPattern+Nb_Day+ExtPattern
        String_Link=str(cpt_link)+','+Loc_String+'\n'
        Daily=Nb_Day+'\n'
        f[0].write(Daily)
        f[2].write(String_Link)
        f[1].write(String)
        #On ajoute cette fois les valeurs des échanges
        for Ind in range(NbVal):
            TimeVal=float((Values[0][Ind]))
            if(TimeVal>Crit_Value):
                f[1].close()
                Nb_Day=str(int(Nb_Day)+1)
                cpt_link+=1
                Loc_File=Filename+AttrPattern+Nb_Day+ExtPattern
                Loc_String=InitPattern+Nb_Day+ExtPattern
                String_Link=str(cpt_link)+','+Loc_String+'\n'
                Daily=Nb_Day+'\n'
                f[0].write(Daily)
                f[2].write(String_Link)
                f[1] = open(Loc_File, 'w')
                String=str(Nb_entries[int(Nb_Day)-1])+'\n'
                f[1].write(String)
                Crit_Value=Crit_Value+86400
            if(len(Values)==2):
                String=Values[0][Ind]+'\t'+Values[1][Ind]+'\n'
            if(len(Values)==3):
                String=Values[0][Ind]+'\t'+Values[1][Ind]+'\t'+Values[2][Ind]+'\n'
            f[1].write(String)
        f[0].close()
        f[1].close()
        f[2].close()
        Test=1
    Test=1

if __name__=='__main__':
    app = wx.App()
    ex = Bernoulli_Frame(None)
    ex.Show()
    app.MainLoop()
