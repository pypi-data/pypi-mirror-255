
def Read_File(filename,filename_out,filename_resume,filename_period,Aggreg_Hours):
#out_file = open(filename_out,'w')
    file = open(filename,'r')
    file_out = open(filename_out,'w')
    Value_Q=[]
    Value_Hour=[]
    cpt_val=0
    First_NewDay=0
    Good_Period=True
    Cur_Value=0
    for New_Word in file:
        #Extraction des différentes données utiles : heure, valeurs
        New_Word=New_Word.split()
        #Selon numéro de l'élément, on sait ce que cela représente
        #Analyse pour extraire minutes
        if(bool(New_Word)):
            Day=New_Word[0].split('.')
            Date=New_Word[1].split(':')
            Hour=int(Date[0])
            Hour_f=float(Date[0])
            New_Word[4]=New_Word[4].replace(",", ".")
            if(Day[2]=='2020' and Day[1]=='01' and Day[0]=='09' and Hour>12):
                Good_Period=False
            New_Improve=True
            if(Good_Period):
                New_Value=float(New_Word[4])
                #if(New_Value<-5):
                #    New_Value=Cur_Value
                if(cpt_val>0):
                    New_Day=int(Date[0])
                    New_Minute=int(Date[1])
                    if(New_Day==Old_Day):
                        Diff_Day=New_Minute-Old_Minute
                    else:
                        Old_Minute=60-Old_Minute
                        Diff_Day=Old_Minute+New_Minute
                        Old_Day=New_Day
                        if(First_NewDay==0):
                            Hour_Val=int(Date[0])
                            if(Hour_Val==0):
                                PosNewDay=len(Value_Q) #On commence le comptage au début de la première nouvelle journée
                                First_NewDay=1
                        else:
                            if(First_NewDay==1):
                                PosLastDay=len(Value_Q)
                                if(PosLastDay==1037):
                                    Test=1
                                DiffDay=PosLastDay-PosNewDay
                                Mod=DiffDay%60
                                if(Mod>0):
                                    Test=1
                    if(Diff_Day==1):
                        Value_Q.append(New_Value)
                        Value_Hour.append(Hour_f)
                        Cur_Value=New_Value
                    else:
                        Added_V=(Cur_Value+New_Value)/2.0
                        New_Improve=False
                        for Min in range(Diff_Day):
                            Sentence=Day[0]+','+Day[1]+','+Date[0]+','+Date[1]+','+New_Word[4]+'\n'
                            file_out.write(Sentence)
                            Value_Q.append(Cur_Value)
                            Value_Hour.append(Hour_f)
                    Old_Minute=New_Minute

                else:
                    Value_Q.append(New_Value)
                    Value_Hour.append(Hour_f)
                    Old_Minute=int(Date[1])
                    Old_Day=int(Date[0])
                    Cur_Value=New_Value

            cpt_val+=1
            if(New_Improve):
                Sentence=Day[0]+','+Day[1]+','+Date[0]+','+Date[1]+','+New_Word[4]+'\n'
                file_out.write(Sentence)
    file.close()
    file_out.close()
    IERR=0
    #On va analyser le nombre de journées : on commence première journée à minuit pour terminer aussi à minuit
    NbHour=(PosLastDay-PosNewDay)/60
    Mod=NbHour%24
    NbElem=Mod*60
    PosLastDay=PosLastDay-NbElem
    NbHour=int((PosLastDay-PosNewDay)/60)
    NbDays=int(NbHour/24)
    #On évalue alors l'évolution des données selon durée choisie par l'utilisateur
    Nb_Period=int((PosLastDay-PosNewDay)/Time)

    ID_Pos=PosNewDay
    Value_P=[]
    Period_P=[]
    Period_Hour=[]
    Pos_P=[]
    filename_period=filename_period+str(Time)+'min.txt'
    file_out = open(filename_period,'w')
    cpt_pos=0
    Prev_P=0
    for Id_Period in range(Nb_Period):
        Moy_P=sum(Value_Q[ID_Pos:ID_Pos+Time])/Time
        Moy_Hour=sum(Value_Hour[ID_Pos:ID_Pos+Time])/Time
        #Certaines données incohérentes sont observées durant la nuit : on vient donc évaluer plutôt récupérer une valeur précédente
        if(cpt_pos==2455):
            Test=2
        if(Moy_P<-5):
            Moy_P=Prev_P
        Test=1
        Value_P.append(Moy_Hour)
        Prev_P=Moy_P
        #On exporte la valeur à chaque nouvelle période de temps
        Sum_P=Moy_P*Time
        #Sum_Hour=Moy_Hour*Time
        cpt_pos+=1
        Period_P.append(Sum_P)
        Pos_P.append(ID_Pos)
        #Period_Hour.append(Sum_Hour)
        ID_Pos+=Time
        Sentence=str(Sum_P)+'\n'
        file_out.write(Sentence)

    file_out.close()
    #On évalue ensuite la variance selon chaque période
    ID_Pos=PosNewDay
    STD_P=[]
    for Id_Period in range(Nb_Period):
        Var_P=0
        for El in range(Time):
            Var_P+=(Value_Q[ID_Pos+El]-Value_P[Id_Period])**2.0/float(Time)
        Var_P=Var_P**0.5
        ID_Pos+=Time
        STD_P.append(Var_P)
    #On va également obtenir la distribution selon la journée
    Nb_Elem=int(60*24/Time)
    Elem_Var=[]
    for ID_Elem in range(Nb_Elem):
        Elem_Var.append([])
    for ID_Day in range(NbDays):
        for ID_Elem in range(Nb_Elem):
            Elem_Var[ID_Elem].append(Value_P[ID_Elem+ID_Day*Nb_Elem])
            Test=1
        Test=1
    #On trie les listes
    for ID_Elem in range(Nb_Elem):
        Elem_Var[ID_Elem]=sorted(Elem_Var[ID_Elem])
    #On vient récupérer valeur médiane
    Perc=[0.5,0.05,0.95]
    PosEl=[]
    for Position in Perc:
        PosEl.append(int(Position*NbDays))
    Val_El=[]
    filename_resume=filename_resume+str(Time)+'min.txt'
    file = open(filename_resume,'w')
    for ID_Elem in range(Nb_Elem):
        Mean_Val=sum(Elem_Var[ID_Elem])/NbDays
        Val_El.append([])
        Val_El[ID_Elem].append(Mean_Val)
        Sentence=str(Mean_Val)
        for Perc_Pos in PosEl:
            Val_El[ID_Elem].append(Elem_Var[ID_Elem][Perc_Pos])
            Sentence+=','
            Sentence+=str(Elem_Var[ID_Elem][Perc_Pos])
        Sentence+='\n'
        file.write(Sentence)
        file.write(Sentence)
    file.close()
    return Period_P,Value_P,Pos_P

