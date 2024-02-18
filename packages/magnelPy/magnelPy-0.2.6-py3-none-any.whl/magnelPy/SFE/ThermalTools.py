"""Thermal Calculation Tools
Notes
-----
The thermal calculation tools module supports various temperature related methods for SFE.
"""

###############
### IMPORTS ###
###############

import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from magnelPy.SFE import FireCurve
from magnelPy.admin import df_writeToExcel



#################################
## USER ACCESIBILITY FUNCTIONS ##
#################################

def EC_concreteSlab_ISO834(h=None,tmax=None,tval=None,moisture=3):
	""" Concrete slab temperature calculation for ISO 834 standard fire exposure,
	in accordance with EN 1992-1-2:2004 provisions

	Parameters
	----------	
	h : float (if None : user input)
		slab thickness [m]

	tmax : float (if None : user input)
		calculated response time [min]
		
	tval : list of float (if None : user input)
		exposure times for calculation output [min]

	moisture : float
		percentage moisture content, percentage of concrete weight [w_%] in range 0 - 3
		required for EN1992-1-2:2004 (default: 3%)

	Returns
	-------
	theta : pd.DataFrame
		temperature in the concrete slab [°C]
		index = nodal position [m]
		column = exposure time [min]

	Note
	-------
	Initial temperature 20°C
	
	Example use
	-----------
	>>> python -c "import magnelPy.SFE as x; x.EC_concreteSlab_ISO834()		 
	"""
	# control switches
	SW_update='stepWise' # 'standard'; 'stepWise'

	# user input specification
	if h is None:
		print("Concrete slab temperature calculation. \nEN 1992-1-2:2004 provisions\nISO 834 standard fire exposure.\n")
		SW_cmd=True
		h,tmax,tval,folder=EC_concreteSlab_ISO834_UserInput()

	# dimension change
	tmax=tmax*60 # [s]
	tval_s = [x * 60 for x in tval] # [s]

	# parameter standard values - cf. EN1992-1-2:2004 
	hc_0=25 # [W/m2K] 0-surface convection coefficient
	eps_0=0.7 # [-] 0-surface emissivity
	hc_end=9 # [W/m2K] end-surface convection coefficient, includes radiation effect
	theta_0=20 # [°C] initial temperature	

	# discretization
	dx=0.001 # [m]
	dt=0.1 # [s]
	X=np.arange(dx/2,h,dx)
	t=np.arange(dt,tmax+dt,dt) # [s]

	# calculation setup - fire curve
	theta_g=FireCurve.ISO834(t/60) # [°C]
	theta=theta_0*np.ones(X.shape[0]) # starting temperature of elements
	theta_s=[theta_0,theta_0] # starting values for 0- and end-surface temperatures

	# output initialization
	out=pd.DataFrame(np.concatenate(([theta_s[0]],theta,[theta_s[-1]])),columns=[0],index=np.concatenate(([0],X,[h])))

	# calculation
	runner=0
	for i,ti in enumerate(t):
		# temperature-dependent properties updating
		if SW_update=='standard':
			cv=concreteVolumetricHeat(theta,method='EN1992-1-2:2004',moisture=moisture)
			K=concreteConductivity(theta,method='EN1992-1-2:2004')
			h0=equivalentConvection(hc_0,eps_0,theta_g[i],theta_s[0])
		elif SW_update=='stepWise':
			step=1 # [s]
			if np.abs(ti-np.around(ti/step,0))<10**-3 or i==0:
				cv=concreteVolumetricHeat(theta,method='EN1992-1-2:2004',moisture=moisture)
				K=concreteConductivity(theta,method='EN1992-1-2:2004')
				h0=equivalentConvection(hc_0,eps_0,theta_g[i],theta_s[0])
		# temperature forward integration
		theta,theta_s=HeatTransfer_1D(K,dx,cv,1,h0,hc_end,theta,theta_g[i],theta_0,dt,SW_surfTemp=True)    

		if np.abs(ti-tval_s[runner])<10**-3:
			out[tval[runner]]=np.concatenate(([theta_s[0]],theta,[theta_s[-1]]))
			print("{:.0f} min".format(tval[runner]))
			runner+=1

	# return
	if SW_cmd:
		file=folder+"\\concSlab_ISO834"
		print("printing to ",file+".xlsx")
		df_writeToExcel(out,file,str(h)+"m",SW_overwrite=False)
	else: return out

