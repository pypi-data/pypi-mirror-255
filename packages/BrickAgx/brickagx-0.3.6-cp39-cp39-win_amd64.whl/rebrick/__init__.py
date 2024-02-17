import os
__AGXVERSION__ = "2.37.2.0"
__version__ = "0.3.6"
try:
    import agx
    if agx.__version__ != __AGXVERSION__:
        print(f"This version of brickagx is compiled for AGX {__AGXVERSION__} only and may crash with your {agx.__version__} version, upgrade brickagx or AGX to make sure the versions are suited for eachother")
except:
    print("Failed finding AGX Dynamics, have you run setup_env?")
    exit(255)


if "DEBUG_AGXBRICK" in os.environ:
    print("#### Using Debug build ####")
    try:
        from .debug.api import *
        from .debug import Core
        from .debug import Math
        from .debug import Physics
        from .debug import Simulation
    except:
        print("Failed finding rebrick modules or libraries, did you set PYTHONPATH correctly? Should point to where rebrick directory with binaries are located")
        print("Also, make sure you are using the same Python version the libraries were built for.")
        exit(255)
else:
    try:
        from .api import *
        from . import Core
        from . import Math
        from . import Simulation
    except:
        print("Failed finding rebrick modules or libraries, did you set PYTHONPATH correctly? Should point to where rebrick directory with binaries are located")
        print("Also, make sure you are using the same Python version the libraries were built for.")
        exit(255)
