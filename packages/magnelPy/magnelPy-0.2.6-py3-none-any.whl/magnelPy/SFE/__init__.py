"""
magnelPy.SFE
============
Provides
  1. Fire definition
  2. Thermal calculation tools
  3. Structural calculation tools
  4. Material properties

=============== ==========================================================
Fire definition ~ FireCurve
==========================================================================
ISO834          ISO834 standard fire definition
=============== ==========================================================

"""

### get submodules ###
from magnelPy.SFE import FireCurve
from magnelPy.SFE import ThermalTools
from magnelPy.SFE import Radiation
from magnelPy.SFE import MaterialProperties



### get command line functionality ###
from magnelPy.SFE.ThermalTools import EC_concreteSlab_ISO834
from magnelPy.SFE.ThermalTools import EC_concreteSlab_ECparametric