def Write_File_Demand(file_demand,Period_Neupotz,Period_Leimer,Period_Hour,Pos_Period,Time):
    file_demand1=file_demand+str(Time)+'min.txt'
    file_out = open(file_demand1,'w')
    file_demand2=file_demand+'Neupotz_Upd_'+str(Time)+'min.txt'
    file_out2 = open(file_demand2,'w')
    file_demand3=file_demand+'LeimerUpd_'+str(Time)+'min.txt'
    file_out3 = open(file_demand3,'w')
    file_demand4=file_demand+'Bad_Period.txt'
    file_out4 = open(file_demand4,'w')
    Bad_Periods=0 #Period where the water demand that is available is lower than 0
    Bad_Periods2=0
    for ID_Period in range(len(Period_Neupotz)):
        Avail_Water=Period_Neupotz[ID_Period]+Period_Leimer[ID_Period]
        if(Avail_Water<0):
            Bad_Periods+=1
            if(Period_Hour[ID_Period]>7 and Period_Hour[ID_Period]<22):
                Test=3
                Bad_Periods2+=1
            #On vient assurer la continuité
            Period_Neupotz[ID_Period]=Period_Neupotz[ID_Period]-Avail_Water/2
            Period_Leimer[ID_Period]=Period_Leimer[ID_Period]-Avail_Water/2
            Sentence4=str(Period_Hour[ID_Period])+str(Pos_Period[ID_Period])+'\n'
            Avail_Water=0
            file_out4.write(Sentence4)

        Sentence=str(Avail_Water)+'\n'
        Sentence2=str(Period_Neupotz[ID_Period])+'\n'
        Sentence3=str(Period_Leimer[ID_Period])+'\n'
        file_out.write(Sentence)
        file_out2.write(Sentence2)
        file_out3.write(Sentence3)
    file_out.close()
    file_out2.close()
    file_out3.close()
    file_out4.close()
    IERR=0
    return IERR

#Analyse injection Neupotz
filename='D:\\PIRARD_Thomas\\Reseau_Jockgrim\\FlowmetersData\\FlowSensorData\\NeupotzData.txt'
filename_out='D:\\PIRARD_Thomas\\Reseau_Jockgrim\\FlowmetersData\\FlowSensorData\\NeupotzData_Improved.txt'
filename_resume='D:\\PIRARD_Thomas\\Reseau_Jockgrim\\FlowmetersData\\FlowSensorData\\Neupotz_Resume_'
filename_period='D:\\PIRARD_Thomas\\Reseau_Jockgrim\\FlowmetersData\\FlowSensorData\\Neupotz_Periods_'
Time=60
Period_Neupotz,Period_Hour_Neupotz,Pos_Period_Neu=Read_File(filename,filename_out,filename_resume,filename_period,Time)
#Analyse injection Leimer
filename='D:\\PIRARD_Thomas\\Reseau_Jockgrim\\FlowmetersData\\FlowSensorData\\LeimerData.txt'
filename_out='D:\\PIRARD_Thomas\\Reseau_Jockgrim\\FlowmetersData\\FlowSensorData\\LeimerData_Improved.txt'
filename_resume='D:\\PIRARD_Thomas\\Reseau_Jockgrim\\FlowmetersData\\FlowSensorData\\Leimer_Resume_'
filename_period='D:\\PIRARD_Thomas\\Reseau_Jockgrim\\FlowmetersData\\FlowSensorData\\Leimer_Periods_'
Period_Leimer,Period_Hour_Leimer,Pos_Period_Lei=Read_File(filename,filename_out,filename_resume,filename_period,Time)
#Récupération information sur eau disponible sur utilisateurs
file_demand='D:\\PIRARD_Thomas\\Reseau_Jockgrim\\FlowmetersData\\FlowSensorData\\Demand_Periods_'
IERR=Write_File_Demand(file_demand,Period_Neupotz,Period_Leimer,Period_Hour_Neupotz,Pos_Period_Lei,Time)
Test=1