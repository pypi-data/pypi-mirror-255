"""Master file for automatic creation of Abaqus material models for thermal-stress analysis
"""

###############
### IMPORTS ###
###############

import numpy as np
import pandas as pd
from magnelPy import admin
from magnelPy.SFE import ThermalTools
from magnelPy.Abaqus import MechanicalProperties
from magnelPy.Abaqus import ThermalProperties



##########################
### THERMAL PROPERTIES ###
##########################
def abaqus_concrete_properties_th(rho=2400,moisture=0,limit='lower',units='mm',irreversible=False):
	""" Create inputs for temperature dependant concrete thermal properties 
	(density, specific heat and conductivity) required in an Abaqus heat-transfer analysis
	
	Parameters
	----------
	rho : float (optional)
		Concrete density at room temperature [kg/m3] (Default: 2400)
	
	moisture : float/precentage (optional)
		moisture content, percentage of concrete weight [w_%] in range 0 - 3
	
	limit : String (optional)
		'lower' = Siliceous aggregates (default)
		'upper' = Calcareous aggregates
	
	units : String (optional)
		'mm' = outputs results in SI-mm units (default)
		'm'  = outputs results in SI units
	
	irreversible : boolean (optional)
		False = thermal properties in the cooling phase are fully recovered (default)
		True =  thermal properties in the cooling phase are irreversible, requires Abaqus model with subroutine
	
	Returns
	-------
	ABQ_input_concrete_th : .xls file
		 Results are written to workdir
	"""
	
	T_list = np.arange(20,1101,5) # [°C]
	
	if irreversible == False:
		c_density = ThermalTools.c_density_EC_T(T_list,rho) # [kg/m3]
		c_conductivity = ThermalTools.c_conductivity_EC_T(T_list, limit=limit) # [W/m K]
		c_specific_heat = ThermalTools.c_specific_heat_EC_T(T_list,moisture) # [J/kg K]
		
		if units == 'm':
			out_c_density = pd.concat([pd.DataFrame(c_density),pd.DataFrame(T_list)],axis=1)
			out_c_conductivity = pd.concat([pd.DataFrame(c_conductivity),pd.DataFrame(T_list)],axis=1)
			out_c_specific_heat = pd.concat([pd.DataFrame(c_specific_heat),pd.DataFrame(T_list)],axis=1)
			
			out_c_density.columns = ['rho [kg/m3]','T [°C]']
			out_c_conductivity.columns = ['k [W/m K]','T [°C]']
			out_c_specific_heat.columns = ['cp [J/kg K]','T [°C]']
			
		if units == 'mm':
			out_c_density = pd.concat([pd.DataFrame(c_density*1e-12),pd.DataFrame(T_list)],axis=1)
			out_c_conductivity = pd.concat([pd.DataFrame(c_conductivity),pd.DataFrame(T_list)],axis=1)
			out_c_specific_heat = pd.concat([pd.DataFrame(c_specific_heat*1e6),pd.DataFrame(T_list)],axis=1)
			out_c_density.columns = ['rho [ton/mm3]','T [°C]']
			out_c_conductivity.columns = ['k [mW/mm K]','T [°C]']
			out_c_specific_heat.columns = ['cp [mJ/ton K]','T [°C]']
		
		out_list = [out_c_density,out_c_conductivity,out_c_specific_heat]
		sheet_list = ['c density','c conductivity','c specific_heat']
	
	if irreversible == True:
		out_c_density = ThermalProperties.c_density_EC_T_irr(T_list,rho=rho,units=units)
		out_c_conductivity = ThermalProperties.c_conductivity_EC_T_irr(T_list,limit=limit,units=units)
		out_c_specific_heat = ThermalProperties.c_specific_heat_EC_T_irr(T_list,moisture=moisture,units=units)
		
		out_list = [out_c_density,out_c_conductivity,out_c_specific_heat]
		sheet_list = ['c density','c_conductivity','c_specific_heat']
	
	filename = 'output/ABQ_input_concrete_th'
	admin.dfList_writeToExcel(out_list,filename,sheet_list)
	print('writing Abaqus heat transfer inputs for concrete (units in {})'.format(units))


