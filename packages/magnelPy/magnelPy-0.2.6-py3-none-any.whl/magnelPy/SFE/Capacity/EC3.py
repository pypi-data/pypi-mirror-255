"""Capacity\\EC3
Notes
-----
EN 1993-1-2:2005 capacity evaluations
note: EN 1993-1-2:2005 further referenced as EC
"""

#############
## IMPORTS ##
#############

import numpy as np
from magnelPy.SFE.MaterialProperties import Steel as steel
import time as timekeeper


############
## MODULE ##
############

def steelcol_thetacrit(Hfi,NEdfi,Icol,Acol,fy,E=200000):
	""" Steel column critical temperature, considering capacity according to section 4.2.3.2 EC;

	Parameters
	----------	
	Hfi   : float
		[-], buckling length for fire design - see Figure 4.1 EC
	NEdfi : float
		[N], fire design load
	Icol  : float
		[mm4], cross-section moment of inertia - consider weak axis / strong axis ifo buckling length 
	Acol  : float
		[mm2], cross-section area
	fy	: float
		[N/mm2], steel yield stress in normal design conditions
	E	 : float
		[N/mm2], steel modulus of elasticity in normal design conditions

	Returns
	-------
	theta_crit : float
		 [C], critical temperature for axially loaded steel column
	
	Example use
	-----------
	from magnelPy.SFE.Capacity import EC3
	Hfi=3500 # [mm]
	Efi=9587*10**3 # [N]
	Icol=8.27*10**8 # [mm4]
	Acol=70.2*10**3 # [mm2] 
	fy=235 # [N/mm2]
	E=200000 # [N/mm2]
	theta_crit=EC3.steelcol_thetacrit(Hfi,Efi,Icol,Acol,fy,E) # [C]; critical temperature
	print("The critical temperature is {0:.0f} degrees C.".format(theta_crit))
	>>> The critical temperature is 508 degrees C.
	"""

	## aux
	tem=np.arange(100,1200,1)

	## column capacity ifo pre-listed critical temperature
	NRdfi=steelcol_capacityGivenTemperature(tem,Hfi,Icol,Acol,fy,E)

	## critical temperature
	theta_crit=np.interp(-NEdfi,-NRdfi,tem) # interpolate on negative values, since np.interp requires x-values to be increasing

	return theta_crit

def steelcol_capacityGivenTemperature(theta,Hfi,Icol,Acol,fy,E=200000,SW_elementwise=False):
	""" Steel column capacity for given critical temperature, according to section 4.2.3.2 EC;

	Parameters
	----------	
	theta : float or np.array (n,) or (m,)
		[C], uniform section temperature
	Hfi : float
		[-], buckling length for fire design - see Figure 4.1 EC
	Icol  : float
		[mm4], cross-section moment of inertia - consider weak axis / strong axis ifo buckling length 
	Acol  : float
		[mm2], cross-section area
	fy	: float or np.array (n,)
		[N/mm2], steel yield stress in normal design conditions
	E	 : float
		[N/mm2], steel modulus of elasticity in normal design conditions
	SW_elementwise : Boolean
		Combine array element-wise; requires arrays of same shape - now assumed (n,)

	Returns
	-------
	theta_crit : float
		 [C], critical temperature for axially loaded steel column
	
	Example use
	-----------
	from magnelPy.SFE.Capacity import EC3
	import numpy as np
	Hfi=3500 # [mm]
	Icol=8.27*10**8 # [mm4]
	Acol=70.2*10**3 # [mm2] 
	fy=235 # [N/mm2]
	E=200000 # [N/mm2]
	temperature=np.array([20,100,300,400,500,600,700])
	NRdfi=EC3.steelcol_capacityGivenTemperature(temperature,Hfi,Icol,Acol,fy,E) # [C]; critical temperature
	for i,tem in enumerate(temperature):
		print("At {0:.1f} degrees C, the design capacity is {1:.0f} kN.".format(tem,NRdfi[i]*10**-3))
	>>> At 20.0 degrees C, the design capacity is 13158 kN.
	>>> At 100.0 degrees C, the design capacity is 13158 kN.
	>>> At 300.0 degrees C, the design capacity is 12783 kN.
	>>> At 400.0 degrees C, the design capacity is 12538 kN.
	>>> At 500.0 degrees C, the design capacity is 9916 kN.
	>>> At 600.0 degrees C, the design capacity is 5839 kN.
	>>> At 700.0 degrees C, the design capacity is 2785 kN.
	"""

	## hardcoded values
	Ymfi = 1.0 # global resistance factor; recommended EC ?

	## broadcast handling

	if not SW_elementwise:
		if not isinstance(theta,np.ndarray):
			theta=np.array([theta])
		if not isinstance(fy,np.ndarray):
			fy=np.array([fy])
		fy=fy[:,np.newaxis]
		theta=theta[np.newaxis,:]

	## input handling
	rcol=np.sqrt(Icol/Acol) # [mm]; radius of gyration 

	## buckling resistance calculation according to 4.2.3.2 EC
	lambda_i = np.sqrt(E/fy)*np.pi
	Lambda_ = (Hfi/rcol)*1/lambda_i
	alpha = 0.65*np.sqrt(235/fy)
	Lambda_theta = Lambda_*np.sqrt(steel.ky_EC3(theta)/steel.kE_EC3(theta))
	fi_theta = 0.5*(1+alpha*Lambda_theta+Lambda_theta**2)
	chi_fi = 1/(fi_theta+np.sqrt(fi_theta**2-Lambda_theta**2))
	NRdfi=chi_fi*Acol*steel.ky_EC3(theta)*fy/Ymfi

	return np.squeeze(NRdfi) # squeeze to remove 1D array


