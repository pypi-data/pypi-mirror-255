"""Tools for creation of Abaqus material models for thermal-stress analysis
Notes
-----
The mechanical properties tools module supports temperature dependant material definitions for concrete, steel and prestressing steel
"""

###############
### IMPORTS ###
###############

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from magnelPy.admin import df_readFromExcel
from magnelPy.SFE import MechanicalTools


####################################################
### Concrete strength and deformation properties ###
####################################################

def c_stress_strain_compression_T(fc_k,aggregates='sil',return_T_list=False):
	""" obtain datapoints for concrete stress-strain relationship at elevated temperatures, for direct input in Abaqus, in range 20 - 1100 °C
	accord. EN 1992-1-2 (pp. 20)
	
	Parameters
	----------
	fc_k : float
		concrete characteristic compressive strength (at 20°C) [MPa]
	
	aggregates : String (optional)
		'sil'  = Siliceous aggregates (default)
		'calc' = Calcareous aggregates
	
	return_T_list : boolean (optional)
		self explanatory
	
	Returns
	-------
	s_out : pd.DataFrame
		Stress-(plastic) strain data in 3 columns for Abaqus input	| stress [MPa] | pl. strain [-] | Temperature [°C] |
	
	e_out : pd.DataFrame
		Elasticity data in 3 columns for Abaqus input	| Young's mod [MPa] | Poisson rat. [-] | Temperature [°C] |
		
	Example use
	-----------
	>>> TODO
	"""
	
	T_list = [20,50,75,100,200,300,400,500,600,700,800,900,1000,1100] # np.arange(20,1001,100)
	k_list,e_c1_list,e_cu_list = MechanicalTools.c_strength_retention_EC(fc_k,T_list,aggregates)
	
	sig_data=[]; ep_data=[]; E_list=[]
	
	# generate data points for each temperature in T_list
	for T,k,e_c1,e_cu in zip(T_list,k_list,e_c1_list,e_cu_list):
		fc_k_T = fc_k*k
		e_list = np.concatenate((np.array([0,0.5,0.6,0.7,0.8,0.9,0.95])*e_c1,np.array([0,0.02,0.04,0.06,0.08,0.1,0.15,0.2,0.3,0.4,0.6,0.8,1])*(e_cu - e_c1) + e_c1))
		s_list = (3*e_list*fc_k_T)/(e_c1*(2+((e_list/e_c1)**3))) # see figure 3.1, pp. 21
		E = s_list[1]/e_list[1] # tangent modulus [MPa], needed to express plastic strain in abaqus
		E_list.append(E)
		e_el_list = s_list/E # elastic strain
		e_pl_list = e_list - e_el_list # plastic strain
		e_pl_list[1] = 0 # correct cases where e_pl is very close to 0
		
		sig_data.append(np.delete(s_list,0)) # removing first element in list using np.delete() since first line in Abaqus table cannot be [0,0]
		ep_data.append(np.delete(e_pl_list,0))
	
	# repackage stress strain data for output
	sig_out = np.array(sig_data).flatten() # [MPa]
	ep_out = np.array(ep_data).flatten() # [-]
	T_out = np.repeat(T_list,len(e_list)-1) # [°C]
	
	s_out = pd.concat([pd.DataFrame(sig_out),pd.DataFrame(ep_out),pd.DataFrame(T_out)],axis=1)
	s_out.columns = ['s [MPa]','e_pl [-]','T [°C]']
	
	# repackage elasticity data for output
	E_out = np.array(E_list)
	pois_out = np.ones(len(T_list))*0.2
	
	e_out = pd.concat([pd.DataFrame(E_out),pd.DataFrame(pois_out),pd.DataFrame(T_list)],axis=1)
	e_out.columns = ['E [MPa]','v [-]','T [°C]']
	
	if return_T_list:
		return s_out, e_out, T_list
	else:
		return s_out, e_out


