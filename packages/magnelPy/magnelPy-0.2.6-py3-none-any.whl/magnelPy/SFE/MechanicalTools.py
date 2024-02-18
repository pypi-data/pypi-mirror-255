"""Mechanical Calculation Tools
Notes
-----
The mechanical calculation tools module supports various temperature related methods for SFE.
"""

#############
## IMPORTS ##
#############

import numpy as np
from scipy.interpolate import interp1d


#################################################################
## Concrete strength and deformatoin properties in EN 1992-1-2 ##
#################################################################

def c_strength_retention_EC(fck,Temp,aggregates='sil'):
	""" obtain tabulated parameters for temperature dependant stress-strain relationships
	accord. EN 1992-1-2 Table 3.1 for NSC (pp. 20) and Table 6.1N for HSC (pp. 59)
	
	Parameters
	----------
	fck : float
		concrete characteristic compressive strength [MPa]
	
	Temp : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]
	
	aggregates : String
		'sil'  = Siliceous aggregates (default)
		'calc' = Calcareous aggregates
	
	Returns
	-------
	k_fc : float or np.array
		Strength retention factor for concrete compressive strength [-]
	
	Ec_1 : float or np.array
		net strain at peak compressive stress [-]
	
	Ec_u : float or np.array
		ultimate net strain [-]
	
	Example use
	-----------
	>>> import numpy as np
	>>> import magnelPy.SFE as sfe
	>>> fck = 50
	>>> Temp = 500
	>>> k_fc,e_c1,e_cu = sfe.MechanicalTools.c_strength_retention_EC(fck,Temp,aggregates='calc')
	"""
	
	# Eurocode 2 data
	T_list = np.insert(np.arange(300,1300,100),0,[20,50,100,200,250])
	if fck < 55: # EN 1992-1-2 Table 3.1
		k_fc_list = [1,1,1,0.95,0.9,0.85,0.75,0.6,0.45,0.3,0.15,0.08,0.04,0.01,0] if aggregates == 'sil' else [1,1,1,0.97,0.94,0.91,0.85,0.74,0.6,0.43,0.27,0.15,0.06,0.02,0] 
	else:
		# EN 1992-1-2 Table 6.1N describes strength reduction factors for HSC (C55/67 and up) in 3 different classes
		if fck < 70: # class 1 (recommended for C55/67 and C60/75)
			k_fc_list = [1,1,0.9,0.9,0.9,0.85,0.75,0.6,0.45,0.3,0.15,0.08,0.04,0.01,0] 
		elif fck < 90: #class 2 (recommended for C70/85 and C80/95)
			k_fc_list = [1,1,0.75,0.75,0.75,0.75,0.75,0.6,0.45,0.3,0.15,0.1125,0.075,0.0375,0]
		else: # class 3 (recommended for C90/105)
			k_fc_list = [1,1,0.75,0.7,0.675,0.65,0.45,0.3,0.25,0.2,0.15,0.08,0.04,0.01,0]
		
	e_c1_list = [0.0025,0.0030625,0.004,0.0055,0.00625,0.007,0.01,0.015,0.025,0.025,0.025,0.025,0.025,0.025,0.025] # EN 1992-1-2 Table 3.1, identical values for silicious and calcereous aggregates
	e_cu_list = np.insert(np.arange(0.0275,0.0501,0.0025),0,[0.02,0.0209375,0.0225,0.025,0.02625]) # EN 1992-1-2 Table 3.1, identical values for silicious and calcereous aggregates
	
	k_fc_data = interp1d(T_list,k_fc_list)
	e_c1_data = interp1d(T_list,e_c1_list)
	e_cu_data = interp1d(T_list,e_cu_list)
	
	k_fc = k_fc_data(Temp).round(10) # using .round(10) resolves issue with trailing digits
	e_c1 = e_c1_data(Temp).round(10)
	e_cu = e_cu_data(Temp).round(10) 
	
	return(k_fc,e_c1,e_cu)


def c_strength_retention_EC_tensile(T):
	""" concrete tensile strength reduction, accord. EN 1992-1-2 Figure 3.2 (pp. 22)
	
	Parameters
	----------	
	T : float or np.array
		(array of) Temperature in range 20 - 600 [°C] (extended beyond 600°C for numerical purposes)
	
	Returns
	-------
	k_fct : float or np.array
		Strength retention factor for concrete tensile strength [-]
	
	Example use
	-----------
	>>> TODO
	"""
	T = np.array(T).astype(float) # conversion to float, to counteract np.piecewise() for int inputs
	conds = [T < 100,(T>=100)&(T<600),T>=600]
	funcs = [1,lambda T:(600-T)/500,0]
	return np.piecewise(T, conds, funcs)


def c_thermal_strain_EC(temp,aggregates='sil'):
	""" returns the total thermal eleongation (thermal strain), with reference to the length at 20°C, accord. EN 1992-1-2 (pp. 26)
	
	Parameters
	----------	
	Temp : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]
	
	aggregates : String
		'sil'  = Siliceous aggregates (default)
		'calc' = Calcareous aggregates
	
	Returns
	-------
	Eps : float or np.array
		total thermal elongation [-]
		
	Example use
	-----------
	>>> import numpy as np
	>>> import magnelPy.SFE as sfe
	>>> Temp = np.arange(20,1101,20)
	>>> eps = sfe.ThermalTools.c_thermal_strain_EC(Temp,aggregates='calc')	
	"""
	
	out = -1.8e-4 + 9e-6*temp + 2.3e-11*temp**3 if aggregates=='sil' else -1.2e-4 + 6e-6*temp + 1.4e-11*temp**3
	out = np.clip(out,0,0.014) if aggregates=='sil' else np.clip(out,0,0.012) # clip off when max value is reached, in accordance with EN 1992-1-2
	return out


