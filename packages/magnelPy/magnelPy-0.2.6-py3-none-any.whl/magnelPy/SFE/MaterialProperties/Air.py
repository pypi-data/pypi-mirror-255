"""MaterialProperties\\Air
Notes
-----
Temperature-dependent properties for use in SFE.
### data adopted from table thermodynamics - searching real reference (assumed Heat 'Transfer - A Practical Approach')
"""

#############
## IMPORTS ##
#############

import numpy as np

############
## MODULE ##
############

temps = np.array([-150, -100, -50, -40, -30, -20, -10, 0.0,  5.0,   10, 
	15,   20,  25,  30,  35,  40,  45,  50,   60,   70,
	80,   90, 100, 120, 140, 160, 180, 200,  250,  300,
	350,  400, 450, 500, 600, 700, 800, 900, 1000, 1500,
	2000]) # [C]; reference temperatures

def density(theta):
	""" Air density

	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range -150 - 2000 [°C]

	Returns
	-------
	rho : float
		 density [kg/m3]
	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import Air as air
	print(air.density(20))
	>>> 1.204
	"""
	density = np.array([ 2.866,  2.038,  1.582,  1.514,  1.451,
		1.394,  1.341,  1.292,  1.269,  1.246,
		1.225,  1.204,  1.184,  1.164,  1.145,
		1.127,  1.109,  1.092,  1.059,  1.028,
		0.9994, 0.9718, 0.9458, 0.8977, 0.8542,
		0.8148, 0.7788, 0.7459, 0.6746, 0.6158,
		0.5664, 0.5243, 0.4880, 0.4565, 0.4042,
		0.3627, 0.3289, 0.3008, 0.2772, 0.1990,
		0.1553]) # [kg/m3]; reference densities


	rho=np.interp(theta,temps,density,right=np.NAN,left=np.NAN)

	return rho

def specific_heat(theta):
	""" Air specific heat

	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range -150 - 2000 [°C]

	Returns
	-------
	cp : float
		 specific heat [J/(kg*K)]
	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import Air as air
	print(air.specific_heat(20))
	>>> 1007
	"""
	spec_heat = np.array([ 983,  966,  999, 1002, 1004,
					  1005, 1006, 1006, 1006, 1006,
					  1007, 1007, 1007, 1007, 1007,
					  1007, 1007, 1007, 1007, 1007,
					  1008, 1008, 1009, 1011, 1013,
					  1016, 1019, 1023, 1033, 1044, 
					  1056, 1069, 1081, 1093, 1115,
					  1135, 1153, 1169, 1184, 1234,
					  1264]) # [J/(kg*K)]; reference values


	cp=np.interp(theta,temps,spec_heat,right=np.NAN,left=np.NAN)

	return cp

def conductivity(theta):
	""" Air conductivity

	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range -150 - 2000 [°C]

	Returns
	-------
	k : float
		 conductivity [W/(m*K)]
	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import Air as air
	print(air.conductivity(20))
	>>> 0.02514
	"""
	conductivity = np.array([0.01171, 0.01582, 0.01979, 0.02057, 0.02134,
							 0.02211, 0.02288, 0.02364, 0.02401, 0.02439,
							 0.02476, 0.02514, 0.02551, 0.02588, 0.02625,
							 0.02662, 0.02699, 0.02735, 0.02808, 0.02881,
							 0.02953, 0.03024, 0.03095, 0.03235, 0.03374,
							 0.03511, 0.03646, 0.03779, 0.04104, 0.04418,
							 0.04721, 0.05015, 0.05298, 0.05572, 0.06093,
							 0.06581, 0.07037, 0.07465, 0.07868, 0.09599,
							 0.11113]) # [W/(m*K)]; reference values


	k=np.interp(theta,temps,conductivity,right=np.NAN,left=np.NAN)

	return k

def kinematic_viscosity(theta):
	""" Air kinematic viscosity

	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range -150 - 2000 [°C]

	Returns
	-------
	v : float
		 kinematic viscosity [m2/s]
	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import Air as air
	print(air.kinematic_viscosity(20))
	>>> 1.516e-05

	"""
	kinematic_viscosity = np.array([0.3013, 0.5837, 0.9319, 1.008, 1.087,
						  1.169,  1.252,  1.338, 1.382, 1.426,
						  1.470,  1.516,  1.562, 1.608, 1.655,
						  1.702,  1.750,  1.798, 1.896, 1.995,
						  2.097,  2.201,  2.306, 2.522, 2.745,
						  2.975,  3.212,  3.455, 4.091, 4.765,
						  5.475,  6.219,  6.997, 7.806, 9.515,
						  11.33,  13.26,  15.29, 17.41, 29.22,
						  66.3]) * 10**-5 # [m2/s]; reference values

	v=np.interp(theta,temps,kinematic_viscosity,right=np.NAN,left=np.NAN)

	return v

def Prandtl(theta):
	""" Air Prandtl number

	Parameters
	----------	
	theta : float or np.array
		(array of) Temperature in range -150 - 2000 [°C]

	Returns
	-------
	Pr : float
		 Prandtl number [-]
	
	Example use
	-----------
	from magnelPy.SFE.MaterialProperties import Air as air
	print(air.Prandtl(20))
	>>> 0.7309

	"""
	Prandtl = np.array([0.7246, 0.7263, 0.7440, 0.7436, 0.7425,
                        0.7408, 0.7387, 0.7362, 0.7350, 0.7336,
                        0.7323, 0.7309, 0.7296, 0.7282, 0.7268,
                        0.7255, 0.7241, 0.7228, 0.7202, 0.7177,
                        0.7154, 0.7132, 0.7111, 0.7073, 0.7041,
                        0.7014, 0.6992, 0.6974, 0.6946, 0.6935,
                        0.6937, 0.6948, 0.6965, 0.6986, 0.7037,
                        0.7092, 0.7149, 0.7206, 0.7260, 0.7478,
                        0.7539]) # [m2/s]; reference values

	Pr=np.interp(theta,temps,Prandtl,right=np.NAN,left=np.NAN)

	return Pr