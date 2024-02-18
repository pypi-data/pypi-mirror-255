"""Fire definition

Notes
-----
The FireCurve module supports definition of temperature-time curves for SFE.
"""

#############
## IMPORTS ##
#############

import numpy as np
import pandas as pd
import math as m
from scipy.interpolate import interp1d

############
## MODULE ##
############

def ISO834(time):
	""" Return ISO834 gas temperature at specified times

	Parameters
	----------
	time :	np.array
		array of time instants [min]

	Returns
	-------
	fire :	np.array
		array of gas temperatures for time [C]

	Reference
	---------
	EN 1991-1-2:2002. Eurocode 1: Actions on structures - Part 1-2:
		General actions - Actions on structures exposed to fire, 3.2.1 (p24) 

	Examples
	--------
	>>> import numpy as np
	>>> import magnelPy.SFE as sfe
	>>> time = np.arange(0,120+1,1)
	>>> fire = sfe.FireCurve.ISO834(time)
	>>> print(np.array([time[[0,30,60,90,120]],
		np.around(fire[[0,30,60,90,120]],0)]))
	[[   0.   30.   60.   90.  120.]
 	[  20.  842.  945. 1006. 1049.]]
	"""
	return 20+345*np.log10(8*time+1)


def ASTM(time):
	""" Return ASTM-E119 gas temperature at specified times

	Parameters
	----------
	time :	np.array
		array of time instants [min]

	Returns
	-------
	fire :	np.array
		array of gas temperatures for time [C]

	Reference
	---------
	ASTM E119-00a: Fire Tests of Building Construction and Materials
	via https://www.nrc.gov/docs/ML0516/ML051640380.pdf

	"""
	t_list = np.array([0,5,10,20,30,60,90,120,180,240,300,360,420,480]) # [min]
	T_list = np.array([68,1000,1300,1462,1550,1700,1792,1850,1925,2000,2075,2150,2225,2300]) # [°F]
	T_list = (T_list-32)*5/9 # conversion °F -> °C
	T_data = interp1d(t_list,T_list)
	return T_data(time)


