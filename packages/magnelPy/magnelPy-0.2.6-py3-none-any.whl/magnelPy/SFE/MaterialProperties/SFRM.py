"""MaterialProperties\\SFRM
Notes
-----
Temperature-dependent properties for use in SFE.

Probabilitic material properties for SFRM at elevated temperatures
Ref(A): Gernay, T., Khorasani, N.E. and Garlock, M., 2016. Fire fragility curves for steel buildings
in a community context: A methodology. Engineering Structures, 113, pp.259-276.
"""

#############
## IMPORTS ##
#############

import numpy as np

############
## MODULE ##
############

def rho(theta,eps=0):
	""" SFRM density according to Ref(A)
	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]
	eps: float
		Probabilistic parameter (standard normal distribution)
		Default: eps = 0 for mean values
	Returns
	-------
	res : float
		 density [kg/m3]
	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import SFRM as sfrm
	print(sfrm.rho(20))
	>>> 284.58
	"""
	return np.exp(-2.028 +7.83*(theta)**-0.0065 + 0.122*eps) # [kg/m3]

def cp(theta,eps=0):
	""" SFRM specific heat according to Ref(A);

	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]

	eps: float
		Probabilistic parameter (standard normal distribution)
		Default: eps = 0 for mean values

	Returns
	-------
	res : float or np.array
		 specific heat [J/kgK]

	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import SFRM as sfrm
	import numpy as np	
	theta=np.arange(100,500,100)
	cp=sfrm.cp(theta)
	print(cp)
	>>> [924.58, 1031.12, 1117.92, 1188.98]
	"""
	return 1700-np.exp(6.81 - 1.61*(10**-3)*theta + 0.44*(10**-6)*(theta**2) + 0.213*eps)

def ki(theta,eps=0):
	""" SFRM conductivity according to Ref(A)

	Parameters
	----------
	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]

	eps: float
		Probabilistic parameter (standard normal distribution)
		Default: eps = 0 for mean values

	Returns
	-------
	res : float or np.array
		 conductivity [W/mK]

	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import SFRM as sfrm
	import numpy as np	
	theta=np.arange(100,500,100)
	ki=sfrm.ki(theta)
	print(ki)
	>>> [0.0794, 0.0954, 0.1141, 0.1360]
	"""	
	return np.exp(-2.72 + 1.89*(10**-3)*theta - 0.195*(10**-6)*(theta**2) + 0.209*eps)





