from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
import pandas as pd
from os.path import join,exists
from os import mkdir
# from osgeo import ogr
# from osgeo import osr
import json
import numpy as np
from enum import Enum
from typing import Literal
import urllib.parse

import matplotlib.pyplot as plt

"""
KIWIS WebServices command :
    getrequestinfo retrieves all available commands

    getGroupList	retrieves a list of object groups
    getSiteList	retrieves a list of sites with metadata
    getStationList	retrieves a list of stations with metadata
    getParameterList	retrieves a list of parameters available at sites and/or stations
    getParameterTypeList	retrieves the system defined parameter type list
    getCatchmentList	retrieves a list of catchments with metadata
    getCatchmentHierarchy	retrieves a hierarchical list of catchments with metadata and parent catchments
    getRiverList	retrieves a list of rivers and water objects with metadata
    getStandardRemarkTypeList	retrieves a hierarchical list of standard remark types
    getRatingCurveList	retrieves a list of rating curves
    getTimeseriesList	retrieves a list of timeseries with metadata
    getTimeseriesTypeList	retrieves a timeseries type list
    getTimeseriesValues	retrieves timeseries data
    getTimeseriesValueLayer	retrieves timeseries data as layer
    getGraphTemplateList	retrieves a list of available graph templates
    getGraph	retrieves a graph image of timeseries data
    getStationGraph	retrieves a graph image of timeseries data based on stations
    getColorClassifications	retrieves a list of WISKI color classifications
    getQualityCodes	retrieves the list of WISKI quality codes
    getReleaseStateClasses	retrieves the list of WISKI release state classes
    getTimeseriesReleaseStateList	retrieves a list of timeseries release states
    getTimeseriesEnsembleValues	retrieves a list of timeseries ensembles with values for one or more timeseries
    getTimeseriesChanges	retrieves a list of changes for a timeseries
    getTimeseriesComments	retrieves object comments/remarks
    checkValueLimit	checks value limitations for time range value requests
"""

URL_SERVICE = 'https://hydrometrie.wallonie.be/services'
URL_SPW   = URL_SERVICE + '/KiWIS/KiWIS'
URL_TOKEN = URL_SERVICE + '/auth/token/'

class kiwis_command(Enum):
    getrequestinfo = "getrequestinfo"
    getGroupList = "getGroupList"
    getSiteList = "getSiteList"
    getStationList = "getStationList"
    getParameterList = "getParameterList"
    getParameterTypeList = "getParameterTypeList"
    getCatchmentList = "getCatchmentList"
    getCatchmentHierarchy = "getCatchmentHierarchy"
    getRiverList = "getRiverList"
    getStandardRemarkTypeList = "getStandardRemarkTypeList"
    getRatingCurveList = "getRatingCurveList"
    getTimeseriesList = "getTimeseriesList"
    getTimeseriesTypeList = "getTimeseriesTypeList"
    getTimeseriesValues = "getTimeseriesValues"
    getTimeseriesValueLayer = "getTimeseriesValueLayer"
    getGraphTemplateList = "getGraphTemplateList"
    getGraph = "getGraph"
    getStationGraph = "getStationGraph"
    getColorClassifications = "getColorClassifications"
    getQualityCodes = "getQualityCodes"
    getReleaseStateClasses = "getReleaseStateClasses"
    getTimeseriesReleaseStateList = "getTimeseriesReleaseStateList"
    getTimeseriesEnsembleValues = "getTimeseriesEnsembleValues"
    getTimeseriesChanges = "getTimeseriesChanges"
    getTimeseriesComments = "getTimeseriesComments"
    checkValueLimit = "checkValueLimit"

class kiwis_request_info(Enum):
    Request = "Request"
    Description = "Description"
    QueryFields = "QueryFields"
    Formats = "Formats"
    Returnfields = "Returnfields"
    OptionalFields = "Optionalfields"

class kiwis_token(Enum):
    ACCESS_TOKEN_KEY = 'access_token'
    TOKEN_TYPE = 'token_type'
    EXPIRES_IN = 'expires_in'