def EuroCodeParametric(time, openingFactor, fireLoadDensity, thermalInertia=1450, length=10, width=10, height=3, t_lim = 20, Reitgruber=False):
	""" Return Eurocode Parametric fire gas temperature at specified times

	Parameters
	----------
	time :	np.array
		array of time instants [min]

	openingFactor : float
		opening factor (typically) between 0.02 and 0.2 [m1/2]

	fireLoadDensity : float
		fire load density related to the surface area [MJ/m2]

	thermalInertia : float
		thermal interia of the compartment, typically between 100 and 2200 [J/m2 s1/2 K] (default = 1450 J/m2 s1/2 K)

	length, width, height : float
		dimensions of a rectangular compartment [m] (default = 10/10/3 m)

	t_lim : float
		factor which indicates the fire growth rate [min] (default = 20 min)
		
	Reitgruber : Boolean
		Take into account correction proposed by Reitguber et al. * (default = False)

	Returns
	-------
	fire :	np.array
		array of gas temperatures for time [C]

	Reference
	---------
	EN 1991-1-2:2002. Eurocode 1: Actions on structures - Part 1-2:
	  Annex A - Parametric temperature-time curves (p30-32)
   *Reitgruber, S., Blasi, C. Di and Franssen, J. (2006) ‘Some Comments on the Parametric Fire Model of Eurocode 1’, 
	    Conference on Fire in Enclosures, (January 2006), pp. 1–25.
	
	Examples
	--------
	>>> import numpy as np
	>>> import magnelPy.SFE as sfe
	>>> time = np.arange(0,120+1,1)
	>>> fire = sfe.FireCurve.EuroCodeParametric(time,0.05,500,1450,10,10,3)
	"""

	# calculation of other parameters required to determine the shape of the heating a cooling phase curves
	A_f = length*width # [m2] floor area
	A_t = 2*A_f + 2*height*(length+width) # [m2] total compartment surface area
	qt_d = fireLoadDensity*A_f/A_t # [MJ/m2] design value of the fire load density related to the total surface area A_t
	Of_lim = 0.0001*qt_d/(t_lim/60) # [m1/2] adjusted opening factor in case of fuel controlled fire
	t_max = max(t_lim/60, 0.0002*qt_d/openingFactor) # [hours] time at which the maximum temperature in the heating phase occurs
	if Reitgruber: 
		Of_lim = 0.00014*qt_d/(t_lim/60)
		t_max = max(t_lim/60, 0.00014*qt_d/openingFactor)
	Lambda = ((openingFactor/thermalInertia)**2)/((0.04/1160)**2) # [-] time scale parameter
	k = 1 + ((openingFactor-0.04)/0.04)*((qt_d-75)/75)*((1160-thermalInertia)/1160) if (openingFactor > 0.04 and qt_d > 75 and thermalInertia <1160) else 1
	Lambda_lim = k*((Of_lim/thermalInertia)**2)/((0.04/1160)**2) # [-] time scale parameter in case of fuel controlled fire
	Lambda_use = Lambda_lim if t_max==t_lim/60 else Lambda
	t_max_st = t_max*Lambda if t_max > t_lim/60 else t_max*Lambda_lim
	theta_max = 20+1325*(1-0.324*m.exp(-0.2*t_max*Lambda_use)-0.204*m.exp(-1.7*t_max*Lambda_use)-0.472*m.exp(-19*t_max*Lambda_use)) # time temperature curve for heating phase (EN 1991-1-2 - Formula A.1)
	x = 1 if t_max>t_lim/60 else t_lim/60*Lambda/(t_max*Lambda_use)
	
	# calcalate tempertures [°C]
	temp_list = []
	for t in time:
		if t/60 <= t_max: # heating phase
			temp_list.append(20+1325*(1 - 0.324*m.exp(-0.2*(t/(60/Lambda_use))) - 0.204*m.exp(-1.7*(t/(60/Lambda_use))) - 0.472*m.exp(-19*(t/(60/Lambda_use)))))
		else: # cooling phase
			if t_max_st < 0.5:
				temp_list.append(max(20,theta_max - 625*(t/60*Lambda - t_max_st*x))) # (EN 1991-1-2 - Formula A.11a)
			else:
				if t_max_st < 2:
					temp_list.append(max(20,theta_max - 250*(3 - t_max_st)*(t/60*Lambda - t_max_st*x))) # (EN 1991-1-2 - Formula A.11b)
				else:
					temp_list.append(max(20,theta_max - 250*(t/60*Lambda - t_max_st*x))) # (EN 1991-1-2 - Formula A.11c)
	return temp_list

