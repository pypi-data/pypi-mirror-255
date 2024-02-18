import numpy as np 
import sys

import magnelPy 
import matplotlib.pyplot as plt


def aic_2_param(data,dists=["N","LN","GM","GU"]):
	""" Calculates Akaike information criterion (AIC) criteria of different kind of theoretical distributions
	Fitting of the distribution is done only based on the mean value and standard distribution
	That way the number of parametars "k" is always equal to 2 and ignored and AIC is calculated only based on the loglikelihood values
	AIC is only supposed to be used to compare difrent models so this modification is ok

	Parameters
	----------	
	data : 1D numpy array or list
		data for which the distributins are fitted

	dists : list of strings
		distrbutions for which the AIC is calculated

		"N":	Normal
		"LN": 	Lognormal
		"GM": 	Gamma
		"GU": 	Gumbel
		"B": 	Beta 4,4 default
		"W": 	Weibull
		"IG": 	Inverese Gauss
		"LG": 	Logistic
		"LLG": 	LogLogistic
		"R": 	Rican
		"NAK": 	Nakagami
		"BS": 	Birnbaum Saunders

	Returns
	-------
	loglike : numpy array
		array with the AIC values
	 
	"""
	
	m=np.mean(data)
	s=np.std(data)
		
	
	loglike=np.zeros(len(dists))
	num=0
	dists=np.array(dists)
	if np.any(dists=="N"):#Normal
		loglike[num]=np.sum(np.log(statFunc.f_Normal(data,m,s)))
		
		num+=1
	if np.any(dists=="LN"):#Lognormal
		loglike[num]=np.sum(np.log(statFunc.f_Lognormal(data,m,s)))
		num+=1
	if np.any(dists=="GM"):#Gamma
		loglike[num]=np.sum(np.log(statFunc.f_Gamma(data,m,s)))
		num+=1
	if np.any(dists=="GU"):#Gumbel
		loglike[num]=np.sum(np.log(statFunc.f_Gumbel(data,m,s)))
		num+=1
	if np.any(dists=="B"): #Beta 4,4 default 
		loglike[num]=np.sum(np.log(statFunc.f_Beta_ab(data,4,4,m,s)))
		num+=1
	if np.any(dists=="W"): #Weibull
		loglike[num]=np.sum(np.log(statFunc.f_Weibull(data,m,s)))
		num+=1
	if np.any(dists=="IG"): #Inverese Gauss
		loglike[num]=np.sum(np.log(statFunc.f_InvGauss(data,m,s)))
		num+=1
	if np.any(dists=="LG"): #Logistic
		loglike[num]=np.sum(np.log(statFunc.f_Logistic(data,m,s)))
		num+=1
	if np.any(dists=="LLG"): #LogLogistic
		loglike[num]=np.sum(np.log(statFunc.f_LogLogistic(data,m,s)))
		num+=1
	if np.any(dists=="R"): #Rican
		loglike[num]=np.sum(np.log(statFunc.f_Rican(data,m,s)))
		num+=1
	if np.any(dists=="NAK"): #Nakagami
		loglike[num]=np.sum(np.log(statFunc.f_Nakagami(data,m,s)))
		num+=1
	if np.any(dists=="BS"): #Birnbaum Saunders
		loglike[num]=np.sum(np.log(statFunc.f_Birnbaum_Saunders(data,m,s)))
		num+=1
		
	return -loglike

def AIC_Norm(data):
	""" Calculates Akaike information criterion (AIC) criteria for normal distributions
	
	Parameters
	----------	
	data : 1D numpy array or list
		data for which the distributin is fitted
	
	Returns
	-------
	AIC : float
		AIC value
	loc,scale : floats
		distribution parameters

	Note
	-------
	In case of the error it returns all "NaN"
	 
	"""
	try:
		loc,scale=stats.norm.fit(data)
		AIC=stats.norm.logpdf(data,loc,scale).sum()+2*2
	
	except:
		AIC,loc,scale=[float('NaN'),float('NaN'),float('NaN')]
	
	return AIC,loc,scale

def AIC_Lognormal(data):
	""" Calculates Akaike information criterion (AIC) criteria for lognormal distributions
	
	Parameters
	----------	
	data : 1D numpy array or list
		data for which the distributin is fitted
	
	Returns
	-------
	AIC : float
		AIC value
	s,loc,scale : floats
		distribution parameters

	Note
	-------
	In case of the error it returns all "NaN"
	 
	"""
	try:
		s,loc,scale=stats.lognorm.fit(data)
		AIC=stats.lognorm.logpdf(data,s,loc,scale).sum()+2*3
	except:
		AIC,s,loc,scale=[float('NaN'),float('NaN'),float('NaN'),float('NaN')]
	
	return AIC,s,loc,scale

def AIC_Gamma(data):
	""" Calculates Akaike information criterion (AIC) criteria for gamma distributions
	
	Parameters
	----------	
	data : 1D numpy array or list
		data for which the distributin is fitted
	
	Returns
	-------
	AIC : float
		AIC value
	a,loc,scale : floats
		distribution parameters

	Note
	-------
	In case of the error it returns all "NaN"
	 
	"""
	try:
		a,loc,scale=stats.gamma.fit(data,floc=0)
		print(loc)
		AIC=stats.gamma.logpdf(data,a,loc,scale).sum()+2*3
	except:
		AIC,a,loc,scale=[float('NaN'),float('NaN'),float('NaN'),float('NaN')]
		
	return AIC,a,loc,scale