def Temperature_LumpedMass_Unprotected(Tg,time,AV,hc,Ksh):
	""" Unprotected steel section temperature, according to section 4.2.5.1 EC;

	Parameters
	----------	
	Tg : np.array(n,m)
		[C], adiabatic surface temperature (gas temperature)
		with n the number of fire curves, and m the number of timesteps
	time : np.array(m,)
		[s], timesteps for the calculation
	hc : float
		[W/(m2K)], convection coefficient
	Av  : float
		[1/m], section factor for the unprotected section
	Ksh  : float
		[-], correction factor for the shadow effect

	Returns
	-------
	Ts : np.array(n,m)
	 [C],  temperature for unprotected steel section

	Example use
	-----------
	import numpy as np
	import magnelPy.SFE as sfe
	from magnelPy.SFE.MaterialProperties import Steel as steel
	from magnelPy.SFE.Capacity import EC3 as EC3
	# parameters steel temperature calculation
	AV = 107 # [1/m]; specific surface section
	AVb = 80 # [1/m]; specific surface boxed
	Ksh = 0.9*AVb/AV # [-]; shadow factor
	hc=35 # [W/m2K]; convection coefficient
	# fire curve definition
	O = 0.04; qf=780 # parameters EPFC
	timelist=np.arange(0,360*60+0.5,0.5) #[s]; timesteps
	Tg=np.array(sfe.FireCurve.EuroCodeParametric(timelist/60, O, qf))
	Ts=EC3.Temperature_LumpedMass_Unprotected(Tg,timelist,AV,hc,Ksh)
	times=[0,60,120,180,240,360] # [min]
	steps=np.array(times)*60*2
	for i,timepoint in enumerate(times):
		print("At {0:.0f} min, the temperature is {1:.0f} degrees C.".format(timepoint,Ts[steps[i]]))
	>>> At 0 min, the temperature is 20 degrees C.
	>>> At 60 min, the temperature is 861 degrees C.
	>>> At 120 min, the temperature is 709 degrees C.
	>>> At 180 min, the temperature is 356 degrees C.
	>>> At 240 min, the temperature is 72 degrees C.
	>>> At 360 min, the temperature is 20 degrees C.
	"""
	
	# hardcoded properties
	emissivity=0.7
	rho=steel.density_EC3() # [kg/m3] steel density (constant)
	
	# initialization
	try: 
		(n,m)=np.shape(Tg)
	except:
		Tg=Tg[np.newaxis,:]
		(n,m)=np.shape(Tg)
	Ts = np.zeros((n,m))
	newT=20*np.ones(n) # [C] starting temperature

	# forward integration
	for i in np.arange(m-1):
		Ts[:,i]=newT # assign temperature
		# steel property at elevated temperature
		cp=steel.cp_EC3(Ts[:,i]) # [J/kgK]; specific heat
		# heat flux
		heat_flux = (hc*(Tg[:,i]-Ts[:,i])+emissivity*5.67*10**-8*((Tg[:,i]+273.15)**4-(Ts[:,i]+273.15)**4)) # [W/m2K]
		newT=Ts[:,i]+Ksh*heat_flux*AV/rho/cp*(time[i+1]-time[i])
	Ts[:,i+1]=newT # assign last temperature
	
	return np.squeeze(Ts)