def EPFC(time, openingFactor, fireLoadDensity, thermalInertia=1450, length=10, width=10, height=3, t_lim = 20, Reitgruber=False):
	""" Return Eurocode Parametric fire gas temperature at specified times - vectorized function

	Parameters
	----------
	time :	np.array (m,)
		array of time instants [min]

	openingFactor : np.array (n,)
		array of opening factor (typically) between 0.02 and 0.2 [m1/2]

	fireLoadDensity : np.array (n,)
		array of fire load density related to the surface area [MJ/m2]

	thermalInertia : float or np.array (n,)
		thermal interia of the compartment, typically between 100 and 2200 [J/m2 s1/2 K] (default = 1450 J/m2 s1/2 K)

	length, width, height : float or np.array (n,)
		dimensions of a rectangular compartment [m] (default = 10/10/3 m)

	t_lim : float or np.array (n,)
		factor which indicates the fire growth rate [min] (default = 20 min)
		
	Reitgruber : Boolean
		Take into account correction proposed by Reitguber et al. * (default = False)

	Returns
	-------
	fire :	np.array(n,m)
		array of gas temperatures for time [C]

	Reference
	---------
	EN 1991-1-2:2002. Eurocode 1: Actions on structures - Part 1-2:
	  Annex A - Parametric temperature-time curves (p30-32)
	Reitgruber, S., Blasi, C. Di and Franssen, J. (2006) ‘Some Comments on the Parametric Fire Model of Eurocode 1’, 
	    Conference on Fire in Enclosures, (January 2006), pp. 1–25.
	
	Examples
	--------
	import numpy as np
	import magnelPy.SFE as sfe
	time = np.arange(0,120+1,1)
	O=np.array([0.04,0.05])
	qf=np.array([600,700])
	fire = sfe.FireCurve.EPFC(time,O,qf)
	timeprint=[30,60,90,120]
	for t in timeprint:
    	print("At {0:.0f} min, the temperature is {1:.0f} degrees C for curve1 and {2:.0f} degrees for curve2.".format(t,fire[0,t],fire[1,t]))
	>>> At 30 min, the temperature is 784 degrees C for curve1 and 841 degrees for curve2.
	>>> At 60 min, the temperature is 843 degrees C for curve1 and 857 degrees for curve2.
	>>> At 90 min, the temperature is 651 degrees C for curve1 and 592 degrees for curve2.
	>>> At 120 min, the temperature is 459 degrees C for curve1 and 326 degrees for curve2.
	"""	
	## check np.array
	if not isinstance(openingFactor,np.ndarray) or not isinstance(fireLoadDensity,np.ndarray):
		raise NameError("This function requires np.array (n,) for both the opening factor and fire load density.")

	## Preparatory steps
	A_f = length*width # [m2] floor area
	A_t = 2*A_f + 2*height*(length+width) # [m2] total compartment surface area
	qt_d = fireLoadDensity*A_f/A_t # [MJ/m2] design value of the fire load density related to the total surface area A_t
	if Reitgruber:
		Of_lim = 0.00014*qt_d/(t_lim/60)
		t_max = np.maximum(t_lim/60, 0.00014*qt_d/openingFactor)
	else: 
		Of_lim = 0.0001*qt_d/(t_lim/60) # [m1/2] adjusted opening factor in case of fuel controlled fire
		t_max = np.maximum(t_lim/60, 0.0002*qt_d/openingFactor)
	Lambda = ((openingFactor/thermalInertia)**2)/((0.04/1160)**2) # [-] time scale parameter
	k=1+((openingFactor-0.04)/0.04)*((qt_d-75)/75)*((1160-thermalInertia)/1160)*(openingFactor > 0.04)*(qt_d > 75)*(thermalInertia <1160)
	Lambda_lim = k*((Of_lim/thermalInertia)**2)/((0.04/1160)**2) # [-] time scale parameter in case of fuel controlled fire
	Lambda_use = np.where(t_max<=t_lim/60,Lambda_lim,Lambda)
	t_max_st = t_max*Lambda_use
	theta_max = 20+1325*(1-0.324*np.exp(-0.2*t_max_st)-0.204*np.exp(-1.7*t_max_st)-0.472*np.exp(-19*t_max_st)) # time temperature curve for heating phase (EN 1991-1-2 - Formula A.1)
	x = np.where(t_max>t_lim/60,1,t_lim/60*Lambda/(t_max*Lambda_use))
	
	## temperature-time calculation
	n=len(theta_max)
	time=time[np.newaxis,:]
	Lambda_use=Lambda_use[:,np.newaxis]; Lambda=Lambda[:,np.newaxis]; theta_max=theta_max[:,np.newaxis]
	# heating phase curve
	Tgh=20+1325*(1-0.324*np.exp(-0.2*time/60*Lambda_use)-0.204*np.exp(-1.7*time/60*Lambda_use)-0.472*np.exp(-19*time/60*Lambda_use))
	# cooling phase curve
	xi=[0.5,2]; yi=[625,250]; rate=np.reshape(np.interp(t_max_st,xi,yi),(n,1))
	Tgc=theta_max - rate*(time/60*Lambda - np.reshape(t_max_st*x,(n,1)))
	# assign temperatures, with reference (minimum) temperature of 20 degrees
	Tg=np.maximum(np.where(Tgc>theta_max,Tgh,Tgc),20)
	
	return Tg 

