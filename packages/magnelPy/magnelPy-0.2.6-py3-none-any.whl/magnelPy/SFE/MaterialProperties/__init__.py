"""
magnelPy.SFE.MaterialProperties
============
Provides
  1. Temperature-dependent material properties (functions)

=============== =================================================================
Steel ~ Steel Properties
=================================================================================
ky_EC3          Steel yield stress retention factor according to EN 1993-1-2:2005
kE_EC3          Steel modulus of elasticity retention factor according to EN 1993-1-2:2005
density_EC3     Steel density according to EN 1993-1-2:2005
cp_EC3          Steel specific heat according to EN 1993-1-2:2005
=============== =================================================================

=============== =================================================================
SFRM ~ Sprayed Fire-Resistive Material Properties
=================================================================================
rho             SFRM density according to Ref(A)
cp              SFRM specific heat according to Ref(A)
ki              SFRM conductivity according to Ref(A)
=============== =================================================================
Ref(A): Gernay, T., Khorasani, N.E. and Garlock, M., 2016. Fire fragility curves for steel buildings
in a community context: A methodology. Engineering Structures, 113, pp.259-276.
=================================================================================

=============== =================================================================
UserDefined ~ User Defined Material
=================================================================================
rho             Density
cp              Specific heat
k               Conductivity
=============== =================================================================

"""

### get submodules ###
from magnelPy.SFE.MaterialProperties import Air
from magnelPy.SFE.MaterialProperties import SFRM
from magnelPy.SFE.MaterialProperties import Steel
from magnelPy.SFE.MaterialProperties.UserDefined import UserDefined
