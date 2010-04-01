# set up espresso basics
from espresso.main._setup import *

# load espresso into PMI
pmiimport('espresso')

import _espresso
from espresso.Real3D import *
from espresso.Int3D import *
from espresso.System import *

infinity=float("inf")
nan=float("nan")
auto='auto'

if pmi.isController :
    # make sure that the workers exit when the script ends
    pmi.registerAtExit()
    # the script continues after this call
else :
    pmi.startWorkerLoop()
    # the script will usually not reach this point on the workers


    
