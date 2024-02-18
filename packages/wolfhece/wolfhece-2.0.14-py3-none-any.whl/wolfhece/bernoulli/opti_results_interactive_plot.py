# %% Libraries
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
# Import slider package
from matplotlib.widgets import Slider

# ===================================================================================
#                                 PARAMETERS
# ===================================================================================


# %% Parameters

# Parameter to display   -> TO CHANGE BEFORE SIMULATION
# 0: X1,    1: X2,      2: X3,      3: X4   
id1_fixed = 0   # parameter to tune 1
id2_fixed = 3   # parameter to tune 2
id1 = 1     # parameter on the x axis
id2 = 2     # parameter on the y axis


# File name
# dirName = "F:/Christophe/Simulations/Optimisation/Screening_GR4/10_13/"
#dir_path = os.path.dirname(os.path.realpath(__file__))
#dirName = dir_path + "/Opti_GR4_25Params/"
dirName = "D:/PIRARD_Thomas/Opti_GR4_25Params/"
fileName = "example.rpt"

# Nomber of parameters
nbParams = 4

# Steps for each parameter
dx1 = 3
dx2 = 0.2
dx3 = 8
dx4 = 1.6
dx = [dx1, dx2, dx3, dx4]

# Range for each parameter
p_min = [75, -5, 100, 10]
p_max = [150, 0, 300, 45]

# Label of parameters
my_labels = ["X1 [mm]", "X2 [mm/hour]", "X3 [mm]", "X4 [hour]"]
my_labelsSlider = ["X1 ", "X2 ", "X3 ", "X4 "]
my_valfmt = ["%3.1f [mm]", "%1.1f [mm/hour]", "%3.1f [mm]", "%2.1f [hour]"]

# Number of simulations
nbSimul = 13






# ===================================================================================
#                                 FUNCTIONS
# ===================================================================================

def get_Nash(i1: int, P1: float, i2: int, P2: float, xi: int, yi:int) -> float:
    Dx = []
    for i in range(nbEl):
        if(matrixData[i][i1]==P1 and matrixData[i][i2]==P2):
            if Dx == []:
                Dx = [matrixData[i,:]]
            else:
                Dx = np.vstack([Dx, matrixData[i,:]])

    xMax = 0.0
    xMin = 0.0
    yMin = 0.0
    yMax = 0.0

    xMax = np.max(Dx[:,xi])
    xMin = np.min(Dx[:,xi])
    x = np.arange(xMin,xMax+dx[xi],dx[xi])
    yMin = np.min(Dx[:,yi])
    yMax = np.max(Dx[:,yi])
    y = np.arange(yMin,yMax+dx[yi],dx[yi])

    n = len(Dx[:,0])
    Nash = np.zeros((len(y),len(x)))
    for i in range(n):
        tmp_ix = (Dx[i][xi]-xMin)/dx[xi]
        tmp_iy = (Dx[i][yi]-yMin)/dx[yi]
        if(tmp_ix%1>0.00001 and tmp_ix%1<0.99999 and tmp_iy%1>0.00001 and tmp_iy%1<0.99999):
            print("Potential error, please check!")
            sys.exit()
        else:
            ix = int(round(tmp_ix))
            iy = int(round(tmp_iy))
        Nash[iy][ix] = Dx[i][4]

    return Nash, xMin,xMax,yMin,yMax


# Update values
def update(val):
    curX2 = round(s_X2.val,1)
    curX4 = round(s_X4.val,1)
    Nash,xMin,xMax,yMax,yMin = get_Nash(id1_fixed,curX2,id2_fixed,curX4,id1,id2)
    # f_d, = [ax.imshow(Nash, interpolation='None', extent=[xMin,xMax,yMax,yMin], aspect='auto')]
    # cbar.draw_all()
    # cbar = fig.colorbar(f_d,ax=ax)
    f_d.set_data(Nash)
    f_d.set_clim(vmin=Nash.min(), vmax=Nash.max())
    fig.canvas.draw_idle()