def abaqus_steel_properties_th(rho_s=7850,units='mm'):
	""" Create inputs for temperature dependant steel thermal properties 
	(density, specific heat and conductivity) required in an Abaqus heat-transfer analysis
	
	Parameters
	----------
	rho : float (optional)
		Steel density at room temperature [kg/m3] (Default: 7850)
	
	units : String (optional)
		'mm' = outputs results in SI-mm units (default)
		'm'  = outputs results in SI units
	
	Returns
	-------
	ABQ_input_concrete_th : .xls file
		 Results are written to workdir
	"""
	
	T_list = np.append([20],np.arange(50,1201,50)) # [°C]
	
	s_conductivity = ThermalTools.s_conductivity_EC_T(T_list) # [W/m K]
	s_specific_heat = ThermalTools.s_specific_heat_EC_T(T_list) # [J/kg K]
	
	if units == 'm':
		out_s_density = pd.DataFrame([rho_s])
		out_s_conductivity = pd.concat([pd.DataFrame(s_conductivity),pd.DataFrame(T_list)],axis=1)
		out_s_specific_heat = pd.concat([pd.DataFrame(s_specific_heat),pd.DataFrame(T_list)],axis=1)
		
		out_s_density.columns = ['rho [kg/m3]']
		out_s_conductivity.columns = ['k [W/m K]','T [°C]']
		out_s_specific_heat.columns = ['k [J/kg K]','T [°C]']
	
	if units == 'mm':
		out_s_density = pd.DataFrame([rho_s*1e-12])
		out_s_conductivity = pd.concat([pd.DataFrame(s_conductivity),pd.DataFrame(T_list)],axis=1)
		out_s_specific_heat = pd.concat([pd.DataFrame(s_specific_heat*1e6),pd.DataFrame(T_list)],axis=1)
		
		out_s_density.columns = ['rho [ton/mm3]']	
		out_s_conductivity.columns = ['k [mW/mm K]','T [°C]']
		out_s_specific_heat.columns = ['k [mJ/ton K]','T [°C]']
	
	filename = 'output/ABQ_input_steel_th'
	out_list = [out_s_density,out_s_conductivity,out_s_specific_heat]
	sheet_list = ['s density','s conductivity','s specific_heat']
	admin.dfList_writeToExcel(out_list,filename,sheet_list)
	print('writing Abaqus heat transfer inputs for steel (units in {})'.format(units))


#############################
### MECHANICAL PROPERTIES ###
#############################

def abaqus_concrete_properties_mech(fcm,fct=-1,aggregates='sil',irreversible=False):
	""" Create inputs for temperature dependant concrete mechanical properties 
	(stress-strain curves, Young's modulus, thermal expansion) required in an Abaqus thermal-stress analysis
	
	Parameters
	----------
	fcm : float
		Concrete compressive strength at 20°C [MPa]
	
	fct : float (optional)
		Concrete tensile strength at 20°C [MPa] (default = -1: fct is calculated based on fib Model Code 2010)
		
	aggregates : String (optional)
		'sil'  = Siliceous aggregates (default)
		'calc' = Calcareous aggregates
	
	irreversible : boolean (optional) NOT IMPLEMENTED
		False = mechanical properties in the cooling phase are fully recovered (default)
		True =  mechanical properties in the cooling phase are irreversible, requires Abaqus model with subroutine
	
	Returns
	-------
	ABQ_input_concrete_mech : .xls file
		 Results are written to workdir
	"""
	
	if irreversible == False:
		compressive_conc, elast_conc = MechanicalProperties.c_stress_strain_compression_T(fcm,aggregates=aggregates) # concrete compressive stress strain data
		tensile_conc = MechanicalProperties.c_stress_displacement_tension_T(fcm, fct = fct) # concrete tensile stress displacement data
		cet_conc = MechanicalProperties.c_thermal_expansion_coef_EC(delta=20) # concrete coefcient of thermal expansion
		aux = MechanicalProperties.Abaqus_CDP_parameters()
	
	if irreversible == True:
		print('not fully implemented! For now only irrecoverable thermal strain')
		cet_conc = MechanicalProperties.c_thermal_expansion_coef_EC(delta=20) # concrete coefcient of thermal expansion
	
	# generate output
	filename = 'output/ABQ_input_concrete_mech'
	out_list = [elast_conc,compressive_conc,tensile_conc,cet_conc,aux]
	sheet_list = ['c elastic','c compressive','c tensile','c thermal expansion','CDP parameters']
	admin.dfList_writeToExcel(out_list,filename,sheet_list)
	print('written Abaqus inputs for fc = {} MPa to {}.xlsx'.format(fcm,filename))


