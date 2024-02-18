
def wolf():
    """ Main wolf application : Map Manager"""
    from .apps.wolf import main
    main()

def wolf2d():
    """ Application for 2D simuations """
    from .apps.wolf2D import main
    main()

def digitizer():
    """ Application for digitizing curves """
    from .apps.curvedigitizer import main
    main()

def params():
    """ Application for managing parameters in WOLF format """
    from .apps.ManageParams import main
    main()

def optihydro():
    """ Application for hydrological optimisation """
    from .apps.Optimisation_hydro import main
    main()

def hydro():
    """ Application for hydrological simulations """
    from .apps.wolfhydro import main
    main()

def compare():
    """ Application for comparing 2D arrays """
    from .apps.wolfcompare2Darrays import main
    from PyTranslate import _
    from wolf_array import WolfArray
    from pathlib import Path
    import sys
    from pathlib import Path

    """gestion de l'éxécution du module en tant que code principal"""
    # total arguments
    n = len(sys.argv)
    # arguments
    print("Total arguments passed:", n)
    assert n in [2,3], _('Usage : wolfcompare <directory> or wolfcompare <file1> <file2>')
    
    if n==2:
        mydir = Path(sys.argv[1])
        if mydir.exists():
            main(mydir)
        else:
            print(_('Directory not found'))
    elif n==3:
        file1 = Path(sys.argv[1])
        file2 = Path(sys.argv[2])

        if file1.exists() and file2.exists():
            main('', [WolfArray(file1), WolfArray(file2)])
        else:
            if not file1.exists():
                print(_('File {} not found'.format(file1)))
            if not file2.exists():
                print(_('File {} not found'.format(file2)))
