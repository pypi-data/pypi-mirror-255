from tb_device_mqtt import TBDeviceMqttClient
from time import sleep
import paho.mqtt.client as mqtt
import time
import requests
import time
import pandas as pd
from datetime import datetime
from datetime import timedelta
from datetime import date
# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
from tb_rest_client.rest import ApiException

try:
    from ..libs import wolfpy
except:
    msg=_('Error importing wolfpy.pyd')
    msg+=_('   Python version : ' + sys.version)
    msg+=_('   If your Python version is not 3.7.x or 3.9.x, you need to compile an adapted library with compile_wcython.py in wolfhece library path')
    msg+=_('   See comments in compile_wcython.py or launch *python compile_wcython.py build_ext --inplace* in :')
    msg+='      ' + dirname(__file__)
    
    raise Exception(msg)


#Global variables
topic = "v1/devices/me/telemetry"
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
#url = 'http://iot4h2o.mv.uni-kl.de:8080/api/auth/login'
url = 'http://iot4h2o.mv.uni-kl.de:8080'
broker = 'iot4h2o.mv.uni-kl.de'
#logging.basicConfig(level=logging.DEBUG)

def callback(client, result):
    print(client, result)
    Test=1
def on_publish(client, userdata, result):
    # log.debug("Data published to ThingsBoard!")
    client.request_attributes(["sensorModel", "attribute_2"], callback=on_attributes_change)
    v=1
    pass
def on_attributes_change(client, result, exception):
    client.stop()
    sleep(3)
    if exception is not None:
        print("Exception: " + str(exception))
    else:
        print(result)
#function for getting the token for the curl-command
def getCurlToken():
    url = 'http://iot4h2o.mv.uni-kl.de:8080/api/auth/login'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    loginJSON = {'username': username, 'password': password}
    tokenAuthResp = requests.post(url, headers=headers, json=loginJSON).json()
    token = tokenAuthResp['token']
    return token

#function for getting telemetry data
def GetTelemetryData(CurlToken,DeviceToken):
    url = 'http://iot4h2o.mv.uni-kl.de:8080/api/plugins/telemetry/DEVICE/'+DeviceToken+'/values/timeseries'
    headers = {'Content-Type': 'application/json', 'X-Authorization': 'Bearer '+CurlToken}
    telemetryDataResp = requests.get(url, headers=headers).json()
    #telemetryDataResp = requests.get(url).json()
    return telemetryDataResp

#insert the following information
username2 = "t.pirard@uliege.be"
username = "t.pirard@zwgs.de"
password = "111122"
#Example network
DeviceID = "698e65a0-21c0-11ec-a052-af580412d5c6" 
DeviceToken = "guCnZNPPCPP6oA9NeE2Q"
DeviceID = "50e87610-c9dd-11ec-abdc-49029c7e8f07" 
DeviceToken = "5CTiU24QD1ldH3AOU6vP"
EntryExample = ["Head","Discharge"]
BarWaterColumn=10.197442889221
#Time data
TimeStamp = time()
PreviousDate = date.fromtimestamp(TimeStamp)
CurrentDate = PreviousDate
#Definition of different usefull device token and usefull entries
#Production unit
DeviceKuhardt = "5124b960-7da1-11eb-81e7-7bf4b1b85926" #Wasserwerk Kuhardt : MengeL1 + MengeL2 +MengeLeimersheim
TokenKuhardt = "uRdOU74bNrwob2wJt6aR"
EntryKuhardt =['MengeL1','MengeL2','MengeLeimersheim']
RevFactorKuhardt=[10*3600,10*3600,100*3600]
DeviceJockgrim = "47a69c00-7da1-11eb-81e7-7bf4b1b85926" #Wasserwerk Jockgrim : Menge + Druck
TokenJockgrim = "VaHJOZvERK3iebpkilwT"
EntryJockgrim = ['Menge','Druck']
RevFactorJockgrim=[3600,100/BarWaterColumn]
#Water towers : Wasserturm
NameTowers=['Hatz',"Rulz","Wor"]
DevicesWT=["39805350-7da1-11eb-81e7-7bf4b1b85926","308325c0-7da1-11eb-81e7-7bf4b1b85926","260db010-7da1-11eb-81e7-7bf4b1b85926"]
TokensWT=["n9IqRbv633DvwV8j6Zqb","8s7KqLd4jzIeGbblEauO","aKhhW6x92cFFEXybMFfa"]
EntryWT = ['Ablauf','Menge','Niveau']
RevFactorWT=[10*3600,10*3600,100]
#Booster system
DeviceKnittel = "5d4e7e30-f423-11eb-88d0-df9159a9b3d4" #Druckerhoehungsanlage - DEA Knittelsheim
TokenKnittel = "XoQ3yRVkWCmsDRqIyhuE"
EntryKnittel = ['Menge','Druck']
RevFactorKnittel = [100*3600,100/BarWaterColumn]

#Vector for devices
DevicesID=[DeviceKuhardt,DeviceJockgrim,DevicesWT[0],DevicesWT[1],DevicesWT[2],DeviceKnittel]
#Vector for token
TokensID=[TokenKuhardt,TokenJockgrim,TokensWT[0],TokensWT[1],TokensWT[2],TokenKnittel]
#Vector for keys
Keys=[EntryKuhardt,EntryJockgrim,EntryWT,EntryWT,EntryWT,EntryKnittel]
#Vector for correction factors
RevFactors=[RevFactorKuhardt,RevFactorJockgrim,RevFactorWT,RevFactorWT,RevFactorWT,RevFactorKnittel]
#Dictionnary for Elements
Entities={}
Ent=["Kuhardt","Jockgrim","Hatz","Rulz","Wor","Knittel"]
for Val in Ent:
    Entities[Val]={}