def Temperature_LumpedMass_Protected_const(Tg,time,AV,c_ins,rho_ins,l_ins,d_ins,n=1):
	""" Protected steel section temperature, according to section 4.2.5.2 EC;
	constant insulation properties

	Parameters
	----------	
	Tg : np.array(m,) or np.array(n,m)
		[C], adiabatic surface temperature (gas temperature)
		with n the number of fire curves, and m the number of timesteps
	time : np.array(m,)
		[s], timesteps for the calculation
	Av  : float or np.array(n,)
		[1/m], section factor for the unprotected section
	c_ins : float or np.array(n,)
		[J/kgK], insulation specific heat
	rho_ins : float or np.array (n,)
		[kg/m3], insulation density
	l_ins : float or np.array(n,)
		[W/mK], insulation conductivity
	d_ins : float or np.array(n,)
		[m], insulation thickness
	n   : float
		[-] number of simulations (explicitly transferred for ease of use)

	Returns
	-------
	Ts : np.array(n,m) or np.array(m,)
	 [C],  temperature for unprotected steel section

	Example use
	-----------
	import numpy as np
	import magnelPy.SFE as sfe
	from magnelPy.SFE.Capacity import EC3 as EC3
	from magnelPy.SFE.MaterialProperties import Steel as steel
	# parameters steel temperature calculation
	AV = 128 # [1/m]; specific surface section of the insulated steel member
	l_ins=0.2 # [W/mK]; insulation conductivity
	rho_ins=800 # [kg/m3]; insulation density
	c_ins=1000 # [J/kgK]; insulation specific heat
	d_ins=0.02 # [m]; insulation thickness
	# fire curve definition
	timelist=np.arange(0,360*60+0.5,0.5) #[s]; timesteps
	O = 0.04; qf=780 # parameters EPFC
	Tg=sfe.FireCurve.EuroCodeParametric(timelist/60, O, qf)
	# steel temperature calculation
	Ts=EC3.Temperature_LumpedMass_Protected_const(Tg,timelist,AV,c_ins,rho_ins,l_ins,d_ins)
	# output print
	times=[0,60,120,180,240,360] # [min]
	steps=np.array(times)*60*2
	for i,timepoint in enumerate(times):
		print("At {0:.0f} min, the temperature is {1:.0f} degrees C.".format(timepoint,Ts[steps[i]]))
	>>> At 0 min, the temperature is 20 degrees C.
	>>> At 60 min, the temperature is 448 degrees C.
	>>> At 120 min, the temperature is 619 degrees C.
	>>> At 180 min, the temperature is 521 degrees C.
	>>> At 240 min, the temperature is 274 degrees C.
	>>> At 360 min, the temperature is 54 degrees C.
	"""
	
	# hardcoded properties
	rho=steel.density_EC3() # [kg/m3] steel density (constant)
	
	# initialization
	m=len(time)
	if np.shape(Tg)!=(n,m):
		Tg=np.tile(Tg,(n,1))
	Ts = np.zeros((n,m))
	newT=20*np.ones(n) # [C] starting temperature

	# forward integration
	for i in np.arange(m-1):
		# assign temperature
		Ts[:,i]=newT
		dTg=Tg[:,i+1]-Tg[:,i] # [C]; temperature increase to next time step
		# material properties at elevated temperature
		cp=steel.cp_EC3(Ts[:,i]) # [J/kgK]; specific heat
		# steel temperature iteration
		phi=c_ins*rho_ins/(cp*rho)*d_ins*AV
		dTs=l_ins*AV/(d_ins*cp*rho)*(Tg[:,i]-Ts[:,i])/(1+phi/3)*(time[i+1]-time[i])-(np.exp(phi/10)-1)*dTg # [C], temperature increase
		delta_Ts=np.maximum(dTs,0,out=dTs,where=dTg>0) # [C], corrected temperature increase
		newT=Ts[:,i]+delta_Ts
	Ts[:,i+1]=newT # assign last temperature
	
	return np.squeeze(Ts)