def HRR_t2(alpha,qf,Af,HRR_perA,Av,hv,chi=1.0,decay_ratio=0.3,dt = 1.):
    """ Heat Release Rate according Annex E of EN 1991-1-2; updated for oxygen-based maximum compartment heat release

    Parameters
    ----------	
    alpha : float
            fire growth rate [W/s2]

    qf : float
            fire load per unit of floor area [J/m2]

    Af : float
            floor area [m2]

    HRR_perA : float
            maximum heat release rate per unit of floor area for fuel controlled fires [W/m2]

    Av : float
            total ventilation area [m2]
            
    hv : float
            (equivalent) height of ventilation area [m]
            
    chi : float
            combustion factor [-]; default value 0.8

    decay_ratio : float
            partim of fuel load consumed in the decay phase [-]; default value 0.3
            
    dt : float
            time step [s]; default value 1.
        
    Returns
    -------
    fire : pd.Series
        index: time [s]
        values: heat release rate [W]
        
    t_cool_end : float
        time since start of fire at which total fuel is consumed

    Note
    -------
    Initial temperature 20°C
    
    Example use
    -----------
    ## Compartment characteristics
	L = 12      # [m]
	B = 12      # [m]
	H = 3.4     # [m]
	H_o = 1.7 # [m]
	A_o = H_o * 7.2 * 2  # [m²]

	## Fire characteristics
	alpha = 30 # [W/s2]; growth rate
	qf = 680*10**6 # [J/m2]; fire load density
	HRR_perA  = 250*10**3 # [W/m2]; fuel controlled HRR per unit area

	## calc parameters
	dt=10 # [s]; timestep for the calculation
	chi=1 # [-]; combustion effiency
	decay_fraction = 0.3 # [-]; fraction of fuel load consumed in the decay phase

	## HRR calculation
	fire,dur = sfe.FireCurve.HRR_t2(alpha, qf, L*B, HRR_perA, A_o, H_o,chi=1.0,decay_ratio=decay_fraction,dt=dt)

	### sanity check
	print("Total heat released is \t\t\t\t\t\t{0:.1f} MJ/m2".format(np.sum(fire.values*dt)*10**-6/(L*B)))
	print("Input fuel load, corrected for combustion efficiency, is \t{0:.1f} MJ/m2".format(qf*10**-6*chi))

	>>> Total heat released is 										680.0 MJ/m2
	>>> Input fuel load, corrected for combustion efficiency, is 	680.0 MJ/m2

    """  
    ## initialization
    # effective fuel load, considering combustion efficiency
    qf_eff=chi*qf*Af # [J]; effective total fuel load
    
    ## HRR characteristics
    #calculating maximum HRR - fuel controlled
    q_max_fuel = HRR_perA*Af # [W]
    #calculating maximum HRR - ventilation controlled     
    Heff_air=3*10**3 # [J/g]; effective heat of combustion of air
    AH=Av*np.sqrt(hv) # [m5/2]
    Q_air=0.5*AH*10**3 # [g/s]; inflow of air through opening 
    q_max_vent=Q_air*Heff_air # [W]
    q_max = min(q_max_fuel,q_max_vent) # [W]
    
    ## phases of the HRR curve
    qf_decay = decay_ratio* qf_eff # [J]; fuel load combusted in the 
    dur_cool = 2*qf_decay/q_max # [s]; cooling duration - RVC : combustion efficiency considered, OK ?
    dur_growth = np.sqrt(q_max/alpha) # [s]; duration of growth phase (neglecting possibility of earlier start of decay phase)
    qf_growth=alpha/3*(dur_growth)**3 # [J]; fuel load combusted in the growth phase (neglecting possible earlier start of decay phase)
    qf_steady=max(qf_eff-qf_growth-qf_decay,0) # [J]; fuel load consumed in the fully developed phase
    if qf_steady==0: # fully developed stage could not be achieved - early start of decay phase; reconsider calc
        dur_steady = 0 # [s]
        qf_growth = qf_eff-qf_decay # [J]
        dur_growth = (3*qf_growth/alpha)**(1/3) # [s]
        q_max=alpha*dur_growth**2 # [W]; max HRR achieved considering early start of decay phase
        dur_cool = 2*qf_decay/q_max # [s]; cooling duration; duration of growth phase; note that sticking to 30% fuel consumed in decay implies a longer decay duration for lower q_max !!
    else:
        dur_steady = qf_steady/q_max # [s]
    t_steady = dur_growth # [s]; time at which steady state is achieved
    t_cool = t_steady + dur_steady # [s]; time at which decay phase starts
    t_cool_end = t_cool + dur_cool # [s]; time at which decay phase ends 
    
    # HRR
    t = np.arange(0,t_cool_end+dt,dt) # time discretization
    q_fire = q_max*np.ones(t.shape) # [W]; array initialization at steady state value
    q_growth=alpha*(t)**2
    q_fire[t<t_steady]=q_growth[t<t_steady]
    if dur_cool == 0: q_decay = np.zeros(t.shape)
    else: q_decay=q_max*(1-(t-t_cool)/(t_cool_end-t_cool))
    q_fire[t>t_cool]=q_decay[t>t_cool]
    q_fire=np.maximum(q_fire,0)
    
    ## output
    fire=pd.Series(q_fire,index=t)
    
    return fire, t_cool_end



#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":

	print("testing")