class kiwis_maintainers(Enum):
    DGH = 'DGH'
    DCENN = 'DCENN'
    EUPEN = 'EUP'

class kiwis_site_fields(Enum):
    site_no = 'site_no'
    site_name = 'site_name'
    site_id = 'site_id'

KIWIS_GROUP_TS = {'rain': \
                    {'5min': {'name': 'DGH-TS-Export-Pluie5min', 'id': 1332286 }, \
                    '1h': {'name': 'DGH-TS-Export-PluieHoraire', 'id': 5716546 }, \
                    '1d': {'name': 'DGH-TS-Export-PluieJourn', 'id': 5728245 }, \
                    '1m': {'name': 'DGH-TS-Export-PluieMensuelle', 'id': 7254396 }}, \
               'flowrate': \
                    {'5or10min': {'name': 'SPW-WS-DebitHR', 'id': 7256917 }, \
                    '1h': {'name': 'SPW-WS-DebitHoraire', 'id': 7256918 }, \
                    '1d': {'name': 'SPW-WS-DebitJourn', 'id': 7256919 }, \
                    '1m': {'name': 'SPW-WS-DebitMensuel', 'id': 7256920 }}, \
               'waterdepth': \
                    {'5or10min': {'name': 'SPW-WS-HauteurHR', 'id': 7255523 }, \
                    '1h': {'name': 'SPW-WS-HauteurHoraire', 'id': 7255522 }, \
                    '1d': {'name': 'SPW-WS-HauteurJourn', 'id': 7255151 }, \
                    '1m': {'name': 'SPW-WS-HauteurMensuelle', 'id': 7255524 }} \
                }

class kiwis_keywords_horq(Enum):
    V5_10MIN    = 'complet'
    V1H         = '1h.moyen'
    VDAY        = 'jour.moyen'
    VMONTH      = 'mois.moyen'
    VMAXAN      = 'an.maximum'
    VMAXANHYD   = 'anHydro.maximum'
    VMINANHYD   = 'anHydro.minimum'
class kiwis_keywords_rain(Enum):
    V5_10MIN    = 'production'
    V1H         = '1h.total'
    VDAY        = 'jour.total'
    VMONTH      = 'mois.total'
    VMAXAN      = 'an.maximum'
    VMAXANHYD   = 'anHydro.maximum'
    VMINANHYD   = 'AnHydro.minimum'

class kiwis_default_q(Enum):
    Q_FULL      = '05-Debit.Complet'
    Q_1H        = '10-Debit.1h.Moyen'
    Q_1H_Ultra  = '10-Debit ultrason.1h.Moyen'

class kiwis_default_h(Enum):
    H_FULL      = '05-Hauteur.Complet'
    H_1H        = '10-Hauteur.1h.Moyen'
    H_1J        = '20-Hauteur.Jour.Moyen'
    Z_1H        = '10-Hauteur_absolue.1h.Moyen'

"""
Code qualité    Validation  Qualité
40              Oui         Mesure ou calcul de qualité standard
80              Oui         Données estimées / corrigées : données fausses ou
                            manquantes qui ont pu être corrigées ou complétées de
                            manière satisfaisante.
120             Oui         Données estimées / corrigées : données fausses ou
                            manquantes qui ont été corrigées ou complétées mais
                            restent suspectes ou de faible qualité.
160             Oui         Données suspectes ou de faible qualité mais non modifiées.
200             Non         Données brutes
205/210         Non         Données de qualité suspecte (contrôle automatique) ou en
                            cours d'analyse à à ne pas utiliser
255 / -1 -                  Données manquantes
"""
class quality_code(Enum):
    # Validated
    STANDARD        = (40, 'blue', '')
    ESTIMATED_OK    = (80, 'green', '+')
    ESTIMATED_DOUBT = (120, 'orange', '>')
    # Not validated
    DOUBT           = (160, 'orange', '*')
    RAW             = (200, 'gray', '.')
    BAD             = (205, 'red', 'o')
    BAD2            = (210, 'red', 'x')
    VOID            = (255, 'black', '.')
    VOID2           = (-1, 'black', '.')
