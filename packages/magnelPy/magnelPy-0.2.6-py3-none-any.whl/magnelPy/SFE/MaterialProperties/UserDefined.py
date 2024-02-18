"""MaterialProperties\\UserDefined
Notes
-----
Temperature-dependent properties for use in SFE.
"""

#############
## IMPORTS ##
#############

import numpy as np
import pandas as pd

############
## MODULE ##
############

class UserDefined(object):
	
	def __init__(self,temperature,conductivity,specific_heat,density):
		""" Initialization of User Defined Material

		Parameters
		----------	
		temperature : np.array (n,)
			Temperatures for which data is provided [°C]
		conductivity : np.array (n,)
			Conductivity for given temperature [W/(m*K)]
		specific_heat : np.array (n,)
			Specific heat for given temperature [J/(kg*K)]
		density : np.array (n,)
			Density for given temperature [kg/m3]

		Returns
		-------
		-
		
		Example use
		-----------
		import magnelPy.SFE.MaterialProperties as mat
		from magnelPy.SFE.MaterialProperties import SFRM as sfrm
		import numpy as np
		T=np.array([20,100,200,300,400,500,600])
		k=sfrm.ki(T)
		c=sfrm.cp(T)
		r=sfrm.rho(T)
		ins=mat.UserDefined(T,k,c,r)
		print(ins.data)
		>>>         k            c           r
			20   0.068407   821.710734  284.577910
			100  0.079424   924.583736  262.721108
			200  0.095388  1031.123125  253.898015
			300  0.114115  1117.924596  248.892572
			400  0.135986  1188.984460  245.408915
			500  0.161419  1247.403953  242.744797
			600  0.190863  1295.601815  240.592363
		"""
		aux=pd.DataFrame([conductivity,specific_heat,density],columns=temperature,index=['k','c','r'])
		self.data=aux.transpose()
		
	def rho(self,theta):
		""" Temperature-dependent density

		Parameters
		----------	
		theta : float or np.array (n,)
			Temperatures for which data is requested

		Returns
		-------
		Interpolated density [kg/m3]
		"""
		return np.interp(theta,self.data.index,self.data['r'].values,left=np.NAN,right=np.NAN)

	def cp(self,theta):
		""" Temperature-dependent specific heat

		Parameters
		----------	
		theta : float or np.array (n,)
			Temperatures for which data is requested

		Returns
		-------
		Interpolated specific heat [J/(kg*K)]
		"""
		return np.interp(theta,self.data.index,self.data['c'].values,left=np.NAN,right=np.NAN)
	
	def k(self,theta):
		""" Temperature-dependent conductivity

		Parameters
		----------	
		theta : float or np.array (n,)
			Temperatures for which data is requested

		Returns
		-------
		Interpolated conductivity [W/(m*K)]
		"""
		return np.interp(theta,self.data.index,self.data['k'].values,left=np.NAN,right=np.NAN)