def Temperature_LumpedMass_Protected_UserDef(Tg,time,AV,ins,d_ins,n=1,SW_update=False):
	""" Protected steel section temperature, according to section 4.2.5.2 EC;
	UserDefined temperature-dependent insulation properties

	Parameters
	----------	
	Tg : np.array(m,) or np.array(n,m)
		[C], adiabatic surface temperature (gas temperature)
		with n the number of fire curves, and m the number of timesteps
	time : np.array(m,)
		[s], timesteps for the calculation
	Av  : float or np.array(n,)
		[1/m], section factor for the unprotected section
	ins : object or list of objects with len(list)=n
		object of UserDefined class SFE\\MaterialProperties\\UserDefined;
		contains call for conductivity, specific heat and density (l_ins [W/(m*K)], c_ins [J/(kg*K)], rho_ins [kg/m3])
	d_ins : float or np.array(n,)
		[m], insulation thickness
	n   : float
		[-] number of simulations (explicitly transfer for ease of use)

	Returns
	-------
	Ts : np.array(n,m) or np.array(m,)
	 [C],  temperature for unprotected steel section

	Example use
	-----------
	import numpy as np
	import magnelPy.SFE as sfe
	from magnelPy.SFE.Capacity import EC3 as EC3
	from magnelPy.SFE.MaterialProperties import Steel as steel
	from magnelPy.SFE.MaterialProperties import SFRM as sfrm
	import magnelPy.SFE.MaterialProperties as mat
	# parameters steel temperature calculation
	AV = 128 # [1/m]; specific surface section of the insulated steel member
	T=np.arange(20,1250,10) # [C]; temperatures for array-wise insulation material definition
	k=sfrm.ki(T) # [W/mK]; sfrm conductivity - used as UserDefined input
	c=sfrm.cp(T) # [kg/m3]; sfrm specific heat - used as UserDefined input
	r=sfrm.rho(T) #  [J/kgK]; sfrm density - used as UserDefined input
	d_ins=0.02 # [m]; insulation thickness
	ins=mat.UserDefined(T,k,c,r) # UserDefined material initialization
	# fire curve definition
	timelist=np.arange(0,360*60+0.5,0.5) #[s]; timesteps
	O = 0.04; qf=780 # parameters EPFC
	Tg=sfe.FireCurve.EuroCodeParametric(timelist/60, O, qf)
	# steel temperature calculation
	Ts=EC3.Temperature_LumpedMass_Protected_UserDef(Tg,timelist,AV,ins,d_ins)
	# output print
	times=[0,60,120,180,240,360] # [min]
	steps=np.array(times)*60*2
	for i,timepoint in enumerate(times):
		print("At {0:.0f} min, the temperature is {1:.0f} degrees C.".format(timepoint,Ts[steps[i]]))
	>>> At 0 min, the temperature is 20 degrees C.
	>>> At 60 min, the temperature is 431 degrees C.
	>>> At 120 min, the temperature is 630 degrees C.
	>>> At 180 min, the temperature is 542 degrees C.
	>>> At 240 min, the temperature is 373 degrees C.
	>>> At 360 min, the temperature is 168 degrees C.
	"""
	
	# hardcoded properties
	rho=steel.density_EC3() # [kg/m3] steel density (constant)
	
	# initialization
	m=len(time)
	if np.shape(Tg)!=(n,m):
		Tg=np.tile(Tg,(n,1))
	Ts = np.zeros((n,m))
	newT=20*np.ones(n) # [C] starting temperature
	if type(ins)!=list: ins=[ins]
	c_ins=np.zeros(n)
	rho_ins=np.zeros(n)
	l_ins=np.zeros(n)

	# forward integration
	t1=timekeeper.time()
	for i in np.arange(m-1):
		# assign temperature
		Ts[:,i]=newT
		dTg=Tg[:,i+1]-Tg[:,i] # [C]; temperature increase to next time step
		# material properties at elevated temperature
		cp=steel.cp_EC3(Ts[:,i]) # [J/kgK]; specific heat
		avg_temp = (Tg[:,i] + Ts[:,i])/2 # average insulation temperature
		for j,ins_mat in enumerate(ins):
			c_ins[j] = ins_mat.cp(avg_temp[j]); rho_ins[j] = ins_mat.rho(avg_temp[j]); l_ins[j] = ins_mat.k(avg_temp[j])
		# steel temperature iteration
		phi=c_ins*rho_ins/(cp*rho)*d_ins*AV
		dTs=l_ins*AV/(d_ins*cp*rho)*(Tg[:,i]-Ts[:,i])/(1+phi/3)*(time[i+1]-time[i])-(np.exp(phi/10)-1)*dTg # [C], temperature increase
		delta_Ts=np.maximum(dTs,0,out=dTs,where=dTg>0) # [C], corrected temperature increase
		newT=Ts[:,i]+delta_Ts
		if SW_update and i%300==0 : 
			t2=timekeeper.time()
			print("Completed calc of {0:.0f}min in {1:.2f}s".format(i/60,t2-t1))
			t1=t2
	Ts[:,i+1]=newT # assign last temperature
	
	return np.squeeze(Ts)

#########
## AUX ##
#########