def c_stress_displacement_tension_T(fc, fct = -1,return_T_list=False):
	""" obtain datapoints for concrete stress-displacement relationship at elevated temperatures, for direct input in Abaqus, in range 20 - 1100 °C
	accord. EN 1992-1-2 (pp. 22) and fib MC 2010 (pp. 130)
	GF constant with increasing temperature
	
	Parameters
	----------
	fc : float
		concrete compressive strength [MPa]
	fct : float (optional)
		concrete tensile strength [MPa]
		when fct = -1, fct is calculated accoring to the fib model code 2010
	
	Returns
	-------
	out : pd.DataFrame
		Dataframe with 3 columns for Abaqus input	| stress [MPa] | displ. [mm] | Temperature [°C] | 
	"""
	if fct == -1:
		fct = c_tensile_strength_fib(fc) # [MPa]
	
	GF = c_fracture_energy_fib(fc)*0.001 # [N/m] -> [N/mm]
	
	T_list = [20,100,200,300,400,500,600,700,800,900,1000,1100]
	k_list = MechanicalTools.c_strength_retention_EC_tensile(T_list)
	
	s_data=[]; dist_data=[]
	
	# generate data points for each temperature in T_list
	for T,k in zip(T_list,k_list):
		fct_k_T = fct*k if k>0 else fct*0.1
		s_list = np.array([1,0.2,0.05])*fct_k_T # value 0.01 fct_k is used since Abaqus only allows non-zero tensile strenghts
		
		# post-peak crack opening at stress = 0.2*fctm and stress = 0
		w1 = GF/fct_k_T # [N/mm]/[N/mm²] = [mm]
		wc = 5*w1 # crack opening [mm]
		w_list = [0,w1,wc]
		
		s_data.append(s_list)
		dist_data.append(w_list)
	
	# repackage data for output
	s_out = np.array(s_data).flatten()
	w_out = np.array(dist_data).flatten()
	T_out = np.repeat(T_list,3)
	
	out = pd.concat([pd.DataFrame(s_out),pd.DataFrame(w_out),pd.DataFrame(T_out)],axis=1)
	out.columns = ['s [MPa]','w [mm]','T [°C]']
	
	out = regularize_fct(out,T_list)
	
	if return_T_list:
		return out, T_list
	else:
		return out


def c_thermal_expansion_coef_EC(aggregates='sil',delta = 20):
	""" returns a table coefcient of thermal expansion (CET) for concrete, with reference to the length at 20°C, for direct input in Abaqus
	accord. EN 1992-1-2 (pp. 26)
	Note: in abaqus thermal strains are defined as total expansion from a reference temperature
	See abaqus manual: http://dsk.ippt.pan.pl/docs/abaqus/v6.13/books/usb/default.htm?startat=pt05ch26s01abm52.html
	
	Parameters
	----------	
	aggregates : String
		'sil'  = Siliceous aggregates (default)
		'calc' = Calcareous aggregates
	
	delta : float
		interval between temperature points
	
	Returns
	-------
	out : pd.DataFrame
		Dataframe with 2 columns for Abaqus input	 | CET [-] | Temperature [°C] | 
	"""
	
	if delta > 20: delta = 20
	
	T_list = np.arange(20,1101,delta)
	e_th = MechanicalTools.c_thermal_strain_EC(T_list)
	e_th[0]=0 # set first value equal to 0, EC2 analytical expression is exactly non-zero at 20°C
	
	cet = np.zeros(len(T_list))
	for i in range(0,len(T_list)):
		if i>0:
			cet[i]=(e_th[i]-e_th[0])/(T_list[i]-20)
	
	out = pd.concat([pd.DataFrame(cet),pd.DataFrame(T_list)],axis=1)
	out.columns = ['CET [-]','T [°C]']
	
	return out