def EC_concreteSlab_ECparametric(h=None,qf=None,O=None,tmax=None,tval=None,moisture=3):
	""" Concrete slab temperature calculation for Eurocode parametric fire (reference compartment),
	in accordance with EN 1992-1-2:2004 provisions

	Parameters
	----------	
	h : float (if None : user input)
		slab thickness [m]

	qf : float
		fire load density related to the surface area [MJ/m2]

	O : float
		opening factor (typically) between 0.02 and 0.2 [m1/2]

	tmax : float (if None : user input)
		calculated response time [min]
		
	tval : list of float (if None : user input)
		exposure times for calculation output [min]

	moisture : float
		percentage moisture content, percentage of concrete weight [w_%] in range 0 - 3
		required for EN1992-1-2:2004 (default: 3%)

	Returns
	-------
	theta : pd.DataFrame
		temperature in the concrete slab [°C]
		index = nodal position [m]
		column = exposure time [min]

	Note
	-------
	Initial temperature 20°C
	
	Example use
	-----------
	>>> python -c "import magnelPy.SFE as x; x.EC_concreteSlab_ECparametric()		 
	"""
	# control switches
	SW_update='stepWise' # 'standard'; 'stepWise'

	# user input specification
	if h is None:
		print("Concrete slab temperature calculation. \nEN 1992-1-2:2004 provisions\nISO 834 standard fire exposure.\n")
		SW_cmd=True
		h,qf,O,tmax,tval,folder=EC_concreteSlab_ECparametric_UserInput()

	# dimension change
	tmax=tmax*60 # [s]
	tval_s = [x * 60 for x in tval] # [s]

	# parameter standard values - cf. EN1992-1-2:2004 
	hc_0=35 # [W/m2K] 0-surface convection coefficient
	eps_0=0.7 # [-] 0-surface emissivity
	hc_end=9 # [W/m2K] end-surface convection coefficient, includes radiation effect
	theta_0=20 # [°C] initial temperature	

	# discretization
	dx=0.001 # [m]
	dt=0.1 # [s]
	X=np.arange(dx/2,h,dx)
	t=np.arange(dt,tmax+dt,dt) # [s]

	# calculation setup - fire curve
	theta_g=FireCurve.EuroCodeParametric(t/60,O,qf) # [°C]
	theta=theta_0*np.ones(X.shape[0]) # starting temperature of elements
	theta_s=[theta_0,theta_0] # starting values for 0- and end-surface temperatures

	# output initialization
	out=pd.DataFrame(np.concatenate(([theta_s[0]],theta,[theta_s[-1]])),columns=[0],index=np.concatenate(([0],X,[h])))

	# calculation
	runner=0
	for i,ti in enumerate(t):
		# temperature-dependent properties updating
		if SW_update=='standard':
			cv=concreteVolumetricHeat(theta,method='EN1992-1-2:2004',moisture=moisture)
			K=concreteConductivity(theta,method='EN1992-1-2:2004')
			h0=equivalentConvection(hc_0,eps_0,theta_g[i],theta_s[0])
		elif SW_update=='stepWise':
			step=1 # [s]
			if np.abs(ti-np.around(ti/step,0))<10**-3 or i==0:
				cv=concreteVolumetricHeat(theta,method='EN1992-1-2:2004',moisture=moisture)
				K=concreteConductivity(theta,method='EN1992-1-2:2004')
				h0=equivalentConvection(hc_0,eps_0,theta_g[i],theta_s[0])
		# temperature forward integration
		theta,theta_s=HeatTransfer_1D(K,dx,cv,1,h0,hc_end,theta,theta_g[i],theta_0,dt,SW_surfTemp=True)    

		if np.abs(ti-tval_s[runner])<10**-3:
			out[tval[runner]]=np.concatenate(([theta_s[0]],theta,[theta_s[-1]]))
			print("{:.0f} min".format(tval[runner]))
			runner+=1

	# return
	if SW_cmd:
		file=folder+"\\concSlab_ECparametric_{:.2f}m".format(h)
		print("printing to ",file+".xlsx")
		df_writeToExcel(out,file,"{:.0f}MJm2_{:.2f}m0.5".format(qf,O),SW_overwrite=False)
	else: return out


############
## MODULE ##
############