def AIC_Nakagami(data):
	""" Calculates Akaike information criterion (AIC) criteria for Nakagami distributions
	
	Parameters
	----------	
	data : 1D numpy array or list
		data for which the distributin is fitted
	
	Returns
	-------
	AIC : float
		AIC value
	a,loc,scale : floats
		distribution parameters

	Note
	-------
	In case of the error it returns all "NaN"
	 
	"""
	try:
		a,loc,scale=stats.nakagami.fit(data)
		AIC=stats.nakagami.logpdf(data,a,loc,scale).sum()+2*3
	except:
		AIC,a,loc,scale=[float('NaN'),float('NaN'),float('NaN'),float('NaN')]
	
	return AIC,a,loc,scale

def AIC_Gumbel(data):
	""" Calculates Akaike information criterion (AIC) criteria for Gumbel distributions
	
	Parameters
	----------	
	data : 1D numpy array or list
		data for which the distributin is fitted
	
	Returns
	-------
	AIC : float
		AIC value
	loc,scale : floats
		distribution parameters

	Note
	-------
	In case of the error it returns all "NaN"
	 
	"""
	try:
		loc,scale=stats.gumbel_r.fit(data)
		AIC=stats.gumbel_r.logpdf(data,loc,scale).sum()+2*2
	except:
		AIC,loc,scale=[float('NaN'),float('NaN'),float('NaN')]
	
	return AIC,loc,scale

def AIC_Beta(data,alpha=4,beta=4):
	""" Calculates Akaike information criterion (AIC) criteria for beta distributions with fixed values of alpha and beta
		
	Parameters
	----------	
	data : 1D numpy array or list
		data for which the distributin is fitted
	
	Returns
	-------
	AIC : float
		AIC value
	a,b,loc,scale : floats
		distribution parameters

	Note
	-------
	In case of the error it returns all "NaN"
	 
	"""
	try:
		a,b,loc,scale=stats.beta.fit(data,fix_a=alpha,fix_b=beta)
		AIC=stats.beta.logpdf(data,a,b,loc=loc,scale=scale).sum()+2*2
	
	except:
		AIC,a,b,loc,scale=[float('NaN'),float('NaN'),float('NaN'),float('NaN'),float('NaN')]

	return AIC,a,b,loc,scale

def AIC_Weibull(data):
	""" Calculates Akaike information criterion (AIC) criteria for Weibull distributions
	
	Parameters
	----------	
	data : 1D numpy array or list
		data for which the distributin is fitted
	
	Returns
	-------
	AIC : float
		AIC value
	c,loc,scale : floats
		distribution parameters

	Note
	-------
	In case of the error it returns all "NaN"
	 
	"""
	try:
		c,loc,scale=stats.weibull_min.fit(data)
		AIC=stats.weibull_min.logpdf(data,c,loc,scale).sum()+2*3
	
	except:
		AIC,c,loc,scale=[float('NaN'),float('NaN'),float('NaN'),float('NaN')]
		
	return AIC,c,loc,scale

def aic_full(data,dists=["N","LN","GM","GU"]):
	""" Calculates Akaike information criterion (AIC) criteria of different kind of theroetical distributions
	

	Parameters
	----------	
	data : 1D numpy array or list
		data for which the distributins are fitted

	dists : list of strings
		distrbutions for which the AIC is calculated

		"N":	Normal
		"LN": 	Lognormal
		"GM": 	Gamma
		"GU": 	Gumbel
		"B": 	Beta 4,4 default
		"W": 	Weibull
		"NAK": 	Nakagami
		
	Returns
	-------
	loglike : numpy array
		array with the AIC values
	 
	"""
		
	loglike=np.zeros(len(dists))
	num=0
	dists=np.array(dists)
	if np.any(dists=="N"):#Normal
		loglike[num],_,_=AIC_Norm(data)
		num+=1
	if np.any(dists=="LN"):#Lognormal
		loglike[num],_,_,_=AIC_Lognormal(data)
		num+=1
	if np.any(dists=="GM"):#Gamma
		loglike[num],_,_,_=AIC_Gamma(data)
		num+=1
	if np.any(dists=="GU"):#Gumbel
		loglike[num],_,_=AIC_Gumbel(data)
		num+=1
	if np.any(dists=="B"): #Beta 4,4 default 
		loglike[num],_,_,_,_=AIC_Beta(data)
		num+=1
	if np.any(dists=="W"): #Weibull
		loglike[num],_,_,_=AIC_Weibull(data)
		num+=1
	if np.any(dists=="NAK"): #Nakagami
		loglike[num],_,_,_=AIC_Nakagami(data)
		num+=1
		
	return -loglike

if __name__ == "__main__":
	
	# print('Test')
	# Pn_input =np.load("Pn8.npy")
	# names=[r'$E_{Confab}$',r'$E_{H&S}$',r'$E_{Iqbal}$',r'$E_{Confab}$',r'$E_{H&S}$',r'$E_{Iqbal}$',r'$E_{Confab}$',r'$E_{H&S}$']
	# #ploty_pdf(Pn_input[:,:3],names)
	# ploty_cdf(Pn_input[:,:6],names,BW=True,figname='blabla')
	# plt.show()
	test_data=np.random.normal(3,0.5,10*10)
	plt.figure()
	AIC=aic_2_param(test_data,dists=["N","LN","GM","GU"])
	print(AIC)
	plt.bar(np.arange(len(AIC)),AIC,tick_label=["N","LN","GM","GU"])

	# plt.figure()
	# AIC2=aic_full(test_data,dists=["N","LN","GM","GU"])
	# print(AIC2)
	# plt.bar(np.arange(len(AIC2)),AIC2,tick_label=["N","LN","GM","GU"])
	plt.show()