def c_thermal_expansion_coef_EC_irr(aggregates='sil'):
	""" returns a table coefcient of thermal expansion (CET) for concrete, with reference to the length at 20°C, for direct input in Abaqus
	accord. EN 1992-1-2 (pp. 26)
	Note: in abaqus thermal strains are defined as total expansion from a reference temperature
	See abaqus manual: http://dsk.ippt.pan.pl/docs/abaqus/v6.13/books/usb/default.htm?startat=pt05ch26s01abm52.html
	Irrecoverable properties based on: Kabala, 2019 (PhD thesis) Figure 3.2
	
	Parameters
	----------	
	aggregates : String
		'sil'  = Siliceous aggregates (default)
		'calc' = Calcareous aggregates
	
	Returns
	-------
	out : pd.DataFrame
		Concrete thermal expansion data in 3 columns for Abaqus input	| exp coef | Temperature [°C] | Max. temperature [°C] |
	"""
	
	# !!! Hardcoded import from excel file, to be coded later !!!
	return df_readFromExcel('input\concrete_irr_thermal_expansion.xlsx','Abaqus')['Abaqus'].reset_index()


def Abaqus_CDP_parameters():
	""" Generates """
	dilation_angle = [38,38,38] # default value
	eccentricity = [0.1,0.1,0.1] # default value
	fb0fc0 = [1.16,1.3,1.6]
	K = [0.666,0.666,0.666] # default value
	viscosity = [0,0,0]
	T_list = [20,300,700]
	
	out = pd.concat([pd.DataFrame(dilation_angle),pd.DataFrame(eccentricity),pd.DataFrame(fb0fc0),pd.DataFrame(K),pd.DataFrame(viscosity),pd.DataFrame(T_list)],axis=1)
	out.columns = ['dilat.','ecc.','fb/fc','K','visc.','T']
	return out


#################################################
### Steel strength and deformatoin properties ###
#################################################
	
def s_stress_strain_EC_T(fy,Es):
	""" obtain datapoints for steel stress-strain relationship at elevated temperatures, for direct input in Abaqus, in range 20 - 1100 °C
	accord. EN 1992-1-2 (pp. 23)
	
	Note: softening is not yet included
	
	Parameters
	----------
	fy : float
		steel tensile strength (at 20°C) [MPa]
	
	Es : float
		slope of the linear elastic range [MPa]
	
	Returns
	-------
	s_out : pd.DataFrame
		Stress-strain data in 3 columns for Abaqus input	| stress [MPa] | pl. strain [-] | Temperature [°C] |
	
	e_out : pd.DataFrame
		Elasticity data in 3 columns for Abaqus input	| Young's mod [MPa] | Poisson rat. [-] | Temperature [°C] |
	"""
	
	n = 10 # number of data points in ascending branch (min. 5 recommended)
	n2 = 50
	
	T_list = np.array([20,100,200,300,400,500,600,700,800,900,1000,1100])
	kfy_list, ksp_list, kE_list = MechanicalTools.s_strength_retention_EC(T_list)
	
	sig_data=[]; ep_data=[]
	
	# fixed strain values see figure 3.3, pp. 23
	e_sy = 0.02 # [-]
	e_st = 0.15 # [-]
	e_su = 0.20 # [-]
	
	fy_T_list = fy*kfy_list # [MPa] reduced yield strength
	fsp_T_list = fy*ksp_list # [MPa] proportional limit fsp
	E_T_list = Es*kE_list # [MPa] (reduced) slope of the linear elastic range
	e_sp_list = fsp_T_list/E_T_list # [-] total strain at proportional limit fsp
	
	c_list = ((fy_T_list - fsp_T_list)**2)/(E_T_list*(e_sy-e_sp_list) - 2*(fy_T_list - fsp_T_list))
	a_list = np.sqrt((e_sy - e_sp_list)*(e_sy - e_sp_list + c_list/E_T_list))
	b_list = np.sqrt(c_list*c_list + c_list*(e_sy - e_sp_list)*E_T_list)
	
	# generate data points for each temperature in T_list
	for T,a,b,c,fyt,f_sp,e_sp,E in zip(T_list,a_list,b_list,c_list,fy_T_list,fsp_T_list,e_sp_list,E_T_list):
		e_list = arangeBias(e_sp,e_sy,n+1,10)
		s_list = f_sp - c + (b/a)*np.sqrt((a**2 - (e_sy - e_list)**2))		
		
		e_el_list = s_list/E # elastic strain
		e_pl_list = e_list - e_el_list # plastic strain
		e_pl_list[0] = 0
		
		s_list = np.append(s_list,[fyt,5,5])
		e_pl_list = np.append(e_pl_list,[e_st - fyt/E,e_su-5/E,0.21])
		
		s_list,e_pl_list = regalurize_fp(s_list,e_pl_list,n=n2)
		
		sig_data.append(s_list)
		ep_data.append(e_pl_list)
	
	# repackage stress strain data for output
	sig_out = np.array(sig_data).flatten() # [MPa]
	ep_out = np.array(ep_data).flatten() # [-]
	T_out = np.repeat(T_list,n2) # [°C]
	
	s_out = pd.concat([pd.DataFrame(sig_out),pd.DataFrame(ep_out),pd.DataFrame(T_out)],axis=1)
	s_out.columns = ['s [MPa]','e_pl [-]','T [°C]']
	
	# repackage elasticity data for output
	E_out = np.array(E_T_list)
	pois_out = np.ones(T_list.size)*0.3
	
	e_out = pd.concat([pd.DataFrame(E_out),pd.DataFrame(pois_out),pd.DataFrame(T_list)],axis=1)
	e_out.columns = ['E [MPa]','v [-]','T [°C]']

	return s_out, e_out