class hydrometry():

    def __init__(self, url:str='', urltoken:str='', credential ='', dir='') -> None:
        """Initialisation sur base d'un URL de service KIWIS
        et recherche des sites et stations disponibles
        """
        self.url = url
        self.urltoken = urltoken
        self.dir = dir
        self.credential = credential

        self.groups = None
        self.stations = None
        self.sites = None
        self.requests = None

        self.idx = 'hydrometry'
        self.plotted = False

        if url=='':
            self.url=URL_SPW

        if urltoken=='':
            self.urltoken=URL_TOKEN

        try:
            self.daily_token()
            self.get_requests()
            self.get_sites()
            self.get_stations()
            self.get_groups()
            self.save_struct(self.dir)
        except:
            pass

    def _get_commandstr(self, which:str):
        return self.url+'?request='+which.value+'&format=json'

    def daily_token(self):
        """
        Get daily token to be identified on hydrometry website

        @todo : manage error as response
        """
        if self.credential == '':
            self._header = None
            return

        today = 'token_'+datetime.now().strftime('%Y%m%d')+'.json'

        if exists(today):
            with open(today, 'r') as f:
                self.token = json.load(f)
        else:
            headers = {'Authorization' : 'Basic {}'.format(self.credential)}
            data = {'grant_type' :'client_credentials'}
            self.token = requests.post(self.urltoken, data=data, headers=headers).json()
            with open(today, 'w') as f:
                json.dump(self.token, f)

        self._header = {'Authorization': 'Bearer {}'.format(self.token['access_token'])}

    def check_plot(self):
        self.plotted = True

    def uncheck_plot(self):
        self.plotted = False

    def save_struct(self,dir=''):

        if dir=='':
            return

        self.sites.to_csv(join(dir,'sites.csv'))
        self.stations.to_csv(join(dir,'stations.csv'))
        self.groups.to_csv(join(dir,'groups.csv'))
        self.requests.to_csv(join(dir,'requests.csv'))

    def _get_stations_pythonlist(self, site_no, onlyreal=True):

        if onlyreal:
            stations = self.realstations[self.realstations['site_no']==site_no]
        else:
            stations = self.stations[self.stations['site_no']==site_no]

        list_name_code = [curname+' --- '+curno   for curname,curno in zip(stations['station_name'].values,stations['station_no'].values)]
        list_code_name = [curno  +' --- '+curname for curname,curno in zip(stations['station_name'].values,stations['station_no'].values)]

        return list_name_code, list_code_name

    def _get_sites_pythonlist(self):

        list_name_code = [curname+' --- '+curno  for curname,curno in zip(self.sites['site_name'].values,self.sites['site_no'].values)]
        return list_name_code

    def get_stations(self):
        """Obtention des stations pour le serveur courant"""

        """
        site_no : numéro du site ; le site correspond au réseau de mesure : DGH pour les stations du SPW-MI et DCENN pour les stations du SPW-ARNE ;
        station_no, station_name : code et nom de la station ;
        station_local_x, station_local_y : coordonnées de la station en Lambert belge 1972 ;
        station_latitude,station_longitude : coordonnées de la station en ETRS89 ;
        river_name : nom de la rivière, cette information n’est disponible que pour les stations de mesure de hauteur d’eau et de débits, les pluviomètres ne sont pas installés sur une rivière – il n’y a donc pas de nom de rivière associé ;
        parametertype_name : type de paramètre ;
        ts_id, ts_name : code et nom de la chronique ;
        ts_unitname, ts_unitsymbol : nom et symbole de l’unité de mesure ;
        ca_sta&ca_sta_returnfields=BV_DCE : nom du bassin versant principal suivi de son abréviation (2 lettres)
        """

        returnfields = 'site_no,'
        returnfields += 'station_no,station_name,station_id,'
        returnfields += 'station_local_x,station_local_y,'
        returnfields += 'station_latitude,station_longitude,'
        returnfields += 'river_name,'
        returnfields += 'ca_sta'

        ca_sta_returnfields = 'station_gauge_datum,'
        ca_sta_returnfields += 'CATCHMENT_SIZE,'
        ca_sta_returnfields += 'BV_DCE'
        # returnfields += 'parametertype_name,'
        # returnfields += 'ts_id,ts_name,'
        # returnfields += 'ts_unitname,ts_unitsymbol,'

        if self.dir!='' and exists(join(self.dir,'stations.csv')):
            self.stations = pd.read_csv(join(self.dir,'stations.csv'),index_col=0)
        elif self.url!='':
            json_data = requests.get(self._get_commandstr(kiwis_command.getStationList) \
                                     +'&metadata=true' \
                                     +'&returnfields='+returnfields \
                                     +'&ca_sta_returnfields='+ca_sta_returnfields \
                                     +'&orderby=station_no', \
                                     verify=True, \
                                     headers=self._header).json()
            self.stations = pd.DataFrame(json_data[1:], columns = json_data[0])

        #Conversion en minuscules
        self.stations['station_name']=self.stations['station_name'].str.lower()

        self.realstations = self.stations[(~pd.isnull(self.stations['station_local_x'])) & (self.stations['station_local_x']!='')]
        self.compstations = self.stations[pd.isnull(self.stations['station_local_x']) | self.stations['station_local_x']!='']

    def select_inside(self, xll:float, yll:float, xur:float, yur:float, tolist=False):
        """
        Recherche les stations dans une zone rectangulaire

        xll, yll : lower left
        xur, yur : upper right
        """

        if xll>xur:
            tmpx=xll
            xll=xur
            xur=tmpx
        if yll>yur:
            tmpy=yll
            yll=yur
            yur=tmpy

        df = self.realstations[(self.realstations['station_local_x'].to_numpy(dtype=np.float64)>=xll) & (self.realstations['station_local_x'].to_numpy(dtype=np.float64)<=xur) & (self.realstations['station_local_y'].to_numpy(dtype=np.float64)>=yll) & (self.realstations['station_local_y'].to_numpy(dtype=np.float64)<=yur)]
        if tolist:
            list_name_code = [curname+' --- '+curno  for curname,curno in zip(df['station_name'].values,df['station_no'].values)]
            return list_name_code
        else:
            return df

    def sort_nearests(self,x:float,y:float):
        """
        Trie les stations en fonction de la distance et retourne un index trié
        """
        dist = np.asarray([(float(cur['station_local_x']) - x)**2 + (float(cur['station_local_y']) - y)**2 for idx,cur in self.realstations.iterrows()])
        index = np.arange(len(dist))[dist.argsort()]

        return index

    def find_nearest(self,x:float,y:float, tolist=False):
        """
        Trouve la station la plus proche
        """
        index = self.sort_nearests(x,y)

        if tolist:
            return [self.realstations.iloc[index[0]]['station_name']+' --- '+self.realstations.iloc[index[0]]['station_no']]
        else:
            return self.realstations.iloc[index[0]]

    def get_timeseries_group(self, rfw:Literal['rain','waterdepth','flowrate'], time:Literal['5min','5or10min','1h','1d','1m']):
        """Obtention des stations pour le groupe souhaité"""

        if self.url!='':
            stations=None
            if rfw in KIWIS_GROUP_TS.keys():
                if time in KIWIS_GROUP_TS[rfw].keys():
                    group_id = KIWIS_GROUP_TS[rfw][time]['id']
                    json_data = requests.get(self._get_commandstr(kiwis_command.getTimeseriesList) +'&timeseriesgroup_id='+str(group_id)+'&orderby=station_no', verify=True, headers=self._header).json()
                    stations = pd.DataFrame(json_data[1:], columns = json_data[0])

            return stations

    def get_sites(self):
        """Obtention des sites pour le serveur courant"""
        if self.dir!='' and exists(join(self.dir,'sites.csv')):
            self.sites = pd.read_csv(join(self.dir,'sites.csv'),index_col=0)
        elif self.url!='':
            json_data = requests.get(self._get_commandstr(kiwis_command.getSiteList),verify=True, headers=self._header).json()
            self.sites = pd.DataFrame(json_data[1:], columns = json_data[0])

    def get_groups(self):
        """Obtention des groupes pour le serveur courant"""
        if self.dir!='' and exists(join(self.dir,'groups.csv')):
            self.groups = pd.read_csv(join(self.dir,'groups.csv'),index_col=0)
        elif self.url!='':
            json_data = requests.get(self._get_commandstr(kiwis_command.getGroupList),verify=True, headers=self._header).json()
            self.groups = pd.DataFrame(json_data[1:], columns = json_data[0])

    # def get_ratingcurves(self):
    #     """Obtention des courbes de tarage pour le serveur courant"""
    #     if self.dir!='':
    #         self.ratingcurves = pd.read_csv(join(self.dir,'ratingcurves.csv'),index_col=0)
    #     elif self.url!='':
    #         json_data = requests.get(self.url+'?request=getRatingCurveList&datasource=0&format=json',verify=True).json()
    #         self.ratingcurves = pd.DataFrame(json_data[1:], columns = json_data[0])

    def get_requests(self):
        """Obtention des requêtes possibles pour le serveur courant"""
        if self.dir!='' and exists(join(self.dir,'requests.csv')):
            self.requests = pd.read_csv(join(self.dir,'requests.csv'),index_col=0)
        elif self.url!='':
            json_data = requests.get(self._get_commandstr(kiwis_command.getrequestinfo),verify=True, headers=self._header).json()
            self.requests = pd.DataFrame(json_data[0]['Requests'])

    def print_requestinfo(self,which:Enum):
        if self.requests is None:
            self.get_requests()

        if which.value in self.requests.keys():
            myrequest = self.requests[which.value]

            for cur in kiwis_request_info:
                print(myrequest[cur.value])

    def timeseries_list(self,stationname='',stationcode=''):
        """Récupération de la liste des TimeSeries pour l'id d'une station"""

        if stationname!='':
            id=self.get_stationid(stationname)
        elif stationcode!='':
            id=self.get_stationid(code=stationcode)

        json_data = requests.get(self._get_commandstr(kiwis_command.getTimeseriesList)
                                 +'&station_id='+str(id)
                                 +'&format=json'
                                 ,verify=True, headers=self._header).json()

        return id,pd.DataFrame(json_data[1:], columns = json_data[0])

    def save_all_lists(self,dir):
        """Sauveragde des listes pour toutes les stations"""
        for curstation in self.stations['station_no']:
            self.save_list(stationcode=curstation,dir=dir)

    def _get_filename_list(self,stationname='',stationcode=''):
        """retourne un nom de fichier avec la station et le code

        Utile car dans certains noms de la BDD KIWIS il y a un caractère '/' qui ne peut être utilisé comme nom de fichier
        Il est remplacé par '-'
        """
        if stationname=='':
            stationname = self.get_stationname(stationcode)

        if stationcode=='':
            stationcode = self.get_stationcode(stationname)

        id = self.get_stationid(stationname,stationcode)

        return stationname.replace('/','-') + '_' + stationcode + '_' + str(id) + '.csv'

    def _get_filename_series(self,stationname='',stationcode='',which:Enum=kiwis_default_q.Q_FULL):
        """retourne un nom de fichier avec la station et le code et le type de données

        Utile car dans certains noms de la BDD KIWIS il y a un caractère '/' qui ne peut être utilisé comme nom de fichier
        Il est remplacé par '-'
        """
        if stationname=='':
            stationname = self.get_stationname(stationcode)

        if stationcode=='':
            stationcode = self.get_stationcode(stationname)

        id = self.get_stationid(stationname,stationcode)

        return stationname.replace('/','-') + '_' + stationcode + '_' + str(id) + '_' + which.value + '.csv'

    def save_list(self,stationname='',stationcode='',dir=''):
        """Sauvegarde de la liste des des timeseries dans un fichier"""
        if not exists(dir):
            mkdir(dir)

        id,list=self.timeseries_list(stationname=stationname,stationcode=stationcode)
        filename = self._get_filename_list(stationname,stationcode)
        list.to_csv(join(dir,filename))

    def timeseries(self,stationname='', stationcode='', dir='', fromdate=datetime.now()-timedelta(60), todate=datetime.now(), ts_name:str='', ts_id:str='', interval=3600, timezone = 'GMT+0'):
        """
        Récupération des valeurs d'une TimeSerie
          - sur base des dates
          - soit en donnant :
            - le nom de la station ou le code ET le nom de la timeserie --> dans ce cas, la routine commence par retrouver l'id de la ts
            - directement l'id de la timeserie

        """

        if timezone=='Europe/Brussels' or timezone=='local':
            timezone=''

        nb = (todate - fromdate).days*24 * (3600/interval)
        cursec = interval
        # id = ''
        if ts_id == '':
            if stationname=='':
                stationname = self.get_stationname(stationcode)
            if stationcode=='':
                stationcode = self.get_stationcode(stationname)
            id = self.get_stationid(stationname,stationcode)

            if dir=='':
                json_data = requests.get(self._get_commandstr(kiwis_command.getTimeseriesList)
                                        +"&"+urllib.parse.urlencode({
                                        "station_id":str(id),
                                        "ts_name":ts_name,
                                        "timezone":timezone})
                                        ,verify=True).json()
                if len(json_data)==1:
                    return None

                ts_id = str(int(pd.DataFrame(json_data[1:], columns = json_data[0])['ts_id'].iloc[0]))
            else:
                filename = self._get_filename_list(stationname,stationcode)
                curlist=pd.read_csv(join(dir,filename),index_col=0)
                ts_id = str(int(curlist.loc(curlist['ts_name'==ts_name])['ts_id']))

            if "1h" in ts_name:
                nb = (todate - fromdate).days*24
                cursec = 3600
            elif "5min" in ts_name:
                nb = (todate - fromdate).days*24*12
                cursec = 300
            elif "10min" in ts_name:
                nb = (todate - fromdate).days*24*6
                cursec = 600
            elif "2min" in ts_name:
                nb = (todate - fromdate).days*24*30
                cursec = 120
            elif "jour" in ts_name:
                nb = (todate - fromdate).days*24
                cursec = 24*3600
            elif "mois" in ts_name:
                nb = (todate - fromdate).days/30
                cursec = 24*30*3600

        if nb>250000:
            curfrom = fromdate
            curend = curfrom+timedelta(seconds=200000 * cursec)
            locts=[]
            while curfrom<todate:
                print(curfrom, curend)
                locts.append(self.timeseries(stationname, stationcode, dir, curfrom, curend, ts_name, ts_id, timezone=timezone))
                curfrom = curend
                curend = curfrom+timedelta(seconds=200000 * cursec)
                if curend>todate:
                    curend=todate

            return pd.concat(locts)
        else:
            json_data = requests.get(self._get_commandstr(kiwis_command.getTimeseriesValues)
                                    +"&"+urllib.parse.urlencode({
                                    "ts_id":str(ts_id),
                                    "from":fromdate.strftime("%Y-%m-%dT%H:%M:%S"),
                                    "to":todate.strftime("%Y-%m-%dT%H:%M:%S"),
                                    # "format":"json",
                                    "timezone":timezone})
                                    ,verify=True, headers=self._header).json()

            df = pd.DataFrame(json_data[0]['data'], columns = json_data[0]['columns'].split(','))
            df.set_index('Timestamp', inplace = True)
            df.index = pd.to_datetime(df.index,format="%Y-%m-%dT%H:%M:%S.%f%z")

        return df.squeeze()

    def timeseries_qc(self,stationname='', stationcode='', dir='', fromdate=datetime.now()-timedelta(60), todate=datetime.now(), ts_name:str='', ts_id:str='', interval=3600, timezone = 'GMT+0'):
        """
        Récupération des quality code d'une TimeSerie
          - sur base des dates
          - soit en donnant :
            - le nom de la station ou le code ET le nom de la timeserie --> dans ce cas, la routine commence par retrouver l'id de la ts
            - directement l'id de la timeserie

        """
        if timezone=='Europe/Brussels' or timezone=='local':
            timezone=''

        nb = (todate - fromdate).days*24 * (3600/interval)
        cursec = interval
        # id = ''
        if ts_id == '':
            if stationname=='':
                stationname = self.get_stationname(stationcode)
            if stationcode=='':
                stationcode = self.get_stationcode(stationname)
            id = self.get_stationid(stationname,stationcode)

            if dir=='':
                json_data = requests.get(self._get_commandstr(kiwis_command.getTimeseriesList)
                                        +"&"+urllib.parse.urlencode({
                                        "station_id":str(id),
                                        "ts_name":ts_name,
                                        "timezone":timezone})+
                                        "&returnfields=Timestamp,Quality%20Code"
                                        ,verify=True).json()
                if len(json_data)==1:
                    return None

                ts_id = str(int(pd.DataFrame(json_data[1:], columns = json_data[0])['ts_id'].iloc[0]))
            else:
                filename = self._get_filename_list(stationname,stationcode)
                curlist=pd.read_csv(join(dir,filename),index_col=0)
                ts_id = str(int(curlist.loc(curlist['ts_name'==ts_name])['ts_id']))

            if "1h" in ts_name:
                nb = (todate - fromdate).days*24
                cursec = 3600
            elif "5min" in ts_name:
                nb = (todate - fromdate).days*24*12
                cursec = 300
            elif "10min" in ts_name:
                nb = (todate - fromdate).days*24*6
                cursec = 600
            elif "2min" in ts_name:
                nb = (todate - fromdate).days*24*30
                cursec = 120
            elif "jour" in ts_name:
                nb = (todate - fromdate).days*24
                cursec = 24*3600
            elif "mois" in ts_name:
                nb = (todate - fromdate).days/30
                cursec = 24*30*3600

        if nb>250000:
            curfrom = fromdate
            curend = curfrom+timedelta(seconds=200000 * cursec)
            locts=[]
            while curfrom<todate:
                print(curfrom, curend)
                locts.append(self.timeseries(stationname,stationcode,dir,curfrom,curend,ts_name,ts_id))
                curfrom = curend
                curend = curfrom+timedelta(seconds=200000 * cursec)
                if curend>todate:
                    curend=todate

            return pd.concat(locts)
        else:
            json_data = requests.get(self._get_commandstr(kiwis_command.getTimeseriesValues)
                                    +"&"+urllib.parse.urlencode({
                                    "ts_id":str(ts_id),
                                    "from":fromdate.strftime("%Y-%m-%dT%H:%M:%S"),
                                    "to":todate.strftime("%Y-%m-%dT%H:%M:%S"),
                                    "timezone":timezone})+
                                    "&returnfields=Timestamp,Quality%20Code"
                                    ,verify=True, headers=self._header).json()

            df = pd.DataFrame(json_data[0]['data'], columns = json_data[0]['columns'].split(','))
            df.set_index('Timestamp', inplace = True)
            df.index = pd.to_datetime(df.index,format="%Y-%m-%dT%H:%M:%S.%f%z")

        return df.squeeze()

    def fromcsv(self,dir='spw',stationname='',stationcode='',which:Enum=kiwis_default_q.Q_FULL,fromdate:datetime=None,todate:datetime=None):
        """
        Lecture depuis un fichier csv créé depuis un import précédent
        Les fichiers doivent être disponibles depuis un sous-répertoire spw
        """
        filename=filename=self._get_filename_series(stationname,stationcode,which)

        if exists(filename):
            mydata= pd.read_csv(filename,header=0,index_col=0,parse_dates=True,engine='pyarrow').squeeze("columns")
        else:
            return

        if fromdate is None and todate is None:
            return mydata
        elif fromdate is None:
            return mydata[:todate]
        elif todate is None:
            return mydata[fromdate:]
        else:
            return mydata[fromdate:todate]

    def saveas(self,flow:pd.Series,dir:str,stationname='',stationcode='',which:Enum=kiwis_default_q.Q_FULL):
        """Sauvegarde d'une series pandas dans un fichier .csv"""
        filename=self._get_filename_series(stationname,stationcode,which.value)
        flow.to_csv(filename,header=['Data'], date_format="%Y-%m-%dT%H:%M:%S.%f%z")

    def get_stationid(self,name:str='',code=''):
        """Récupération de l'id sur base du nom ou du code"""
        if name!='':
            return int(self.stations.loc[self.stations['station_name']==name.lower()]['station_id'].iloc[0])
        elif code!='':
            return int(self.stations.loc[self.stations['station_no']==code]['station_id'].iloc[0])
        else:
            return None

    def get_gauge_datum(self,name:str='',code=''):
        """Récupération de l'altitude de référence sur base du nom ou du code"""
        try:
            if name!='':
                return self.stations.loc[self.stations['station_name']==name.lower()]['station_gauge_datum'].iloc[0]
            elif code!='':
                return self.stations.loc[self.stations['station_no']==code]['station_gauge_datum'].iloc[0]
            else:
                return None
        except:
            return None

    def get_catchment_size(self,name:str='',code=''):
        """Récupération de la surface du BV de référence sur base du nom ou du code"""
        try:
            if name!='':
                return self.stations.loc[self.stations['station_name']==name.lower()]['CATCHMENT_SIZE'].iloc[0]
            elif code!='':
                return self.stations.loc[self.stations['station_no']==code]['CATCHMENT_SIZE'].iloc[0]
            else:
                return None
        except:
            return None

    def get_bv_dce(self,name:str='',code=''):
        """Récupération du nom de BV au sens de la DCE "Directive Cadre Eau" sur base du nom ou du code"""
        try:
            if name!='':
                return self.stations.loc[self.stations['station_name']==name.lower()]['BV_DCE'].iloc[0]
            elif code!='':
                return self.stations.loc[self.stations['station_no']==code]['BV_DCE'].iloc[0]
            else:
                return None
        except:
            return None

    def get_stationcode(self,name:str=''):
        """Récupération du code sur base du nom"""
        if name!='':
            return self.stations.loc[self.stations['station_name']==name.lower()]['station_no'].squeeze()
        else:
            return None

    def get_stationname(self,code:str=''):
        """Récupération du nom sur base du code"""
        if code!='':
            return self.stations.loc[self.stations['station_no']==code]['station_name'].squeeze()
        else:
            return None

    def get_siteid(self,name:str='',code=''):
        """Récupération de l'id sur base du nom ou du code"""
        if name!='':
            return int(self.sites.loc[self.sites[kiwis_site_fields.site_name.value]==name.lower()]['site_id'])
        elif code!='':
            return int(self.sites.loc[self.sites[kiwis_site_fields.site_no.value]==code]['site_id'])
        else:
            return None

    def get_sitecode(self,name:str=''):
        """Récupération du code sur base du nom"""
        if name!='':
            return self.sites.loc[self.sites[kiwis_site_fields.site_name.value]==name.lower()][kiwis_site_fields.site_no.value].squeeze()
        else:
            return None

    def get_sitename(self,code:str=''):
        """Récupération du nom sur base du code"""
        if code!='':
            return self.sites.loc[self.sites[kiwis_site_fields.site_no.value]==code][kiwis_site_fields.site_name.value].squeeze()
        else:
            return None
