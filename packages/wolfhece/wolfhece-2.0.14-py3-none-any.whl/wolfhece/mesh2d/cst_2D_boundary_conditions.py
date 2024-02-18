from enum import Enum
from typing import Union

if not '_' in __builtins__:
    import gettext
    _=gettext.gettext

"""
Please note that integer values must conform to FORTRAN Wolf modules
They can not be changed freely by the Python user/developer
"""
class Direction(Enum):
    LEFT  = 1
    BOTTOM= 2
    X     = 1
    Y     = 2

class BCType_2D_GPU(Enum):
    # The numbers match the numbers in Wolf's simulations parameters.
    # H    = (1,_('Water level [m]'))
    QX   = (2,_('Flow rate along X [m²/s]'))
    QY   = (3,_('Flow rate along Y [m²/s]'))
    NONE = (4,_('None'))
    HMOD = (7,_('Water level [m] / impervious if entry point'))
    FROUDE_NORMAL = (8,_('Froude normal to the border [-]'))

class BCType_2D(Enum):
    # The numbers match the numbers in Wolf's 2D simulations parameters.
    H    = (1,_('Water level [m]'))
    QX   = (2,_('Flow rate along X [m²/s]'))
    QY   = (3,_('Flow rate along Y [m²/s]'))
    NONE = (4,_('None'))
    QBX  = (5,_('Sediment flow rate along X [m²/s]'))
    QBY  = (6,_('Sediment flow rate along Y [m²/s]'))
    HMOD = (7,_('Water level [m] / impervious if entry point'))
    FROUDE_NORMAL = (8,_('Froude normal to the border [-]'))
    ALT1 = (9,_('to check'))
    ALT2 = (10,_('to check'))
    ALT3 = (11,_('to check'))
    DOMAINE_BAS_GAUCHE = (12,_('to check'))
    DOMAINE_DROITE_HAUT = (13,_('to check'))
    SPEED_X = (14,_('Speed along X [m/s]'))
    SPEED_Y = (15,_('Speed along Y [m/s]'))
    FROUDE_ABSOLUTE = (16,_('norm of Froude in the cell [-]'))

class BCType_2D_OO(Enum):
    WATER_DEPTH       = (1, _('Water depth [m]'))
    WATER_LEVEL       = (2, _('Water level [m]'))
    FROUDE_NORMAL     = (4, _('Froude normal to the border [-]'))
    FREE_NONE         = (5, _('Free border'))
    CONCENTRATION     = (7, _('Concentration [-]'))
    IMPERVIOUS        = (99, _('Impervious'))
    NORMAL_DISCHARGE     = (31, _('Normal discharge [m²/s]'))
    TANGENT_DISCHARGE    = (32, _('Tangent discharge [m²/s]'))
    MOBILE_DAM_POWER_LAW = (127, _('Mobile dam with power law'))
    CLOSE_CONDUIT_QNORMAL     = (61, _('Close conduit - normal discharge [m²/s]'))
    CLOSE_CONDUIT_QTANGET     = (62, _('Close conduit - tangent discharge [m²/s]'))
    CLOSE_CONDUIT_H_FOR_SPEED = (63, _('Close conduit - h for speed [m]'))

def choose_bc_type(version:Union[int,str] = 1):
    if version==1 or version =='prev':
        return BCType_2D
    elif version==2 or version =='oo':
        return BCType_2D_OO
    elif version==3 or version =='gpu':
        return BCType_2D_GPU

# Color associated to a number of BC per border
ColorsNb = {1 : (0.,0.,1.),
            2 : (1.,.5,0.),
            3 : (0.,1.,0.),
            4 : (1.,0.,1.),
            5 : (0.,1.,1.)}