def s_thermal_expansion_coef_EC():
	""" returns a table coefcient of thermal expansion (CET) for reinforcing steel, with reference to the length at 20°C, for direct input in Abaqus
	accord. EN 1992-1-2 (pp. 29)
	Note: in abaqus thermal strains are defined as total expansion from a reference temperature
	See abaqus manual: http://dsk.ippt.pan.pl/docs/abaqus/v6.13/books/usb/default.htm?startat=pt05ch26s01abm52.html
	
	Returns
	-------
	out : pd.DataFrame
		Dataframe with 2 columns for Abaqus input	 | CET [-] | Temperature [°C] | 
	"""
	
	T_list = np.arange(20,1101,1)
	e_th = MechanicalTools.s_thermal_strain_EC(T_list)
	e_th[0]=0 # set first value equal to 0, EC2 analytical expression is exactly non-zero at 20°C
	
	cet = np.zeros(len(T_list))
	for i in range(0,len(T_list)):
		if i>0:
			cet[i]=(e_th[i]-e_th[0])/(T_list[i]-20)
	
	out = pd.concat([pd.DataFrame(cet),pd.DataFrame(T_list)],axis=1)
	out.columns = ['CET [-]','T [°C]']
	
	return out


##############################################################
### Prestressing steel strength and deformatoin properties ###
##############################################################

