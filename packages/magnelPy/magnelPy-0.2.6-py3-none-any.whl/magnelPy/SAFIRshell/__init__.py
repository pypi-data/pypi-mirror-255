"""
magnelPy.SAFIRshell
===================
Provides
  1. SAFIR input file generation and modification
  2. run SAFIR from Python

=============== ==========================================================
SAFIR control ~ control.py
==========================================================================
Test            Test function (prints string to screen)
XXXX            XXXX
=============== ==========================================================

"""

### get submodules ###
from magnelPy.SAFIRshell.control import runSAFIR
# allows for direct (anaconda) command line SAFIR runs >> python -c "import magnelPy.SAFIRshell as x; x.runSAFIR()"
# https://towardsdatascience.com/whats-init-for-me-d70a312da583