def abaqus_steel_properties_mech(fy=500,E=210000,irreversible=False):
	""" Create inputs for temperature dependant steel mechanical properties 
	(stress-strain curves, Young's modulus, thermal expansion) required in an Abaqus thermal-stress analysis
	
	Parameters
	----------
	fy : float (optional)
		Steel yield strength at 20°C [MPa]
	
	E : float (optional)
		Steel Young's modulus at 20°C [MPa]
	
	irreversible : boolean (optional) NOT IMPLEMENTED
		False = mechanical properties in the cooling phase are fully recovered (default)
		True =  mechanical properties in the cooling phase are irreversible, requires Abaqus model with subroutine
	
	Returns
	-------
	ABQ_input_concrete_mech : .xls file
		 Results are written to workdir
	"""
	
	if irreversible == False:
		stress_strain_steel, elast_steel = MechanicalProperties.s_stress_strain_EC_T(fy,E)
		cet_steel = MechanicalProperties.s_thermal_expansion_coef_EC()
	
	if irreversible == True:
		print('not implemented!')
	
	# generate output
	filename = 'output/ABQ_input_steel_mech'
	out_list = [stress_strain_steel, elast_steel,cet_steel]
	sheet_list = ['s stress-strain','s elastic','s thermal expansion']
	admin.dfList_writeToExcel(out_list,filename,sheet_list)
	print('written Abaqus inputs for fy = {} MPa to {}.xlsx'.format(fy,filename))


def abaqus_prestressingsteel_properties_mech(fp=1860,Ep=195000,irreversible=False):
	""" Create inputs for temperature dependant prestressing steel mechanical properties 
	(stress-strain curves, Young's modulus, thermal expansion) required in an Abaqus thermal-stress analysis
	
	Parameters
	----------
	fp : float (optional)
		Steel strength at 20°C [MPa]
	
	Ep : float (optional)
		Steel Young's modulus at 20°C [MPa]
	
	irreversible : boolean (optional) NOT IMPLEMENTED
		False = mechanical properties in the cooling phase are fully recovered (default)
		True =  mechanical properties in the cooling phase are irreversible, requires Abaqus model with subroutine
	
	Returns
	-------
	ABQ_input_concrete_mech : .xls file
		 Results are written to workdir
	"""
	
	if irreversible == False:
		stress_strain_p_steel, elast_p_steel = MechanicalProperties.p_stress_strain_EC_T(fp,Ep,softening=True)
		cet_p_steel = MechanicalProperties.p_thermal_expansion_coef_EC()
	
	if irreversible == True:
		print('not implemented!')
	
	# generate output
	filename = 'output/ABQ_input_prestressingsteel_mech'
	out_list = [stress_strain_p_steel, elast_p_steel,cet_p_steel]
	sheet_list = ['p elastic','p stress-strain','p thermal expansion']
	admin.dfList_writeToExcel(out_list,filename,sheet_list)
	print('written Abaqus inputs for fp = {} MPa to {}.xlsx'.format(fp,filename))


#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":
	
	# TEST 1: Concrete mechanical properties
	abaqus_concrete_properties_th(irreversible=False,moisture=2)
	
	# TEST 2: Concrete mechanical properties
	abaqus_steel_properties_th()
	
	# TEST 3: Concrete mechanical properties
	fcm = 50 # [MPa]
	abaqus_concrete_properties_mech(fcm)
	
	# TEST 4: Steel mechanical properties
	fy = 500 # [MPa]
	E = 210000 # [MPa]
	abaqus_steel_properties_mech(fy,E)
	
	# TEST 5: Prestressing steel mechanical properties
	fp = 1860 # [MPa]
	Ep = 195000 # [MPa]
	abaqus_prestressingsteel_properties_mech(fp,Ep)