def p_stress_strain_EC_T(fp,Ep,softening=False,return_T_list=False):
	""" obtain datapoints for concrete stress-strain relationship at elevated temperatures, for direct input in Abaqus, in range 20 - 1100 °C
	accord. EN 1992-1-2 (pp. 23)
	
	Parameters
	----------
	fp : float
		prestressing steel tensile strength (at 20°C) [MPa]
	
	Ep : float
		slope of the linear elastic range [MPa]

	Returns
	-------
	s_out : pd.DataFrame
		Stress-strain data in 3 columns for Abaqus input	| stress [MPa] | pl. strain [-] | Temperature [°C] |
	
	e_out : pd.DataFrame
		Elasticity data in 3 columns for Abaqus input	| Young's mod [MPa] | Poisson rat. [-] | Temperature [°C] |
	"""
	
	n = 10 # number of data points in ascending branch (min. 5 recommended)
	n2 = 50 # number of regularized points
	
	T_list = np.array([20,100,200,300,400,500,600,700,800,900])
	kfy_list, ksp_list, kEp_list = MechanicalTools.p_strength_retention_EC(T_list)
	beta = 1 # [-] 
	
	sig_data=[]; ep_data=[]
	
	# fixed strain values see figure 3.3, pp. 23
	e_py = 0.02 # [-]
	e_pt = 0.05 # [-]
	e_pu = 0.1 # [-] 
	
	fy_T_list = fp*kfy_list*beta # [MPa] reduced yield strength
	fsp_T_list = fp*ksp_list*beta # [MPa] proportional limit fsp
	E_T_list = Ep*kEp_list # [MPa] (reduced) slope of the linear elastic range
	e_sp_list = fsp_T_list/E_T_list # [-] total strain at proportional limit fsp
	
	c_list = ((fy_T_list - fsp_T_list)**2)/(E_T_list*(e_py-e_sp_list) - 2*(fy_T_list - fsp_T_list))
	a_list = np.sqrt((e_py - e_sp_list)*(e_py - e_sp_list + c_list/E_T_list))
	b_list = np.sqrt(c_list*c_list + c_list*(e_py - e_sp_list)*E_T_list)
	
	# generate data points for each temperature in T_list
	for T,a,b,c,fy_T,f_sp,e_sp,E in zip(T_list,a_list,b_list,c_list,fy_T_list,fsp_T_list,e_sp_list,E_T_list):
		e_list = arangeBias(e_sp,e_py,n+1,10)
		s_list = f_sp - c + (b/a)*np.sqrt((a**2 - (e_py - e_list)**2))
		
		e_el_list = s_list/E # elastic strain
		e_pl_list = e_list - e_el_list # plastic strain
		e_pl_list[0] = 0
		
		if softening:
			s_list = np.append(s_list,[fy_T,50,50])
			e_pl_list = np.append(e_pl_list,[e_pt - fy_T/E,e_pu-50/E,0.11])
		
		s_list,e_pl_list = regalurize_fp(s_list,e_pl_list,n=n2)
		
		sig_data.append(s_list)
		ep_data.append(e_pl_list)
	
	# repackage stress strain data for output
	sig_out = np.array(sig_data).flatten() # [MPa]
	ep_out = np.array(ep_data).flatten() # [-]
	T_out = np.repeat(T_list,n2) # [°C]
	
	s_out = pd.concat([pd.DataFrame(sig_out),pd.DataFrame(ep_out),pd.DataFrame(T_out)],axis=1)
	s_out.columns = ['s [MPa]','e_pl [-]','T [°C]']
	
	# repackage elasticity data for output
	E_out = np.array(E_T_list)
	pois_out = np.ones(T_list.size)*0.3
	
	e_out = pd.concat([pd.DataFrame(E_out),pd.DataFrame(pois_out),pd.DataFrame(T_list)],axis=1)
	e_out.columns = ['E [MPa]','v [-]','T [°C]']
	
	if return_T_list:
		return s_out, e_out, T_list
	else:
		return s_out, e_out


def p_thermal_expansion_coef_EC():
	""" returns a table coefcient of thermal expansion (CET) for prestressing steel, with reference to the length at 20°C, for direct input in Abaqus
	accord. EN 1992-1-2 (pp. 29)
	Note: in abaqus thermal strains are defined as total expansion from a reference temperature
	See abaqus manual: http://dsk.ippt.pan.pl/docs/abaqus/v6.13/books/usb/default.htm?startat=pt05ch26s01abm52.html

	Returns
	-------
	out : pd.DataFrame
		Dataframe with 2 columns for Abaqus input	 | CET [-] | Temperature [°C] | 
	"""
	
	T_list = np.arange(20,1101,1)
	e_th = MechanicalTools.p_thermal_strain_EC(T_list)
	e_th[0]=0 # set first value equal to 0, EC2 analytical expression is exactly non-zero at 20°C
	
	cet = np.zeros(len(T_list))
	for i in range(0,len(T_list)):
		if i>0:
			cet[i]=(e_th[i]-e_th[0])/(T_list[i]-20)

	out = pd.concat([pd.DataFrame(cet),pd.DataFrame(T_list)],axis=1)
	out.columns = ['CET [-]','T [°C]']
	
	return out