##############################################################
## Steel strength and deformatoin properties in EN 1992-1-2 ##
##############################################################

def s_strength_retention_EC(T,steeltype='hotrolled'):
	""" returns deterministic value of the strenght retention factor for steel properties at elevated temperatures
	according to EN 1992-1-2 (pp. 23)
	
	Parameters
	----------	
	T : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]
	
	Steeltype : String
		'hotrolled' (default)
		'coldworked'
	
	Returns
	-------
	k_fy : float or np.array
		Strength retention factor for steel maximum stress level [-]
		
	k_sp : float or np.array
		Strength retention factor for steel proportional limit [-]
		
	k_Es : float or np.array
		Strength retention factor for steel slope of the linear elastic range [-]
	"""
	T_list = np.array([20,100,200,300,400,500,600,700,800,900,1000,1100,1200])
	
	if steeltype == 'hotrolled':
		# EN 1992-1-2 - Table 3.2a (2004), note: identical to EN 1993-1-2:2005 - Table 3.1
		kfy_list = np.array([1,1,1,1,1,0.78,0.47,0.23,0.11,0.06,0.04,0.02,0.0])
		ksp_list = np.array([1,1,0.81,0.61,0.42,0.36,0.18,0.07,0.05,0.04,0.02,0.01,0.0]) # note: fs_p = fs_y up to 100°C -> linear ascending branch in stress-stain diagram
		kE_list = np.array([1,1,0.9,0.8,0.7,0.6,0.31,0.13,0.09,0.07,0.04,0.02,0.0])
	if steeltype == 'coldworked':
		# EN 1992-1-2 - Table 3.2a (2004)
		kfy_list = np.array([1,1,1,1,0.94,0.67,0.4,0.12,0.11,0.08,0.05,0.03,0.0])
		ksp_list = np.array([1,0.96,0.92,0.81,0.63,0.44,0.26,0.08,0.06,0.05,0.03,0.02,0.0])
		kE_list = np.array([1,1,0.87,0.72,0.56,0.4,0.24,0.08,0.06,0.05,0.03,0.02,0.0])
	kfy_interpol = interp1d(T_list,kfy_list)
	ksp_interpol = interp1d(T_list,ksp_list)
	kEs_interpol = interp1d(T_list,kE_list)
	
	return kfy_interpol(T),ksp_interpol(T), kEs_interpol(T)


def s_thermal_strain_EC(temp):
	""" returns the total thermal elongation (thermal strain), with reference to the length at 20°C
	accord. EN 1992-1-2 (pp. 28-29)
	
	Parameters
	----------	
	temp : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]
	
	Returns
	-------
	Eps : float or np.array
		total thermal elongation of steel [-]
	"""
	out = []
	for T in temp:
		if T <= 750: out.append(-2.416e-4 + T*1.2e-5 + T*T*0.4e-8)
		else:
			if T <= 860: out.append(11e-3)
			else: out.append(-6.2e-3 + T*2e-5)
	
	return out


##########################################################################
## Prestressing teel strength and deformatoin properties in EN 1992-1-2 ##
##########################################################################

def p_thermal_strain_EC(temp):
	""" returns the total thermal elongation (thermal strain), with reference to the length at 20°C
	accord. EN 1992-1-2 (pp. 28-29)
	
	Parameters
	----------	
	temp : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]
	
	Returns
	-------
	Eps : float or np.array
		total thermal elongation of prestressing steel [-]
	"""
	
	return -2.016e-4 + temp*1e-5 + temp*temp*0.4e-8


def p_strength_retention_EC(T, SteelClass='B'):
	""" returns deterministic value of the strenght retention factor for prestressing steel properties at elevated temperatures
	according to EN 1992-1-2 (pp. 25)
	
	Parameters
	----------	
	T : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]
		
	SteelClass : String
		accord. EN 1992-1-1 Table C.1 (pp. 205)
		'B' 5.0% Characteristic strain at maximum force (Default) 
		'A' 2.5% Characteristic strain at maximum force
	
	Returns
	-------
	k_fy : float or np.array
		Strength retention factor for prestressing steel maximum stress level [-]
		
	k_sp : float or np.array
		Strength retention factor for prestressing steel proportional limit [-]
		
	k_Ep : float or np.array
		Strength retention factor for prestressing steel slope of the linear elastic range [-]
	"""
	
	T_list = np.array([20,100,200,300,400,500,600,700,800,900])
	
	if SteelClass == 'B':
		# EN 1992-1-2 - Table 3.3 (2004)
		kfy_list = np.array([1,0.99,0.87,0.72,0.46,0.22,0.10,0.08,0.05,0.03])
	
	if SteelClass == 'A':
		# EN 1992-1-2 - Table 3.3 (2004)
		kfy_list = np.array([1,1,0.87,0.70,0.50,0.30,0.14,0.06,0.04,0.02])
		
	ksp_list = np.array([1,0.68,0.51,0.32,0.13,0.07,0.05,0.03,0.02,0.01]) # note: fs_p = fs_y at 20°C -> linear ascending branch in stress-stain diagram
	kEp_list = np.array([1,0.98,0.95,0.88,0.81,0.54,0.41,0.10,0.07,0.03])
	
	kfy_interpol = interp1d(T_list,kfy_list)
	ksp_interpol = interp1d(T_list,ksp_list)
	kEp_interpol = interp1d(T_list,kEp_list)
	
	return kfy_interpol(T),ksp_interpol(T), kEp_interpol(T)


#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":

	print("testing")