def c_thermal_strain_EC(temp,aggregates='sil'):
	""" returns the total thermal eleongation (thermal strain), with reference to the length at 20°C, accord. EN 1992-1-2 (pp. 26)
	
	>> MOVED to SFE.MechanicalTools.py <<
	
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


def HeatTransfer_1D(k,L,cv,A,h0,hend,theta,theta_inf_0,theta_inf_end,dt,SW_surfTemp=False):
	""" 1D heat transfer calculation step

	Parameters
	----------	
	k : (m,) np.array
		material thermal conductivity [W/(mK)]

	L : float or (m,) np.array
		element thickness [m]

	cv : float or (m,) np.array
		volumetric heat capacity [J/(m**3K)]
		
	A : float or (m,) np.array
		sample area perpendicular to the direction of heat transfer [m2]

	h0 : float
		convection coefficient at 0-surface [W/(m2K)]

	hend : float
		convection coefficient at end-surface [W/(m2K)]

	theta : (m,) np.array [°C] or [K]
		temperature of the sample

	theta_inf_0 : float
		exposure temperature at 0-surface

	theta_inf_end : float
		exposure temperature at end-surface

	dt : float
		timestep [s]

	SW_surfTemp : Boolean
		switch for calculation of surface temperatures

	Returns
	-------
	theta : (m,) np.array [°C] or [K]
		temperature of the sample

	Example use
	-----------
	>>> XXX		 
	"""	
	R=Resistance_1D(k,L,A,h0,hend)# (n x 1) array of resistance : 1 @ surface, n-1 between nodes, 1 @ end
	# theta=np.append(np.insert(theta,0,theta_inf_0),theta_inf_end) # single theta-vector : code option A
	theta=np.concatenate(([theta_inf_0],theta,[theta_inf_end])) # single theta-vector : code option B
	Q_ij=Qij(theta[:-1],theta[1:],R) # [W] (n+1 x 1) heat transfer values
	Q_i=-np.diff(Q_ij) # (n x 1) net heat transfer to nodes; equivalent to : Qi=Qij[:-1]-Qij[1:]
	theta[1:-1]+=element_TempChange(Q_i,L*A,dt,cv) # updated temperature vector

	if not SW_surfTemp: return theta[1:-1]
	else:
		Rsurf=R_conv([h0,hend],A)
		theta_s=surfaceTemp(theta[[0,-1]],theta[[1,-2]],R[[0,-1]],Rsurf)
		return theta[1:-1],theta_s


#########
## AUX ##
#########

def equivalentConvection(h,eps,theta_inf,theta_s):
	""" Equivalent convection coefficient for radiation effect

	Parameters
	----------		
	h : float or (m,n) np.array
		convection coefficient [W/(m2K)]

	eps : float or (m,n) np.array
		emissivity/absorptivity [-]

	theta_inf : float or (m,n) np.array
		exposure temperature [°C]

	theta_s : float or (m,n) np.array
		surface temperature	

	Returns
	-------
	h_eq : float or (m,) np.array
		equivalent covection coefficient [W/(m2K)]

	Example use
	-----------
	>>> XXX	
	"""
	from scipy.constants import sigma as sig # Stefan-Boltzmann coefficient : 5.670367*10**-8 [J/(sm2K4)]

	Tinf=theta_inf+273.15 # [K] dimension change
	Ts=theta_s+273.15 # [K] dimension change

	return h+eps*sig*(Tinf**2+Ts**2)*(Tinf+Ts)

def element_TempChange(Q,dV,dt,cv):
	""" Temperature change of a uniform temperature element, for given heat transfer in time interval
	
	Parameters
	----------	
	Q : float or (m x n) np.array
		heat transfer (inflow-outflow+generated) for the element [W]

	dV : float or (m x n) np.array
		volume of the element [m3]
		
	dt : float
		time interval for which the heat transfer and element properties are approximated constant [s]

	cv : float or (m x n) np.array
		volumetric heat capacity [J/(m**3K)]

	Returns
	-------
	dT : float or (m x n) np.array
		temperature change for the element
	
	Example use
	-----------
	print("### CASE 1 - HEATING OF WATER ###")
    print("Coolblue reports \"experimental results\" for water boiler:\
        \n- 2200 W\n- 115 sec till boiling (incl. 15 sec of boiling)\n- for 0.5 l")

    # temperature increase
    V=0.5*10**-3 # [m3] volume of water
    Q=2200 # [W] net heat input
    duration=115-15 # [s] listed boiling time
    cv=4186*10**3 # [J/(m3K)] volumetric heat = 4186 [J/(kgK)] * 10**3 [kg/m3]
    
    # calculate temperature increase
    theta=ThermalTools.element_TempChange(Q,V,duration,cv)
    print("==> Temperature increase implied by Coolblue data: {:.2f} °Celcius".format(theta))

    ## Output :
    # ### CASE 1 - HEATING OF WATER ###
    # Coolblue reports "experimental results" for water boiler:
    # - 2200 W
    # - 115 sec till boiling (incl. 15 sec of boiling)
    # - for 0.5 l
    # ==> Temperature increase implied by Coolblue data: 105.11 °Celcius	 
	"""
	return Q*dt/(cv*dV)

def Qij(Ti,Tj,Rij):
	""" Heat transferred from node i to node j

	Parameters
	----------	
	Ti : float or (m x n) np.array
		temperature of node i [°C] or [K]

	Tj : float or (m x n) np.array
		temperature of node j [°C] or [K]
		
	Rij : float or (m x n) np.array
		heat transfer resistance between nodes [K/W]

	Returns
	-------
	Q : float or (m x n) np.array
		heat transferred between nodes
	
	Example use
	-----------
	>>> XXX		 
	"""
	return (Ti-Tj)/Rij

def R_cond(k,L,A,type='element'):
	""" Conduction resistance for uniform material sample
	- option 1 : conduction resistance for given element (or array of elements) : type == element
	- option 2 : conduction resistance in between elements : type == interface -- currently only for 1D model

	Parameters
	----------	
	k : float or (m x n) np.array
		material thermal conductivity [W/(mK)]

	L : float or (m x n) np.array
		thickness of the sample [m]
		
	A : float or (m x n) np.array
		sample area perpendicular to the direction of heat transfer [m2]

	Returns
	-------
	R : float or (m x n) np.array
		heat transfer resistance [K/W]
	
	Example use
	-----------
	>>> XXX		 
	"""
	R=L/(k*A)
	if type=='element': return R
	if type=='interface':
		return R[:-1]+np.diff(R)/2 # currently only for 1D model - note: this (better) approx results in a (slightly) lower conductivity / higher resistance as compared to keq = 1/2*(k1+k2)

def R0(h,k,L,A):
	""" Resistance between ambient and first node // applies to end node as well

	Parameters
	----------	
	h : float or (m,) np.array
		covection resistance [W/(m2K)]

	k : float or (m,) np.array
		material thermal conductivity [W/(mK)]

	L : float or (m,) np.array
		thickness of the sample [m]
		
	A : float or (m,) np.array
		sample area perpendicular to the direction of heat transfer [m2]

	Returns
	-------
	R : float or (m,) np.array
		heat transfer resistance [K/W]
	
	Example use
	-----------
	>>> XXX		 
	"""
	return L/(2*k*A)+1/(h*A) # note : half sample thickness from surface to first node

def R_total_1D(R_0,R_internal,R_end):
	""" Total resistance vector 1D thermal calculation

	Parameters
	----------	
	R_0 : float 
		resistance from boundary temperature to first node [K/W]

	R_interal : (n, ) np.array
		internal conduction resistance between n+1 nodes [K/W]
		
	R_end : float 
		resistance from last node to boundary temperature [K/W]

	Returns
	-------
	R : (n+1,) np.array
		heat transfer resistance [K/W]

	Comment
	-------
	- To be superseded by 2D concept
	- Different return options in code give same result; speed difference unclear
	
	Example use
	-----------
	>>> XXX		 
	"""
	# return np.append([R_0],np.append(R_internal,R_end))
	return np.concatenate(([R_0],R_internal,[R_end]))
	# return np.append(np.insert(R_internal,[0],[R_0]),R_end)
	# return np.append(np.concatenate(([R_0],R_internal)),R_end)

def Resistance_1D(k,L,A,h0,hend):
	""" Total resistance vector 1D thermal calculation - from input values

	Parameters
	----------	
	k : (m,) np.array
		material thermal conductivity [W/(mK)]

	L : float (m,) np.array
		element thickness [m]
		
	A : float or (m,) np.array
		sample area perpendicular to the direction of heat transfer [m2]

	h0 : float
		convection resistance at 0-surface [W/(m2K)]

	hend : float
		convection resistance at end-surface [W/(m2K)]

	Returns
	-------
	R : (n+1,) np.array
		heat transfer resistance [K/W]

	Comment
	-------
	- To be superseded by 2D concept
	- Different return options in code give same result; speed difference unclear
	
	Example use
	-----------
	>>> XXX		 
	"""
	Rcond=R_cond(k,L,A,type='interface') # conduction resistance in the core solid
	try:
		R_0=R0(h0,k[0],L[0],A) # resistance to first node
		Rend=R0(hend,k[-1],L[-1],A) # resistance from end node
	except: # L as float
		R_0=R0(h0,k[0],L,A) # resistance to first node
		Rend=R0(hend,k[-1],L,A) # resistance from end node	
	R=R_total_1D(R_0,Rcond,Rend) # (n x 1) array of resistance : 1 @ surface, n-1 between nodes, adiabatic @ end
	return R


def surfaceTemp(theta_inf,theta_1,R0,Rsurf):
	""" Surface temperature

	Parameters
	----------	
	theta_inf : float or (m x n) np.array
		ambient temperature [°C] or [K]

	theta_1 : float or (m x n) np.array
		first node temperature [°C] or [K]

	R0 : float or (m x n) np.array 
		resistance between ambient and first node [K/W]
		
	Rsurf : float or (m x n) np.array 
		surface resistance [K/W]

	Returns
	-------
	R : (n+1,) np.array
		heat transfer resistance [K/W]

	Comment
	-------
	- To be superseded by 2D concept
	- Different return options in code give same result; speed difference unclear
	
	Example use
	-----------
	>>> XXX		 
	"""
	# return np.append([R_0],np.append(R_internal,R_end))
	# return np.concatenate(([R_0],R_internal,[R_end]))
	return theta_inf-(theta_inf-theta_1)*Rsurf/R0

def R_conv(h,A):
	""" Convection resistance
	- incomplete help specification
	"""
	X=h*A
	return np.ones(np.shape(X))/X

def EC_concreteSlab_ISO834_UserInput():
	""" cmd-line user input for EC_concreteSlab_ISO834
	"""	
	h=UserInput_common1()
	tmax,tval,targetfolder=UserInput_common2()

	return h,tmax,tval,targetfolder

def EC_concreteSlab_ECparametric_UserInput():

	h=UserInput_common1()

	# qf
	qf=780 # [MJ/m2]
	print("\n## The fire load density is %i MJ/m2 ##" % (qf))
	u=input("Press ENTER to confirm, or specify other qf [MJ/m2]: ")
	if u!='': qf=float(u); print("\n %d MJ per m2 floor area" % (qf))

	# O
	O=0.04 # [m1/2]
	print("\n## The opening factor is %d m0.5 ##" % (O))
	u=input("Press ENTER to confirm, or specify other O [m0.5]: ")
	if u!='': O=float(u); print("\n %i m0.5 opening factor" % (O))

	tmax,tval,targetfolder=UserInput_common2()

	return h,qf,O,tmax,tval,targetfolder

def UserInput_common1():
	# h
	h=0.2 # [m]
	print("\n## Slab thickness = {:.3f} m ##".format(h))
	u=input("Press ENTER to confirm, or specify alternative slab thickness [m]: ")
	if u!='': h=float(u); print("\n Concrete slab thickness {:.3f} m".format(h))

	return h

def UserInput_common2():
	# tmax
	tmax=120 # [min]
	print("\n## Maximum exposure time calculation %i minutes ##" % (tmax))
	u=input("Press ENTER to confirm, or specify other tmax [min]: ")
	if u!='': tmax=int(u); print("\n %i min ISO 834 standard heating regime" % (tmax))

	# valuation steps
	tval=np.arange(15,tmax+1,15)
	print("\n## The default time-step for printing is 15 minutes.\nTime-steps for which the temperature will be saved are ", tval, " ##")
	u=input("Press ENTER to confirm, or specify alternative timestep: ")
	if u!='': step=int(u); tval=np.arange(step,tmax+1,step); print("\nTime-steps for which the temperature will be saved are ", tval)

	# target folder
	print("\n## Results will be saved in local worker directory. ##")
	u=input("Press ENTER to confirm, or provide path to alternative directory: ")
	if u!='': 
		if u[0]=="\"": targetfolder=u[1:-1] # strips quotes from path
		else: targetfolder=u
	else: targetfolder=os.getcwd()
	print("\nOutput will be saved in ", targetfolder)

	return tmax,tval,targetfolder

############
## LEGACY ##
############

def concreteVolumetricHeat(Temp,method='EN1992-1-2:2004',moisture=3,rho_concrete = 2400):
	""" concrete volumetric heat at elevated temperature

	Parameters
	----------	
	Temp : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]

	method : str
		Indication of data used; options:
		'EN1992-1-2:2004' (default) : Eurocode values

	moisture : float
		percentage moisture content, percentage of concrete weight [w_%] in range 0 - 3
		required for EN1992-1-2:2004 (default: 3%)

	rho_concrete : float
		Concrete density at room temperature [kg/m3]
		required for EN1992-1-2:2004 (default: 2400 kg/m3)

	Returns
	-------
	c_v : float or np.array
		 volumetric heat of concrete [J/m3]
	
	Example use
	-----------
	>>> XXX		 
	"""
	if method=='EN1992-1-2:2004':
		density=c_density_EC_T(Temp,rho_concrete)
		cp=c_specific_heat_EC_T(Temp, moisture)
		return cp*density

def concreteConductivity(Temp,method='EN1992-1-2:2004',limit='lower'):
	""" concrete conductivity at elevated temperature

	Parameters
	----------	
	Temp : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]

	method : str
		Indication of data used; options:
		'EN1992-1-2:2004' (default) : Eurocode values

	limit : str
		argument for 
		'lower'  = lower bound Eurocode conductivity (default)
		'upper' = upper bound Eurocode conductivity

	Returns
	-------
	lambda_c : float or np.array
		 thermal conductivity of concrete [W/m K]
	
	Example use
	-----------
	>>> XXX		 
	"""
	if method=='EN1992-1-2:2004':
		return c_conductivity_EC_T(Temp, limit)

def c_density_EC_T(Temp,rho_concrete = 2400):
	""" concrete density at elevated temperature (influenced by water loss), accord. EN 1992-1-2 (pp. 28)
	
	Parameters
	----------	
	rho_concrete : float
		Concrete density at room temperature [kg/m3] (Default: 2400)
	
	Temp : float or np.array
		(array of) Temperature(s) in range 20 - 1200 [°C]

	Returns
	-------
	rho_T : float or np.array
		(Reduced) density for concrete at temperature Temp [kg/m3]
	
	Example use
	-----------
	>>> import numpy as np
	>>> import magnelPy.SFE as sfe
	>>> Temp = np.arange(900,1001,20)
	>>> rho_c = 2300
	>>> rho_T = sfe.ThermalTools.c_density_EC_T(Temp,rho_c)

	[2084.375 2080.35  2076.325 2072.3   2068.275 2064.25 ]			
	"""
	SW_method='interp1d' # 'interp1d'; 'np.piecewise'; 'precalc'
	# note : possibly further options where a precalc is loaded as part of the module from a pickle or similar

	if SW_method=='interp1d': # reference interpolation approach - approx 5s for referene test (ExampleCases\06_1DThermalCalc.py - Case 5)
		T_list = [20,115,200,400,1200]
		k_rho_list = [1,1,0.98,0.95,0.88] 
		k_rho_data = interp1d(T_list,k_rho_list)
		k_rho = k_rho_data(Temp)
	elif SW_method=='np.piecewise': # alternative interpolation approach - approx 3s for referene test (ExampleCases\06_1DThermalCalc.py - Case 5)
		k_rho=np.piecewise(
			Temp,
			[(115<Temp)&(Temp<=200),(200<Temp)&(Temp<=400),400<Temp],
			[lambda Temp:1-0.02*(Temp-115)/85,lambda Temp:0.98-0.03*(Temp-200)/200,lambda Temp:0.95-0.07*(Temp-400)/800,1])
	elif SW_method=='precalc': # alternative interpolation approach - extremely slow - code left for reference
		T=np.arange(0,1201,1)
		k=np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0.999764705882353,0.999529411764706,0.999294117647059,0.999058823529412,0.998823529411765,0.998588235294118,0.998352941176471,0.998117647058824,0.997882352941176,0.997647058823529,0.997411764705882,0.997176470588235,0.996941176470588,0.996705882352941,0.996470588235294,0.996235294117647,0.996,0.995764705882353,0.995529411764706,0.995294117647059,0.995058823529412,0.994823529411765,0.994588235294118,0.994352941176471,0.994117647058824,0.993882352941176,0.993647058823529,0.993411764705882,0.993176470588235,0.992941176470588,0.992705882352941,0.992470588235294,0.992235294117647,0.992,0.991764705882353,0.991529411764706,0.991294117647059,0.991058823529412,0.990823529411765,0.990588235294118,0.990352941176471,0.990117647058824,0.989882352941176,0.989647058823529,0.989411764705882,0.989176470588235,0.988941176470588,0.988705882352941,0.988470588235294,0.988235294117647,0.988,0.987764705882353,0.987529411764706,0.987294117647059,0.987058823529412,0.986823529411765,0.986588235294118,0.986352941176471,0.986117647058824,0.985882352941176,0.985647058823529,0.985411764705882,0.985176470588235,0.984941176470588,0.984705882352941,0.984470588235294,0.984235294117647,0.984,0.983764705882353,0.983529411764706,0.983294117647059,0.983058823529412,0.982823529411765,0.982588235294118,0.982352941176471,0.982117647058824,0.981882352941176,0.981647058823529,0.981411764705882,0.981176470588235,0.980941176470588,0.980705882352941,0.980470588235294,0.980235294117647,0.98,0.97985,0.9797,0.97955,0.9794,0.97925,0.9791,0.97895,0.9788,0.97865,0.9785,0.97835,0.9782,0.97805,0.9779,0.97775,0.9776,0.97745,0.9773,0.97715,0.977,0.97685,0.9767,0.97655,0.9764,0.97625,0.9761,0.97595,0.9758,0.97565,0.9755,0.97535,0.9752,0.97505,0.9749,0.97475,0.9746,0.97445,0.9743,0.97415,0.974,0.97385,0.9737,0.97355,0.9734,0.97325,0.9731,0.97295,0.9728,0.97265,0.9725,0.97235,0.9722,0.97205,0.9719,0.97175,0.9716,0.97145,0.9713,0.97115,0.971,0.97085,0.9707,0.97055,0.9704,0.97025,0.9701,0.96995,0.9698,0.96965,0.9695,0.96935,0.9692,0.96905,0.9689,0.96875,0.9686,0.96845,0.9683,0.96815,0.968,0.96785,0.9677,0.96755,0.9674,0.96725,0.9671,0.96695,0.9668,0.96665,0.9665,0.96635,0.9662,0.96605,0.9659,0.96575,0.9656,0.96545,0.9653,0.96515,0.965,0.96485,0.9647,0.96455,0.9644,0.96425,0.9641,0.96395,0.9638,0.96365,0.9635,0.96335,0.9632,0.96305,0.9629,0.96275,0.9626,0.96245,0.9623,0.96215,0.962,0.96185,0.9617,0.96155,0.9614,0.96125,0.9611,0.96095,0.9608,0.96065,0.9605,0.96035,0.9602,0.96005,0.9599,0.95975,0.9596,0.95945,0.9593,0.95915,0.959,0.95885,0.9587,0.95855,0.9584,0.95825,0.9581,0.95795,0.9578,0.95765,0.9575,0.95735,0.9572,0.95705,0.9569,0.95675,0.9566,0.95645,0.9563,0.95615,0.956,0.95585,0.9557,0.95555,0.9554,0.95525,0.9551,0.95495,0.9548,0.95465,0.9545,0.95435,0.9542,0.95405,0.9539,0.95375,0.9536,0.95345,0.9533,0.95315,0.953,0.95285,0.9527,0.95255,0.9524,0.95225,0.9521,0.95195,0.9518,0.95165,0.9515,0.95135,0.9512,0.95105,0.9509,0.95075,0.9506,0.95045,0.9503,0.95015,0.95,0.9499125,0.949825,0.9497375,0.94965,0.9495625,0.949475,0.9493875,0.9493,0.9492125,0.949125,0.9490375,0.94895,0.9488625,0.948775,0.9486875,0.9486,0.9485125,0.948425,0.9483375,0.94825,0.9481625,0.948075,0.9479875,0.9479,0.9478125,0.947725,0.9476375,0.94755,0.9474625,0.947375,0.9472875,0.9472,0.9471125,0.947025,0.9469375,0.94685,0.9467625,0.946675,0.9465875,0.9465,0.9464125,0.946325,0.9462375,0.94615,0.9460625,0.945975,0.9458875,0.9458,0.9457125,0.945625,0.9455375,0.94545,0.9453625,0.945275,0.9451875,0.9451,0.9450125,0.944925,0.9448375,0.94475,0.9446625,0.944575,0.9444875,0.9444,0.9443125,0.944225,0.9441375,0.94405,0.9439625,0.943875,0.9437875,0.9437,0.9436125,0.943525,0.9434375,0.94335,0.9432625,0.943175,0.9430875,0.943,0.9429125,0.942825,0.9427375,0.94265,0.9425625,0.942475,0.9423875,0.9423,0.9422125,0.942125,0.9420375,0.94195,0.9418625,0.941775,0.9416875,0.9416,0.9415125,0.941425,0.9413375,0.94125,0.9411625,0.941075,0.9409875,0.9409,0.9408125,0.940725,0.9406375,0.94055,0.9404625,0.940375,0.9402875,0.9402,0.9401125,0.940025,0.9399375,0.93985,0.9397625,0.939675,0.9395875,0.9395,0.9394125,0.939325,0.9392375,0.93915,0.9390625,0.938975,0.9388875,0.9388,0.9387125,0.938625,0.9385375,0.93845,0.9383625,0.938275,0.9381875,0.9381,0.9380125,0.937925,0.9378375,0.93775,0.9376625,0.937575,0.9374875,0.9374,0.9373125,0.937225,0.9371375,0.93705,0.9369625,0.936875,0.9367875,0.9367,0.9366125,0.936525,0.9364375,0.93635,0.9362625,0.936175,0.9360875,0.936,0.9359125,0.935825,0.9357375,0.93565,0.9355625,0.935475,0.9353875,0.9353,0.9352125,0.935125,0.9350375,0.93495,0.9348625,0.934775,0.9346875,0.9346,0.9345125,0.934425,0.9343375,0.93425,0.9341625,0.934075,0.9339875,0.9339,0.9338125,0.933725,0.9336375,0.93355,0.9334625,0.933375,0.9332875,0.9332,0.9331125,0.933025,0.9329375,0.93285,0.9327625,0.932675,0.9325875,0.9325,0.9324125,0.932325,0.9322375,0.93215,0.9320625,0.931975,0.9318875,0.9318,0.9317125,0.931625,0.9315375,0.93145,0.9313625,0.931275,0.9311875,0.9311,0.9310125,0.930925,0.9308375,0.93075,0.9306625,0.930575,0.9304875,0.9304,0.9303125,0.930225,0.9301375,0.93005,0.9299625,0.929875,0.9297875,0.9297,0.9296125,0.929525,0.9294375,0.92935,0.9292625,0.929175,0.9290875,0.929,0.9289125,0.928825,0.9287375,0.92865,0.9285625,0.928475,0.9283875,0.9283,0.9282125,0.928125,0.9280375,0.92795,0.9278625,0.927775,0.9276875,0.9276,0.9275125,0.927425,0.9273375,0.92725,0.9271625,0.927075,0.9269875,0.9269,0.9268125,0.926725,0.9266375,0.92655,0.9264625,0.926375,0.9262875,0.9262,0.9261125,0.926025,0.9259375,0.92585,0.9257625,0.925675,0.9255875,0.9255,0.9254125,0.925325,0.9252375,0.92515,0.9250625,0.924975,0.9248875,0.9248,0.9247125,0.924625,0.9245375,0.92445,0.9243625,0.924275,0.9241875,0.9241,0.9240125,0.923925,0.9238375,0.92375,0.9236625,0.923575,0.9234875,0.9234,0.9233125,0.923225,0.9231375,0.92305,0.9229625,0.922875,0.9227875,0.9227,0.9226125,0.922525,0.9224375,0.92235,0.9222625,0.922175,0.9220875,0.922,0.9219125,0.921825,0.9217375,0.92165,0.9215625,0.921475,0.9213875,0.9213,0.9212125,0.921125,0.9210375,0.92095,0.9208625,0.920775,0.9206875,0.9206,0.9205125,0.920425,0.9203375,0.92025,0.9201625,0.920075,0.9199875,0.9199,0.9198125,0.919725,0.9196375,0.91955,0.9194625,0.919375,0.9192875,0.9192,0.9191125,0.919025,0.9189375,0.91885,0.9187625,0.918675,0.9185875,0.9185,0.9184125,0.918325,0.9182375,0.91815,0.9180625,0.917975,0.9178875,0.9178,0.9177125,0.917625,0.9175375,0.91745,0.9173625,0.917275,0.9171875,0.9171,0.9170125,0.916925,0.9168375,0.91675,0.9166625,0.916575,0.9164875,0.9164,0.9163125,0.916225,0.9161375,0.91605,0.9159625,0.915875,0.9157875,0.9157,0.9156125,0.915525,0.9154375,0.91535,0.9152625,0.915175,0.9150875,0.915,0.9149125,0.914825,0.9147375,0.91465,0.9145625,0.914475,0.9143875,0.9143,0.9142125,0.914125,0.9140375,0.91395,0.9138625,0.913775,0.9136875,0.9136,0.9135125,0.913425,0.9133375,0.91325,0.9131625,0.913075,0.9129875,0.9129,0.9128125,0.912725,0.9126375,0.91255,0.9124625,0.912375,0.9122875,0.9122,0.9121125,0.912025,0.9119375,0.91185,0.9117625,0.911675,0.9115875,0.9115,0.9114125,0.911325,0.9112375,0.91115,0.9110625,0.910975,0.9108875,0.9108,0.9107125,0.910625,0.9105375,0.91045,0.9103625,0.910275,0.9101875,0.9101,0.9100125,0.909925,0.9098375,0.90975,0.9096625,0.909575,0.9094875,0.9094,0.9093125,0.909225,0.9091375,0.90905,0.9089625,0.908875,0.9087875,0.9087,0.9086125,0.908525,0.9084375,0.90835,0.9082625,0.908175,0.9080875,0.908,0.9079125,0.907825,0.9077375,0.90765,0.9075625,0.907475,0.9073875,0.9073,0.9072125,0.907125,0.9070375,0.90695,0.9068625,0.906775,0.9066875,0.9066,0.9065125,0.906425,0.9063375,0.90625,0.9061625,0.906075,0.9059875,0.9059,0.9058125,0.905725,0.9056375,0.90555,0.9054625,0.905375,0.9052875,0.9052,0.9051125,0.905025,0.9049375,0.90485,0.9047625,0.904675,0.9045875,0.9045,0.9044125,0.904325,0.9042375,0.90415,0.9040625,0.903975,0.9038875,0.9038,0.9037125,0.903625,0.9035375,0.90345,0.9033625,0.903275,0.9031875,0.9031,0.9030125,0.902925,0.9028375,0.90275,0.9026625,0.902575,0.9024875,0.9024,0.9023125,0.902225,0.9021375,0.90205,0.9019625,0.901875,0.9017875,0.9017,0.9016125,0.901525,0.9014375,0.90135,0.9012625,0.901175,0.9010875,0.901,0.9009125,0.900825,0.9007375,0.90065,0.9005625,0.900475,0.9003875,0.9003,0.9002125,0.900125,0.9000375,0.89995,0.8998625,0.899775,0.8996875,0.8996,0.8995125,0.899425,0.8993375,0.89925,0.8991625,0.899075,0.8989875,0.8989,0.8988125,0.898725,0.8986375,0.89855,0.8984625,0.898375,0.8982875,0.8982,0.8981125,0.898025,0.8979375,0.89785,0.8977625,0.897675,0.8975875,0.8975,0.8974125,0.897325,0.8972375,0.89715,0.8970625,0.896975,0.8968875,0.8968,0.8967125,0.896625,0.8965375,0.89645,0.8963625,0.896275,0.8961875,0.8961,0.8960125,0.895925,0.8958375,0.89575,0.8956625,0.895575,0.8954875,0.8954,0.8953125,0.895225,0.8951375,0.89505,0.8949625,0.894875,0.8947875,0.8947,0.8946125,0.894525,0.8944375,0.89435,0.8942625,0.894175,0.8940875,0.894,0.8939125,0.893825,0.8937375,0.89365,0.8935625,0.893475,0.8933875,0.8933,0.8932125,0.893125,0.8930375,0.89295,0.8928625,0.892775,0.8926875,0.8926,0.8925125,0.892425,0.8923375,0.89225,0.8921625,0.892075,0.8919875,0.8919,0.8918125,0.891725,0.8916375,0.89155,0.8914625,0.891375,0.8912875,0.8912,0.8911125,0.891025,0.8909375,0.89085,0.8907625,0.890675,0.8905875,0.8905,0.8904125,0.890325,0.8902375,0.89015,0.8900625,0.889975,0.8898875,0.8898,0.8897125,0.889625,0.8895375,0.88945,0.8893625,0.889275,0.8891875,0.8891,0.8890125,0.888925,0.8888375,0.88875,0.8886625,0.888575,0.8884875,0.8884,0.8883125,0.888225,0.8881375,0.88805,0.8879625,0.887875,0.8877875,0.8877,0.8876125,0.887525,0.8874375,0.88735,0.8872625,0.887175,0.8870875,0.887,0.8869125,0.886825,0.8867375,0.88665,0.8865625,0.886475,0.8863875,0.8863,0.8862125,0.886125,0.8860375,0.88595,0.8858625,0.885775,0.8856875,0.8856,0.8855125,0.885425,0.8853375,0.88525,0.8851625,0.885075,0.8849875,0.8849,0.8848125,0.884725,0.8846375,0.88455,0.8844625,0.884375,0.8842875,0.8842,0.8841125,0.884025,0.8839375,0.88385,0.8837625,0.883675,0.8835875,0.8835,0.8834125,0.883325,0.8832375,0.88315,0.8830625,0.882975,0.8828875,0.8828,0.8827125,0.882625,0.8825375,0.88245,0.8823625,0.882275,0.8821875,0.8821,0.8820125,0.881925,0.8818375,0.88175,0.8816625,0.881575,0.8814875,0.8814,0.8813125,0.881225,0.8811375,0.88105,0.8809625,0.880875,0.8807875,0.8807,0.8806125,0.880525,0.8804375,0.88035,0.8802625,0.880175,0.8800875,0.88])
		s=pd.Series(k,index=T)
		aid=np.rint(Temp)
		k_rho=s[aid].values
	return(k_rho*rho_concrete)

	
def c_conductivity_EC_T(Temp, limit='lower'):
	""" concrete thermal conductivity at elevated temperature, accord. EN 1992-1-2 (pp. 28)
	
	Parameters
	----------
	Temp : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]
		
	limit : String
		'lower'  = lower bound Eurocode conductivity - recommended value (default)
		'upper' =  upper bound Eurocode conductivity - value for composite structures
	
	Returns
	-------
	lambda_c : float or np.array
		 thermal conductivity of concrete [W/m K]
	 
	Example use
	-----------
	>>> import numpy as np
	>>> import magnelPy.SFE as sfe
	>>> Temp = np.arange(20,1101,20)
	>>> lambda_c = sfe.ThermalTools.c_conductivity_EC_T(Temp)		 
	"""
	
	if limit == 'lower':
		return 1.36 - 0.136*(Temp/100) + 0.0057*(Temp/100)*(Temp/100)
	
	if limit == 'upper':
		return 2.00 - 0.2451*(Temp/100) + 0.0107*(Temp/100)*(Temp/100)

	
def c_specific_heat_EC_T(Temp, moisture = 3):
	""" concrete specific heat at elevated temperature, accord. EN 1992-1-2 (pp. 26-27)
	
	Parameters
	----------	
	Temp : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]
		
	moisture : float (percentage)
		moisture content, percentage of concrete weight [w_%] in range 0 - 3 

	Returns
	-------
	c_p : float or np.array
		 specific heat of concrete [J/kg K]
	
	Example use
	-----------
	>>> import numpy as np
	>>> import magnelPy.SFE as sfe
	>>> Temp = np.arange(20,1101,20)
	>>> moisture_c = 2
	>>> c_p = sfe.ThermalTools.c_specific_heat_EC_T(Temp,moisture_c)		 
	"""
	SW_method='interp1d' # 'interp1d'; 'np.piecewise'

	if SW_method=='interp1d':

		if moisture > 0: # reference interpolation approach - approx 9s for referene test (ExampleCases\06_1DThermalCalc.py - Case 5)
			u_list = [0.0,1.5,3.0]
			cp_peak_list = [900,1470,2020]
			cp_peak_interp = interp1d(u_list,cp_peak_list) # assumes linear interpolation for moisture percentage values between 0 and 3% 
			cp_peak = cp_peak_interp(moisture)
			
			T_list = [20,99,100,115,200,400,1200]
			cp_list = [900,900,cp_peak,cp_peak,1000,1100,1100]
		if moisture == 0:
			T_list = [20,100,200,400,1200]
			cp_list = [900,900,1000,1100,1100]
			
		cp_interp = interp1d(T_list,cp_list)	
		cp=cp_interp(Temp)

	elif SW_method=='np.piecewise': # alternative interpolation approach - approx 3s for referene test (ExampleCases\06_1DThermalCalc.py - Case 5)
		if moisture>0: # note: below 0.263 % moisture, this results in a plateau below the 200°C final value of 1000 J/(kgK)
			dpeak=np.piecewise(moisture,[moisture<=1.5,moisture>1.5],[570/1.5*moisture,570+550/1.5*(moisture-1.5)]) 
			cp=np.piecewise(
				Temp,
				[(100<=Temp)&(Temp<=115),(115<Temp)&(Temp<=200),(200<Temp)&(Temp<=400),400<Temp],
				[lambda Temp:900+dpeak,lambda Temp:900+dpeak-(dpeak-100)*(Temp-115)/85,lambda Temp:1000+(Temp-200)/2,1100,900])
		elif moisture==0:
			cp=np.piecewise(
				Temp,
				[(Temp<=200),(200<Temp)&(Temp<=400),400<Temp],
				[lambda Temp:900+(Temp-100),lambda Temp:1000+(Temp-200)/2,1100,900])

	return cp


def s_conductivity_EC_T(Temp):
	""" steel thermal conductivity at elevated temperature, accord. EN 1993-1-2 (pp. 26)
	
	Parameters
	----------	
	Temp : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]
		
	Returns
	-------
	lambda_s : float or np.array
		 thermal conductivity of steel [W/m K]
	"""
	
	lambda_intp = interp1d([0,800,1200],[54,27.3,27.3])
	return lambda_intp(Temp)

	
def s_specific_heat_EC_T(Temp):
	""" steel specific heat at elevated temperature, accord. EN 1993-1-2 (pp. 25)
	
	Parameters
	----------	
	Temp : float or np.array
		(array of) Temperature in range 20 - 1200 [°C]

	Returns
	-------
	c_p : np.array
		 specific heat of steel [J/kg K]

	Note
	------
	Depreciation warning: functionality duplicate MaterialProperties\\Steel.py
	"""
	if type(Temp) == int: Temp = [Temp]
	
	cp_list = []
	for T in Temp:
		if T < 600:
			cp_list.append(425 + 0.773*T - 0.00169*T**2 + 2.22e-6*T**3)
		else:
			if T < 735:
				cp_list.append(666 + 13002/(738 - T))
			else:
				if T < 900:
					cp_list.append(545 + 17820/(T - 731))
				else:
					cp_list.append(650)
	
	return np.array(cp_list)

#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":

	print("testing")
	
	dV=np.array([[0.5*10**-3,10**-3],[0.5*10**-3,10**-3]])
	q=np.array([[2200,2200],[3000,3000]])
	dt=100
	cv=np.array([[4182*10**3,4182*10**3],[4182*10**3,4182*10**3]])

	print(dV)

	dT=element_TempChange(q,dV,dt,cv)
	print(dT)