# %% Reading of the file(s)
list_data = []
for simul in range(nbSimul):
    # data_reader = []
    fileAccess = dirName + str(simul+1) + "_" + str(nbSimul) + "/" + fileName
    with open(fileAccess, newline='') as fileID:
        data_reader = []
        data_reader = csv.reader(fileID,delimiter='|')       
        i=0
        for raw in data_reader:
            if i>2:
                list_data.append(raw)
            i += 1
        

nbEl = len(list_data[:]) - nbSimul    # - nbSimul because the last line of each file is composed of only '*'
matrixData = np.zeros((nbEl,nbParams+1))
counter = 0
for i in range(len(list_data[:])): 
    if len(list_data[i]) != nbParams+1+3:
        if(len(list_data[i])==1 and list_data[i][0][0] == '*'):
            continue
        else:
            print("ERROR: Something went wrong with the number of elements in the input file!")
            sys.exit()
    for j in range(nbParams+1):
        matrixData[counter][j] = float(list_data[i][2+j].strip())
    counter += 1


# %% Best parameters
best_NS = np.max(matrixData[:,4])
min_NS = np.min(matrixData[:,4])
i_bNS = np.argmax(matrixData[:,4])
i_mNS = np.argmin(matrixData[:,4])
print("Best parameters : ", matrixData[i_bNS,:-1])
print("Best Nash = ", matrixData[i_bNS,-1])
bX1 = matrixData[i_bNS][0]
bX2 = matrixData[i_bNS][1]
bX3 = matrixData[i_bNS][2]
bX4 = matrixData[i_bNS][3]

best_param = [bX1, bX2, bX3, bX4]


# %% ----- Interactive plot -----

# %% Construct plane (X1,X3) with variable parameters X2 & X4


# Create main axis
fig = plt.figure(figsize=(6, 4))
ax = fig.add_subplot(111)
fig.subplots_adjust(bottom=0.2, top=0.75)


# Create axes for sliders

ax_T = fig.add_axes([0.3, 0.92, 0.4, 0.05])
ax_T.spines['top'].set_visible(True)
ax_T.spines['right'].set_visible(True)

ax_Ef = fig.add_axes([0.3, 0.85, 0.4, 0.05])
ax_Ef.spines['top'].set_visible(True)
ax_Ef.spines['right'].set_visible(True)



# Create sliders
s_X2 = Slider(ax=ax_T, label=my_labelsSlider[id1_fixed], valmin=p_min[id1_fixed], valmax=p_max[id1_fixed], valstep=dx[id1_fixed],valinit=best_param[id1_fixed], valfmt=my_valfmt[id1_fixed], facecolor='#cc7000')
s_X4 = Slider(ax=ax_Ef, label=my_labelsSlider[id2_fixed],valmin=p_min[id2_fixed], valmax=p_max[id2_fixed], valstep=dx[id2_fixed],valinit=best_param[id2_fixed], valfmt=my_valfmt[id2_fixed], facecolor='#cc7000')


# Plot default data
Nash = []
# x = np.linspace(-0, 1, 100)
X2_0 = best_param[id1_fixed]
X4_0 = best_param[id2_fixed]
Nash,xMin,xMax,yMax,yMin = get_Nash(id1_fixed,X2_0,id2_fixed,X4_0,id1,id2)
# f_d, = ax.imshow(Nash, interpolation='None', extent=[xMin,xMax,yMax,yMin], aspect='auto')
f_d, = [ax.imshow(Nash, interpolation='None', extent=[xMin,xMax,yMin,yMax], aspect='auto')]
ax.set_xlabel(my_labels[id1])
ax.set_ylabel(my_labels[id2])
cbar = fig.colorbar(f_d,ax=ax)
# f_d, = ax.plot(x, y, linewidth=2.5)

s_X2.on_changed(update)
s_X4.on_changed(update)



    

plt.show()

t=1
# import pickle
# pickle.dump(fig, open('FigureObject.fig.pickle', 'wb')) # This is for Python 3 - py2 may need `file` instead of `open`