########################################################
### AUX : Material properties in fib Model Code 2010 ###
########################################################
def c_tensile_strength_fib(fcm):
	""" calculate concrete mean tensile strength, accord. fib MC 2010 (pp. 118)

	Parameters
	----------
	fcm : float
		concrete mean compressive strength [MPa]
	
	Returns
	-------
	fctm : float
		concrete mean tensile strenght [MPa]
	"""
	
	fck = fcm -8
	fctm = 0.3*fck**(2/3) if fck <= 50 else 2.12*np.log(1+0.1*(fcm))
	return fctm


def c_fracture_energy_fib(fcm):
	""" calculate concrete fracture energy, accord. fib MC 2010 (pp. 120)
	
	Parameters
	----------
	fcm : float
		concrete mean compressive strength [MPa]
	
	Returns
	-------
	Gf : float
		concrete fracture energy (energy required to propagate a tensile crack of unit area) [N/m]
	"""
	return 73*fcm**(0.18)


###################
### AUX METHODS ###
###################

def regularize_fct(data, T_list, n=25):
	w_max = max(data['w [mm]'])
	w_out = arangeBias(0,w_max,n,20)
	
	s_data=[]; w_data=[]
	
	for T in T_list:
		data_T = data.loc[data['T [°C]'] == T]
		s_list = np.array(data_T['s [MPa]'])
		w_list = np.array(data_T['w [mm]'])
		
		s_list = np.append(s_list,s_list[-1])
		w_list = np.append(w_list,w_max)
		
		s_interpol = interp1d(w_list,s_list)
		s_out = s_interpol(w_out)
		
		s_data.append(s_out)
		w_data.append(w_out)
		
	s_df = np.array(s_data).flatten()
	w_df = np.array(w_data).flatten()
	T_df = np.repeat(T_list,n)
	
	out = pd.concat([pd.DataFrame(s_df),pd.DataFrame(w_df),pd.DataFrame(T_df)],axis=1)
	out.columns = ['s [MPa]','w [mm]','T [°C]']
	return out


def regalurize_fp(sig,ep,n=10):
	s_interpol = interp1d(ep,sig)
	ep_out = np.linspace(min(ep), max(ep),n)
	return s_interpol(ep_out), ep_out


def arangeBias(start,end,n,bias):
	""" create an array of numbers using a certain bias (similar to meshing bias in Abaqus)
	when bias = 1, behaves like np.arange(start,end,n)

	Parameters
	----------
	start, end : float
		start and end value of array
	
	n : int
		number of items in array, including 'start' and 'end'
		
	bias : float
		scale difference between first and last interval
	
	Returns
	-------
	out : np.array
		array of length n, in which the first interval is <bias> times the last interval
	
	Example use
	-----------
	>>> import numpy as np
	>>> from TTH_util import arangeBias
	>>> print(arangeBias(10,20,5,2))
	[10.   11.71018456   13.8648821    16.57963087   20.]
	"""
	
	bias = bias**(1/(n-2))
	
	intervals = []
	for i in range(0,n-1): intervals.append(bias**i)
	intervals_scaled = np.array(intervals)/sum(intervals)
	
	points = np.array([0])
	s = 0
	for i in intervals_scaled:
		s = s + i
		points = np.append(points,[s])
	
	return points*(end-start)+start



#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":
	
	SW_test = 2

	print("testing")
	
	if SW_test==1:
		import matplotlib.pyplot as plt
		fy=500
		Es=210000
		df_s, df_E = s_stress_strain_EC_T(fy,Es)
		for T in df_s['T [°C]'].unique():
			data = df_s.loc[df_s['T [°C]'] == T]
			E = df_E.loc[df_E['T [°C]'] == T]['E [MPa]']
			s = np.array(data['s [MPa]'])
			epl = data['e_pl [-]']
			eel = np.array(s/float(E))
			etot = eel+epl
			
			s = np.append([0], s)
			etot = np.append([0],etot)
			
			plt.plot(etot,s)
	
	if SW_test == 2:
		a = c_thermal_expansion_coef_EC_irr()
