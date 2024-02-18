"""Test file for irrecoverable Abaqus material models
"""

###############
### IMPORTS ###
###############

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from magnelPy.Abaqus import MechanicalProperties
from magnelPy.Abaqus import ThermalProperties
from scipy.interpolate import interp1d

SW_test = 3


def track_Tmax(T_list):
	max_T = -1
	T_max_list = []
	
	for T in T_list:
		if T > max_T: max_T = T
		T_max_list.append(max_T)
	
	return(T_max_list)


def abaqus_interpolation(T_list,Tmax_list,df):
	
	T_rise_data = df.loc[df['T [°C]'] == df['Tmax [°C]']]
	T_fall_data = pd.concat([df.iloc[[0]],df.loc[df['T [°C]'] != df['Tmax [°C]']]])
	out = []
	
	print(T_fall_data)
	
	for T,Tmax in zip(T_list,Tmax_list):
		if T >= Tmax:
			out_data = interp1d(T_rise_data.iloc[:, 1],T_rise_data.iloc[:, 0])
			out.append(float(out_data(T)))
		if T < Tmax: 
			out_data = interp1d(T_fall_data.iloc[:, 2],T_fall_data.iloc[:, 0])
			out.append(float(out_data(Tmax)))
			
	return(out)


#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":
	
	# TEST 1: Concrete irrecoverable density
	if SW_test == 1:
		rho_data = ThermalProperties.c_density_EC_T_irr(np.arange(20,801,20),units='m')
		
		# simulate heating regime: 20°C -> 500°C -> 20°C
		T = np.concatenate((np.arange(20,501,20),np.arange(500,19,-20),np.arange(20,701,20)))
		Tmax = track_Tmax(T)
		dens = abaqus_interpolation(T,Tmax,rho_data)
		
		fig, ax1 = plt.subplots()
		ax2 = ax1.twinx()
		ax1.plot(dens,'r')
		ax2.plot(T)
		ax2.plot(Tmax,'m--')
		
		ax1.set_ylabel('Density')
		ax2.set_ylabel('Temperature [°C]')
		ax1.set_xlabel('Time')
	
	
	# TEST 2: Concrete irrecoverable conductivity
	if SW_test == 2:
		rho_data = ThermalProperties.c_conductivity_EC_T_irr(np.arange(20,801,20))
		
		# simulate heating regime: 20°C -> 500°C -> 20°C
		T = np.concatenate((np.arange(20,501,20),np.arange(500,19,-20),np.arange(20,701,20)))
		Tmax = track_Tmax(T)
		k = abaqus_interpolation(T,Tmax,rho_data)
		
		fig, ax1 = plt.subplots()
		ax2 = ax1.twinx()
		ax1.plot(k,'r')
		ax2.plot(T)
		ax2.plot(Tmax,'m--')
		
		ax1.set_ylabel('Conductivity')
		ax2.set_ylabel('Temperature [°C]')
		ax1.set_xlabel('Time')
	
	
	# TEST 3: Concrete irrecoverable specific heat
	if SW_test == 3:
		k_data = ThermalProperties.c_specific_heat_EC_T_irr(np.arange(20,801,5),moisture=1,units='m')
		
		# simulate heating regime: 20°C -> 500°C -> 20°C
		T = np.concatenate((np.arange(20,101,5),np.arange(110,19,-5),np.arange(20,501,5),np.arange(500,19,-5)))
		Tmax = track_Tmax(T)
		cp = abaqus_interpolation(T,Tmax,k_data)
		
		fig, ax1 = plt.subplots()
		ax2 = ax1.twinx()
		ax1.plot(cp,'r',label='specific heat')
		ax2.plot(T,label='Temperature')
		ax2.plot(Tmax,'m--',label='Max temperature')
		
		ax1.set_ylabel('Conductivity')
		ax2.set_ylabel('Temperature [°C]')
		ax1.set_xlabel('Time')
		ax1.set_ylim(800,2400)
		ax2.set_ylim(0,800)
		
		ax1.legend()
		ax2.legend()
	
	# TEST 4: Concrete irrecoverable thermal expansion
	if SW_test == 4:
		a_data = MechanicalProperties.c_thermal_expansion_coef_EC_irr(delta=10)
		
		# simulate heating regime: 20°C -> 500°C -> 20°C
		T = np.concatenate((np.arange(20,401,5),np.arange(400,19,-5)))
		Tmax = track_Tmax(T)
		a = abaqus_interpolation(T,Tmax,a_data)
		
		fig, ax1 = plt.subplots()
		ax2 = ax1.twinx()
		ax1.plot(a,'r',label='specific heat')
		ax2.plot(T,label='Temperature')
		ax2.plot(Tmax,'m--',label='Max temperature')
		
		ax1.set_ylabel('Conductivity')
		ax2.set_ylabel('Temperature [°C]')
		ax1.set_xlabel('Time')
		ax1.set_ylim(800,2400)
		ax2.set_ylim(0,800)
		
		ax1.legend()
		ax2.legend() 
	
	print('done')
		