Test=1
for El in Entities:
    Entities[El]["Keys"]={}
    #Entities[El]["Keys"]["Name"]={}
cpt=0
#Definition of TokenID, DeviceID, Keys and Directory
Basic_Directory='E:\\Network_Thomas\\Jockgrim_Data\\'
file={}
#Entrées
for El in Entities:
    Entities[El]["TokenID"]=TokensID[cpt]
    Entities[El]["DeviceID"]=DevicesID[cpt]
    Entities[El]["Directory"]=Basic_Directory+El+'\\'
    file[El]={}
    for LocKey in Keys[cpt]:
        Entities[El]["Keys"][LocKey]={}
        file[El][LocKey]={}
    cpt_key=0
    for IdKey in Entities[El]["Keys"]:
        Entities[El]["Keys"][IdKey]={}
        Entities[El]["Keys"][IdKey]["TimeStamp"]=TimeStamp
        Entities[El]["Keys"][IdKey]["Value"]=0
        Entities[El]["Keys"][IdKey]["RevFactor"]=RevFactors[cpt][cpt_key]
        Entities[El]["Keys"][IdKey]["Filename"]=Entities[El]["Directory"]+IdKey+'_'+str(CurrentDate.year)+'_'+str(CurrentDate.month)+'.bin'
        #file[El][IdKey]=open(Entities[El]["Keys"][IdKey]["Filename"], 'a')
        Test=1
        cpt_key+=1
    cpt+=1
#Sorties
Entities_Out=['Hatz','Rulz','Wor']
File_Out=[]
for El in Entities_Out:
    File_Out.append(Entities[El]['Directory'])
#Part related to the time
Time={}
Time['Directory']=Basic_Directory+'Delta_Measurements.txt'
#Function to read the data in the file corresponding to the new_day

#for Elem in Entities:

client= TBDeviceMqttClient(broker, DeviceToken)
client.connect()  

next_reading = time() 
PreviousTimeStamp = time()
INTERVAL=5*60
NewTimeStamp=True

#Parameters for the potential simulatio of the network 
Simulation_Instant=True
network_directory="D:\\ProgThomas\\wolf_oo\\Sources-Thomas3\\Solutions\\Unit_Tests\\to_debug\\Compar_Model_Sensib_Extr_500"
new_initiation=1
while CurrentDate.year==2022:

    next_reading += INTERVAL
    sleep_time = next_reading-time()
    #Every device is read to access to its own information
    for Elem in Entities:
        telemetryData=GetTelemetryData(getCurlToken(),Entities[Elem]["DeviceID"])
        for Key in Entities[Elem]["Keys"]:
            TimeUsed=float(telemetryData[Key][0]['ts']/1000)
            if(Entities[Elem]["Keys"][Key]['TimeStamp']!=TimeUsed):
                Loc_Data=telemetryData[Key][0]['value']
                Loc_Data=float(Loc_Data)/float(Entities[Elem]["Keys"][Key]["RevFactor"])
                Loc_Data=str(Loc_Data)
                CurrentDate=pd.Timestamp(TimeUsed, unit='s',tz='Europe/Vatican')

                if(PreviousDate.month!=CurrentDate.month):
                    #The previous file with the previous day is closed and the new file with the current day is opened
                    Entities[Elem]["Filename"]=Entities[Elem]["Directory"]+Key+'_'+str(CurrentDate.year)+'_'+str(CurrentDate.month)+'.bin'
                    file[Elem][Key].close()
                    file[Elem][Key] = open(Entities[Elem]["Filename"], 'a')
                file[Elem][Key]=open(Entities[Elem]["Keys"][Key]["Filename"], 'a')
                file[Elem][Key].write(Loc_Data)
                file[Elem][Key].write('\n')
                Entities[Elem]["Keys"][Key]['TimeStamp']=TimeUsed
                file[Elem][Key].close()
                Test=1
                if(NewTimeStamp):
                    #Export of the current time of the measure : we consider a unique timestamp for each source of information
                    f_time=open(Time['Directory'],'a')
                    #We transform based on delta
                    Delta=CurrentDate.day*86400+CurrentDate.hour*3600+CurrentDate.minute*60+CurrentDate.second
                    f_time.write(str(Delta))
                    f_time.write('\n')
                    f_time.close()
                    NewTimeStamp=False
    NewTimeStamp=True
    #print(value)
    if sleep_time > 0:
        if(Simulation_Instant):
            Results_Reservoirs=wolfpy.jockgrim_application(Basic_Directory,network_directory,CurrentDate.year,CurrentDate.month,new_initiation)
            new_initiation=0
            telemetry = {"Hatzenbühl": Results_Reservoirs[0], "Rülzheim": Results_Reservoirs[1], "Wörth": Results_Reservoirs[2]}
            # Sending volume data to ThingsBoard
            client.send_telemetry(telemetry,1)
            #Sending results to the txt files to obtain also it on the machine
            cpt_elem=0
            for El in File_Out:
                El=El+'Results_'+str(CurrentDate.year)+'_'+str(CurrentDate.month)+'.txt'
                file_out = open(El, 'a')
                file_out.write(str(Results_Reservoirs[cpt_elem]))
                file_out.write('\n')
                cpt_elem+=1
                file_out.close()
        sleep(sleep_time)

#client.disconnect()
f.close()
Test=1