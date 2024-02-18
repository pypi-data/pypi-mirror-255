"""Tools for creation of Abaqus material models for heat transfer analysis
Notes
-----
The thermal properties tools module supports temperature dependant material definitions for concrete, steel and prestressing steel
"""

###############
### IMPORTS ###
###############

import numpy as np
import pandas as pd
from magnelPy.SFE import ThermalTools
from scipy.interpolate import interp1d



#################################################
### Concrete irrecoverable thermal properties ###
#################################################

def c_density_EC_T_irr(T,rho=2400,units='mm'):
	""" concrete density at elevated temperature (influenced by water loss), 
	accord. EN 1992-1-2 (pp. 28)
	
	Parameters
	----------
	T : np.array
		array of Temperatures in range 20 - 1200 [°C]
	
	rho : float (optional)
		Concrete density at room temperature [kg/m3] (Default: 2400)
		
	units : String (optional)
		'mm' = outputs results in SI-mm units (default)
		'm'  = outputs results in SI units
	
	Returns
	-------
	out : pd.DataFrame
		Concrete density data in 3 columns for Abaqus input	| density | Temperature [°C] | Max. temperature [°C] |
	"""
	
	T_list = [20,115,200,400,1200]
	k_rho_list = [1,1,0.98,0.95,0.88] 
	k_rho_data = interp1d(T_list,k_rho_list)
	k_rho = k_rho_data(T)
	
	rho_c = k_rho*rho
	Tmax = np.append(T,T[1:])
	T = np.append(np.full((len(T)-1,),20),T)
	rho_c = np.append(rho_c,rho_c[1:])
	
	if units == 'm':
		out = pd.concat([pd.DataFrame(rho_c),pd.DataFrame(T),pd.DataFrame(Tmax)],axis=1)
		out.columns = ['rho [kg/m3]','T [°C]','Tmax [°C]']
	if units == 'mm':
		out = pd.concat([pd.DataFrame(rho_c*1e-12),pd.DataFrame(T),pd.DataFrame(Tmax)],axis=1)
		out.columns = ['rho [ton/mm3]','T [°C]','Tmax [°C]']
	
	return out


def c_conductivity_EC_T_irr(T,limit='lower',units='mm'):
	""" concrete thermal conductivity at elevated temperature
	accord. EN 1992-1-2 (pp. 28)
	
	Parameters
	----------
	T : np.array
		(array of) temperatures in range 20 - 1200 [°C]
	
	limit : String (optional)
		'lower' = Siliceous aggregates (default)
		'upper' = Calcareous aggregates
	
	units : String (optional)
		'mm' = outputs results in SI-mm units (default)
		'm'  = outputs results in SI units
	
	Returns
	-------
	out : pd.DataFrame
		Concrete conductivity data in 3 columns for Abaqus input	| conductivity | Temperature [°C] | Max. temperature [°C] |
	"""
	
	if limit == 'lower': lambda_c =  1.36 - 0.1360*(T/100) + 0.0057*(T/100)*(T/100)
	if limit == 'upper': lambda_c =  2.00 - 0.2451*(T/100) + 0.0107*(T/100)*(T/100)
	
	Tmax = np.append(T,T[1:])
	T = np.append(np.full((len(T)-1,),20),T)
	lambda_c = np.append(lambda_c,lambda_c[1:])
	
	out = pd.concat([pd.DataFrame(lambda_c),pd.DataFrame(T),pd.DataFrame(Tmax)],axis=1)
	if units == 'm': out.columns = ['k [W/m K]','T [°C]','Tmax [°C]']
	if units == 'mm': out.columns = ['k [mW/mm K]','T [°C]','Tmax [°C]']
		
	return out


def c_specific_heat_EC_T_irr(T, moisture=3,units='mm'):
	""" concrete specific heat at elevated temperature
	accord. EN 1992-1-2 (pp. 28)
	
	Parameters
	----------
	T : np.array
		(array of) temperatures in range 20 - 1200 [°C]
	
	moisture : float (percentage)
		moisture content, percentage of concrete weight [w_%] in range 0 - 3 
	
	units : String (optional)
		'mm' = outputs results in SI-mm units (default)
		'm'  = outputs results in SI units
	
	Returns
	-------
	out : pd.DataFrame
		Concrete conductivity data in 3 columns for Abaqus input	| conductivity | Temperature [°C] | Max. temperature [°C] |
	"""
	
	cp_data = ThermalTools.c_specific_heat_EC_T(T,moisture=moisture)
	cp_data_cooling = ThermalTools.c_specific_heat_EC_T(T,moisture=0)
	
	Tmax = np.append(T,T[1:])
	T = np.append(np.full((len(T)-1,),20),T)
	cp = np.append(cp_data_cooling,cp_data[1:])
	
	
	if units == 'm': 
		out = pd.concat([pd.DataFrame(cp),pd.DataFrame(T),pd.DataFrame(Tmax)],axis=1)
		out.columns = ['cp [J/kg K]','T [°C]','Tmax [°C]']
	if units == 'mm': 
		out = pd.concat([pd.DataFrame(cp*1e6),pd.DataFrame(T),pd.DataFrame(Tmax)],axis=1)
		out.columns = ['cp [mJ/ton K]','T [°C]','Tmax [°C]']
		
	return out

#################################################
### Steel irrecoverable thermal properties ###
#################################################

# TODO


#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":
	
	# TEST 1: Irreversible concrete density
	T = np.linspace(20,500,25)
	print(c_specific_heat_EC_T_irr(T))