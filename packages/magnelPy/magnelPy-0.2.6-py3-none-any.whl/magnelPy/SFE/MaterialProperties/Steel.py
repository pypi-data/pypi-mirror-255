"""MaterialProperties\\Steel
Notes
-----
Temperature-dependent properties for use in SFE.
"""

#############
## IMPORTS ##
#############

import numpy as np

############
## MODULE ##
############

def ky_EC3(theta):
	""" Steel yield stress retention factor according to EN 1993-1-2:2005

	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]

	Returns
	-------
	ky_EC3 : float or np.array
		 retentionfactor for steel yield stress [-]
		 EN 1993-1-2:2005, Table 3.1
	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import Steel as steel
	import numpy as np	
	theta=np.arange(100,1200,100)
	kfy=steel.ky_EC3(theta)
	print(kfy)
	>>> [1.   1.   1.   1.   0.78 0.47 0.23 0.11 0.06 0.04 0.02]
	"""
	T=[20,400,500,600,700,800,900,1100,1200]
	k=[1,1,0.78,0.47,0.23,0.11,0.06,0.02,10**-10]
	ky_EC3=np.interp(theta,T,k)
	return ky_EC3


def kE_EC3(theta):
	""" Steel modulus of elasticity retention factor according to EN 1993-1-2:2005

	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]

	Returns
	-------
	kE_EC3 : float or np.array
		 retentionfactor for steel modulus of elasticity [-]
		 EN 1993-1-2:2005, Table 3.1
	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import Steel as steel
	import numpy as np	
	theta=np.arange(100,1200,100)
	kfy=steel.kE_EC3(theta)
	print(kE)
	>>> [1.     0.9    0.8    0.7    0.6    0.31   0.13   0.09   0.0675 0.045 0.0225]
	"""
	T=[20,100,500,600,700,800,1100,1200]
	k=[1,1,0.6,0.31,0.13,0.09,0.0225,10**-10]
	kE_EC3=np.interp(theta,T,k)
	return kE_EC3

def density_EC3(theta=None):
	""" Steel density according to EN 1993-1-2:2005

	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]

	Returns
	-------
	rho_EC3 : float
		 density [kg/m3]
		 EN 1993-1-2:2005, 3.2.2
	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import Steel as steel
	print(steel.density_EC3())
	>>> 7850.0
	"""
	if  isinstance(theta,np.ndarray):
		rho_EC3 = 7850.0*np.ones(np.shape(theta)) # [kg/m3]
	else:
		rho_EC3 = 7850.0 # [kg/m3]
	return rho_EC3

def cp_EC3(theta):
	""" Steel specific heat according to EN 1993-1-2:2005;
	note: constant specific heat maintained above 1200 degrees C for numerical purposes

	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]

	Returns
	-------
	cp : float or np.array
		 specific heat [J/kgK]
		 EN 1993-1-2:2005, 3.4.1.2
	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import Steel as steel
	import numpy as np	
	theta=np.arange(100,500,100)
	cp=steel.cp_EC3(theta)
	print(cp)
	>>> [487.62 529.76 564.74 605.88]
	"""

	cp=np.select([theta<600, theta<735, theta<900, theta<=1200, theta<2000],  
            [425+0.773*theta-1.69/1000*theta**2+2.22*10**-6*theta**3, 666+13002/(738-theta), 545+17820/(theta-731),650,650])

	return cp


