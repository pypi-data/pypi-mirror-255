#__author__ = "magnelPy"
# test 2

####################
## MODULE IMPORTS ##
####################

from copy import deepcopy
from scipy.stats import uniform
from scipy.stats import gumbel_r
from scipy.stats import norm
from scipy.stats import lognorm
from scipy.stats import t
from scipy.stats import beta as Beta
from scipy.stats import gamma
from scipy.stats import invgauss
from scipy.stats import logistic
from scipy.stats import fisk
from scipy.stats import rice
from scipy.stats import nakagami
from scipy.stats import fatiguelife

from scipy.optimize import minimize
from scipy.integrate import quad
from scipy.stats import weibull_min

from scipy.optimize import fsolve

import math
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

##############
## FUNCTION ##
##############

## inverse CDF function ##
##########################
#------------------------------------------------------------------------------------------------------------
# realization x for stochastic variable X, given quantile r
#
# Input (in function of distribution):
# 	r = quantile (0,1)
#	m = mean value X
#	s = standard deviation X
# 	a = lower bound distribution
# 	b = uppper bound distribution
#	sm = pd.Series with mean value of constitutent variables Xi
#	ss = pd.Series with standard deviations of constituent variables Xi
#	sP = pd.Series with probabilities of constituent variables Xi
#
# Output:
#	realization x
##------------------------------------------------------------------------------------------------------------

def Finv_Uniform(r,a,b):
	"""Return realization x~U[a,b] for quantile r """
	#--------------------------------------------------------------------------------------------------------
	# X ~ uniform distribution in range (a,b)
	# Input: r,a,b
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	return uniform.ppf(r,a,b-a)

def Finv_Gumbel(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Gumbel distribution
	# Input: r,m,s
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	scale,loc=p_Gumbel(m,s)
	return gumbel_r.ppf(r,loc,scale)

def Finv_Normal(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Normal distribution
	# Input: r,m,s
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	return norm.ppf(r,m,s)

def Finv_Lognormal_truncated(r,m,s,b):
	#--------------------------------------------------------------------------------------------------------
	# X ~ truncated lognormal distribution
	# Input: r,m,s,b (b = upper bound)
	#--------------------------------------------------------------------------------------------------------
	sln,mln=p_Lognormal(m,s)
	r2=r*F_Lognormal(b,m,s)
	return lognorm.ppf(r2,sln,0,np.exp(mln))

def Finv_Lognormal(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Lognormal distribution
	# Input: r,m,s
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	sln,mln=p_Lognormal(m,s)
	return lognorm.ppf(r,sln,0,np.exp(mln))

def Finv_MixedLN(r,sm,ss,sP):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Mixed-Lognormal distribution, with lognormal constituents Xi
	# Input: r,sm,ss,SP
	#--------------------------------------------------------------------------------------------------------
	ssln,smln=p_Lognormal(sm,ss) # parameters of constituents
	if isinstance(r,np.ndarray):
		x=deepcopy(r)
		for i,ri in enumerate(r): # note: for-loop not optimized - TIME CONSUMING
			x0=lognorm.ppf(ri,ssln,0,np.exp(smln)) # Finv for constituent in isolation
			x0=x0.dot(sP) # starting value as weighted average
			myargstuple=(ri,ssln,smln,sP)
			res=minimize(Finv_MixedLN_cost,x0,myargstuple)
			x[i]=res.x[0]
	else:
		x0=lognorm.ppf(r,ssln,0,np.exp(smln)) # Finv for constituent in isolation
		x0=x0.dot(sP) # starting value as weighted average
		myargstuple=(r,ssln,smln,sP)
		res=minimize(Finv_MixedLN_cost,x0,myargstuple)
		x=res.x[0]
	return x

def Finv_t(r,df):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Standardized Student's t distribution
	# Input: r,df
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	return t.ppf(r,df)

def Finv_Beta_01(r,alpha,beta):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Beta distribution (0,1)
	# Input: r,alpha,beta
	#--------------------------------------------------------------------------------------------------------
	return Beta.ppf(r,alpha,beta)

def Finv_Beta_ab(r,m,s,alpha,beta):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Beta distribution (a,b)
	# Input: r,m,s,alpha,beta
	# cfr. W&S p.5.28
	#--------------------------------------------------------------------------------------------------------
	a,b=Beta_lim(m,s,alpha,beta)
	y=Finv_Beta_01(r,alpha,beta) 
	return a+(b-a)*y

def Finv_Gamma(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Gamma distribution
	# Input: r,m,s
	# rvc 01/2019
	#--------------------------------------------------------------------------------------------------------
	a,scale=p_Gamma(m,s)
	return gamma.ppf(r,a,loc=0,scale=scale)

def Finv_Weibull(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Gamma distribution
	# Input: r,m,s
	# rvc 01/2019
	#--------------------------------------------------------------------------------------------------------
	c,scale=p_Weibull(m,s)
	return weibull_min.ppf(r,c,loc=0,scale=scale)

def Finv_InvGauss(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Inverse Gauss distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	mi,scale=p_InvGauss(m,s)
	return invgauss.ppf(r,mi,loc=0,scale=scale)

def Finv_Logistic(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Logistic distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	loc,scale=p_Logistic(m,s)
	return logistic.ppf(r,loc=loc,scale=scale)

def Finv_LogLogistic(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ LogLogistic distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	c,scale=p_LogLogistic(m,s)
	return fisk.ppf(r,c,loc=0,scale=scale)

def Finv_Rican(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Rican distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	b,scale=p_Rican(m,s)
	return rice.ppf(r,b,loc=0,scale=scale)

def Finv_Nakagami(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Nakagami distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	ni,scale=p_Nakagami(m,s)
	return nakagami.ppf(r,ni,loc=0,scale=scale)

def Finv_Birnbaum_Saunders(r,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Birnbaum_Saunders distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	c,scale=p_Birnbaum_Saunders(m,s)
	return fatiguelife.ppf(r,c,loc=0,scale=scale)

## CDF function ##
##################
#------------------------------------------------------------------------------------------------------------
# quantile r for stochastic variable X, given realization x
#
# Input (in function of distribution):
# 	x = realization X
#	m = mean value X
#	s = standard deviation X
#	sm = pd.Series with mean value of constitutent variables Xi
#	ss = pd.Series with standard deviations of constituent variables Xi
#	sP = pd.Series with probabilities of constituent variables Xi
#
# Output:
#	quantile r
#------------------------------------------------------------------------------------------------------------

def F_Normal(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Normal distribution
	# Input: x,m,s
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	return norm.cdf(x,m,s)

def F_Lognormal(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Lognormal distribution
	# Input: x,m,s
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	# multi-x multi LN processing
	if isinstance(x,pd.Series) and isinstance(m,pd.Series) and isinstance(s,pd.Series):
		tmp=x.values.repeat(len(s))
		tmp=tmp.reshape(len(x),len(s))
		x=pd.DataFrame(tmp,index=x.index,columns=s.index)
	sln,mln=p_Lognormal(m,s)
	return lognorm.cdf(x,sln,0,np.exp(mln))

def F_MixedLN(x,sm,ss,sP):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Mixed-Lognormal distribution, with lognormal constituents Xi
	# Input: x,sm,ss,sP
	#--------------------------------------------------------------------------------------------------------
	sr=F_Lognormal(x,sm,ss)
	return sr.dot(sP)

def F_MixedLN_trial(x,sm,ss,sP):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Mixed-Lognormal distribution, with lognormal constituents Xi
	# Input: x,sm,ss,sP
	#
	# Date: 18/01/2018
	#--------------------------------------------------------------------------------------------------------
	ssln,smln=p_Lognormal(sm,ss) # parameters of constituents
	if isinstance(x,np.ndarray):
		out=np.zeros(x.shape)
		for ci in sm.index:
			sri=F_Lognormal(x,sm[ci],ss[ci])
			out+=sri*sP[ci]
		return out
	else:
		sr=F_Lognormal(x,sm,ss)
		return sr.dot(sP)

def F_Gumbel(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Gumbel distribution
	# Input: x,m,s
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	scale,loc=p_Gumbel(m,s)
	return gumbel_r.cdf(x,loc,scale)

def F_Beta_01(x,alpha,beta):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Beta distribution (0,1)
	# Input: x, alpha, beta
	#--------------------------------------------------------------------------------------------------------
	return Beta.cdf(x,alpha,beta)

def F_Beta_ab(x,alpha,beta,a,b):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Beta distribution (a,b)
	# Input: x, alpha, beta, a, b
	# cfr. W&S p.5.28
	#--------------------------------------------------------------------------------------------------------
	y=(x-a)/(b-a)
	return F_Beta_01(y,alpha,beta)

def F_Beta_ms(x,m,s,alpha,beta):
	# stopgap solution
	a,b=Beta_lim(m,s,alpha,beta)
	return F_Beta_ab(x,alpha,beta,a,b)

def F_Gamma(x,m=None,s=None,k=None,l=None):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Gamma distribution
	# Input: x + m,s OR k,l (priority for m,s)
	# cfr. W&S p.5.8
	#--------------------------------------------------------------------------------------------------------

	if m is None and s is None: # l and k are given
		m,s=m_Gamma(l,k)
	a,scale=p_Gamma(m,s)
	return gamma.cdf(x,a,loc=0,scale=scale)

def F_InvGauss(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Inverse Gauss distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	mi,scale=p_InvGauss(m,s)
	return invgauss.cdf(x,mi,loc=0,scale=scale)

def F_Logistic(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Logistic distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	loc,scale=p_Logistic(m,s)
	return logistic.cdf(x,loc=loc,scale=scale)

def F_LogLogistic(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ LogLogistic distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	c,scale=p_LogLogistic(m,s)
	return fisk.cdf(x,c,loc=0,scale=scale)

def F_Rican(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Rican distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	b,scale=p_Rican(m,s)
	return rice.cdf(x,b,loc=0,scale=scale)

def F_Nakagami(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Nakagami distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	ni,scale=p_Nakagami(m,s)
	return nakagami.cdf(x,ni,loc=0,scale=scale)

def F_Birnbaum_Saunders(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Birnbaum_Saunders distribution
	# Input: Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	c,scale=p_Birnbaum_Saunders(m,s)
	return fatiguelife.cdf(x,c,loc=0,scale=scale)

def F_Lognormal_truncated(x,m,s,b):
	#--------------------------------------------------------------------------------------------------------
	# X ~ truncated lognormal distribution
	# Input: r,m,s,b (b = upper bound)
	#--------------------------------------------------------------------------------------------------------
	return F_Lognormal(x,m,s)/F_Lognormal(b,m,s)

## PDF function ##
##################
#------------------------------------------------------------------------------------------------------------
# fx for stochastic variable X, given realization x
#
# Input (in function of distribution):
# 	x = realization X
#	m = mean value X
#	s = standard deviation X
#
# Output:
#	fx(x)
#------------------------------------------------------------------------------------------------------------

def f_Normal(x,m,s,SW_log=False):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Normal distribution
	# Input: x,m,s
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	if SW_log: return norm.logpdf(x,m,s)
	else: return norm.pdf(x,m,s)

def f_Lognormal(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Lognormal distribution
	# Input: x,m,s
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	sln,mln=p_Lognormal(m,s)
	return lognorm.pdf(x,sln,0,np.exp(mln))

def f_MixedLN(x,sm,ss,sP):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Mixed-Lognormal distribution, with lognormal constituents Xi
	# Input: x,sm,ss,sP
	#--------------------------------------------------------------------------------------------------------
	out=np.zeros(x.shape)
	ssln,smln=p_Lognormal(sm,ss)
	for Xi in ssln.index:
		out+=f_Lognormal(x,sm[Xi],ss[Xi])*sP[Xi]
	return out

def f_Gumbel(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Gumbel distribution
	# Input: x,m,s
	#--------------------------------------------------------------------------------------------------------
	scale,loc=p_Gumbel(m,s)
	return gumbel_r.pdf(x,loc,scale)

def f_Gamma(x,m=None,s=None,k=None,l=None):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Gamma distribution
	# Input: x + m,s OR k,l (priority for m,s)
	# cfr. W&S p.5.8
	#--------------------------------------------------------------------------------------------------------
	if m is None and s is None: # l and k are given
		m,s=m_Gamma(l,k)
	a,scale=p_Gamma(m,s)
	return gamma.pdf(x,a,loc=0,scale=scale)

def f_Beta_01(x,alpha,beta,SW_log=False):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Beta distribution (0,1)
	# Input: x, alpha, beta
	#--------------------------------------------------------------------------------------------------------
	if SW_log: return Beta.logpdf(x,alpha,beta)
	else :return Beta.pdf(x,alpha,beta)

def f_Beta_ab(x,alpha,beta,m,s,SW_log=False):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Beta distribution (a,b)
	# Input: x, alpha, beta, m, s
	# cfr. W&S p.5.28
	#--------------------------------------------------------------------------------------------------------
	a,b=Beta_lim(m,s,alpha,beta)
	y=(x-a)/(b-a)
	return f_Beta_01(y,alpha,beta,SW_log)

def f_Weibull(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Weibull distribution
	# Input: x,m,s
	#--------------------------------------------------------------------------------------------------------
	c,scale=p_Weibull(m,s)
	return weibull_min.pdf(x,c,loc=0,scale=scale)

def f_InvGauss(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Inverse Gauss distribution
	# Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	mi,scale=p_InvGauss(m,s)
	return invgauss.pdf(x,mi,loc=0,scale=scale)

def f_Logistic(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Logistic distribution
	# Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	loc,scale=p_Logistic(m,s)
	return logistic.pdf(x,loc=loc,scale=scale)

def f_LogLogistic(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ LogLogistic distribution
	# Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	c,scale=p_LogLogistic(m,s)
	return fisk.pdf(x,c,loc=0,scale=scale)

def f_Rican(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Rican distribution
	# Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	b,scale=p_Rican(m,s)
	return rice.pdf(x,b,loc=0,scale=scale)

def f_Nakagami(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Nakagami distribution
	# Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	ni,scale=p_Nakagami(m,s)
	return nakagami.pdf(x,ni,loc=0,scale=scale)

def f_Birnbaum_Saunders(x,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Birnbaum_Saunders distribution
	# Input: x,m,s
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	c,scale=p_Birnbaum_Saunders(m,s)
	return fatiguelife.pdf(x,c,loc=0,scale=scale)

def f_Lognormal_truncated(x,m,s,b):
	#--------------------------------------------------------------------------------------------------------
	# X ~ truncated lognormal distribution
	# Input: r,m,s,b (b = upper bound)
	#--------------------------------------------------------------------------------------------------------
	if x>b: return 0
	return f_Lognormal(x,m,s)/F_Lognormal(b,m,s)


## parameter calculation ##
###########################
#------------------------------------------------------------------------------------------------------------
# distribution parameters for stochastic variable X, given mean and standard deviation
#
# Input (in function of distribution):
#	m = mean value X
#	s = standard deviation X
#
# Output:
#	distribution parameters
#------------------------------------------------------------------------------------------------------------

def p_Lognormal(m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Lognormal distribution
	# Input:m,s
	# Output:mln,sln cfr. W&S p.4.14
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	cov=s/m;
	sln=np.sqrt(np.log(1+cov**2))
	mln=np.log(m)-1/2*sln**2
	return sln,mln

def p_Gumbel(m,s,Version=1):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Lognormal distribution
	# Input:m,s
	# Intermediate calc: alpha,u cfr. W&S p.5.21
	# Output: scale, loc cfr. scipy
	# Version 1: update 30/01/2024 with more precise values
	#--------------------------------------------------------------------------------------------------------
	# parameters Gumbel W&S
	if Version==0: 
		alpha=1.282/s
		u=m-0.5772/alpha
	else: 
		alpha=np.pi/np.sqrt(6)/s
		u=m-0.5772156649/alpha
	# parameters Gumbel scipy
	scale=1/alpha
	loc=u
	return scale,loc

def p_Gamma(m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Gamma distribution
	# Input:m,s
	# Intermediate calc: k,lambda cfr. W&S p.5.8
	# Output: scale, loc cfr. scipy
	# rvc 01/2019
	#--------------------------------------------------------------------------------------------------------
	# parameters Gamma W&S
	l=m/s**2
	k=m*l
	# parameters Gamma scipy
	a=k
	scale=1/l
	return a,scale

def p_Weibull(m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Gamma distribution
	# Input:m,s
	# Intermediate calc: k,u cfr. W&S p.5.26
	# Output: c, scale cfr. scipy
	# rvc 05/2019
	#--------------------------------------------------------------------------------------------------------
	# parameters W&S (eps = loc = 0)
	# note : parameters weibull_min scipy: c=k; scale=u
	c,scale=p_Weibull_aux(m,s)
	return c,scale

def p_InvGauss(m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Inverse Gauss distribution
	# Input:m,s
	# Need to be checked
	# Output: mi, scale cfr. scipy
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	mi=s**2/m**2
	scale=m**3/s**2
	return mi,scale

def p_Logistic(m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Logistic distribution
	# Input:m,s
	# Need to be checked
	# Output: loc, scale cfr. scipy
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------
	loc=m
	scale=math.sqrt(3/math.pi)*s
	return loc,scale

def p_LogLogistic(m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ LogLogistic distribution
	# Input:m,s
	# Output: c, scale cfr. scipy
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------

	c,scale=p_LogLogistic_aux(m,s)
	return c,scale


def p_Rican(m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Rican distribution
	# Input:m,s
	# Output: b, scale cfr. scipy
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------

	b,scale=p_Rican_aux(m,s)
	return b,scale

def p_Nakagami(m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Nakagami distribution
	# Input:m,s
	# Output: ni, scale cfr. scipy
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------

	ni,scale=p_Nakagami_aux(m,s)
	return ni,scale

def p_Birnbaum_Saunders(m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Birnbaum_Saunders distribution
	# Input:m,s
	# Output: c, scale cfr. scipy
	# Balsa 12/2019
	#--------------------------------------------------------------------------------------------------------

	c,scale=p_Birnbaum_Saunders_aux(m,s)
	return c,scale

def Beta_alphabeta(m,s,a=None,b=None):
	""" Beta distribution shape parameters (alpha,beta) for given m,s and bounds (a,b)
	ref: W&S p. 5.29
	"""

	## scale to Beta01
	if a is not None and b is not None:
		mu=(m-a)/(b-a)
		sig=s/(b-a)
	else:
		mu=m; sig=s

	## calculate alpha and beta
	# ref: https://stats.stackexchange.com/questions/12232/calculating-the-parameters-of-a-beta-distribution-using-the-mean-and-variance
	alpha=((1-mu)/sig**2-1/mu)*mu**2
	beta=alpha*(1/mu-1)

	return alpha,beta





## limit calculation ##
#######################

def Beta_lim(m,s,alpha,beta):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Beta distribution (a,b)
	# Input: m,s,alpha,beta
	# cfr. W&S p.5.29
	#
	# note: only limited testing
	#--------------------------------------------------------------------------------------------------------
	c=np.sqrt(s**2*(alpha+beta)**2*(alpha+beta+1)/(alpha*beta)) # c = (b-a)
	a=m-alpha/(alpha+beta)*c
	b=c+a
	return a,b


## 'moment' calculation ##
##########################
#------------------------------------------------------------------------------------------------------------
# mean and standard deviation for stochastic variable X, given distribution parameters
#
# Input (in function of distribution)
#
# Output:
#	m = mean value X
#	s = standard deviation X
#------------------------------------------------------------------------------------------------------------

def m_Lognormal(mln,sln):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Lognormal distribution
	# Input: mln,sln cfr. W&S p.4.14
	# rvcpy - 2017
	#--------------------------------------------------------------------------------------------------------
	cov=np.sqrt(np.exp(sln**2)-1)
	m=np.exp(mln+1/2*sln**2)
	return m,m*cov

def m_alpha_Lognormal(alpha,m,s):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Lognormal distribution
	# Input: 
	#	alpha = exponent
	#	m,s = mean and standard deviation of lognormal variable X
	#--------------------------------------------------------------------------------------------------------
	def integrand(x,alpha,m,s):
		return x**alpha*f_Lognormal(x,m,s)
	return quad(integrand, 0., np.inf, args=(alpha,m,s))[0]

def m_alpha_MixedLN(Alpha,sm,ss,sP,SW_float=False):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Mixed-Lognormal distribution, with lognormal constituents Xi
	# Input: 
	#	alpha = exponent - float or pd.Series
	#	sm,ss,sP = pd.Series of constituent LN means, standard deviations, and probabilities
	#--------------------------------------------------------------------------------------------------------
	if isinstance(Alpha,float): Alpha=pd.Series(Alpha,index=['1']); SW_float=True
	Ma=deepcopy(Alpha)
	for key in Alpha.index:
		m_alpha_i=pd.Series(index=sP.index) # initialization
		for C in sP.index:
			m_alpha_i[C]=m_alpha_Lognormal(Alpha[key],sm[C],ss[C])
		Ma[key]=m_alpha_i.dot(sP)
	if SW_float: return Ma.values[0]
	else: return Ma

def m_Gamma(l,k):
	#--------------------------------------------------------------------------------------------------------
	# X ~ Gamma distribution
	# Input: lambda, k cfr. W&S p.5.8
	# rvc 2019
	#--------------------------------------------------------------------------------------------------------
	return k/l,np.sqrt(k/l**2)


##################
## AUX FUNCTION ##
##################

def Finv_MixedLN_cost(x,r,ssln,smln,sP):
	ri=sP.dot(lognorm.cdf(x,ssln,0,np.exp(smln))) # r-value for given x (Mixed-LN, cfr. f[F_MixedLN])
	return (r-ri)**2

def p_Weibull_aux(m,s):
	try:
		m[0]
	except:
		m=m.reshape((1,1))
		s=s.reshape((1,1))

	def myFunction(z,*data):
		# unpack parameters
		m,s=data
		ci=z[0]; scalei=z[1]
		# array of mean and variance deviations
		F=np.empty(2) # initialization
		F[0]=weibull_min.mean(ci,loc=0,scale=scalei)-m
		F[1]=weibull_min.std(ci,loc=0,scale=scalei)-s
		return F
	c=np.zeros((m.size,1))
	scale=np.zeros((m.size,1))
	for num in np.arange(m.size):
		# starting values
		c_0=10.
		scale_0=1.
		z_0=np.array([c_0,scale_0])
		m_0=m[num]
		s_0=s[num]
		# optimize 
		a=fsolve(myFunction,z_0,args=(m_0,s_0))
		c[num,:]=a[0]
		scale[num,:]=a[1]
	
	return c,scale

def p_LogLogistic_aux(m,s):

	try:
		m[0]
	except:
		m=m.reshape((1,1))
		s=s.reshape((1,1))

	def myFunction(z,*data):
		# unpack parameters
		m,s=data
		ci=z[0]; scalei=z[1]
		# array of mean and variance deviations
		F=np.empty(2) # initialization
		F[0]=fisk.mean(ci,loc=0,scale=scalei)-m
		F[1]=fisk.std(ci,loc=0,scale=scalei)-s
		return F
	c=np.zeros((m.size,1))
	scale=np.zeros((m.size,1))
	for num in np.arange(m.size):
		# starting values
		c_0=10.
		scale_0=1.
		z_0=np.array([c_0,scale_0])
		m_0=m[num]
		s_0=s[num]
		# optimize 
		a=fsolve(myFunction,z_0,args=(m_0,s_0))
		c[num,:]=a[0]
		scale[num,:]=a[1]
	return c,scale

def p_Rican_aux(m,s):
	
	try:
		m[0]
	except:
		m=m.reshape((1,1))
		s=s.reshape((1,1))
	
	def myFunction(z,*data):
		# unpack parameters
		m,s=data
		bi=z[0]; scalei=z[1]
		# array of mean and variance deviations
		F=np.empty(2) # initialization
		F[0]=rice.mean(bi,loc=0,scale=scalei)-m
		F[1]=rice.std(bi,loc=0,scale=scalei)-s
		return F
	b=np.zeros((m.size,1))
	scale=np.zeros((m.size,1))
	for num in np.arange(m.size):
		# starting values
		b_0=10.
		scale_0=1.
		z_0=np.array([b_0,scale_0])
		m_0=m[num]
		s_0=s[num]
		# optimize 
		a=fsolve(myFunction,z_0,args=(m_0,s_0))
		b[num,:]=a[0]
		scale[num,:]=a[1]
	return b,scale

def p_Nakagami_aux(m,s):
	
	try:
		m[0]
	except:
		m=m.reshape((1,1))
		s=s.reshape((1,1))
	
	def myFunction(z,*data):
		# unpack parameters
		m,s=data
		nii=z[0]; scalei=z[1]
		# array of mean and variance deviations
		F=np.empty(2) # initialization
		F[0]=nakagami.mean(nii,loc=0,scale=scalei)-m
		F[1]=nakagami.std(nii,loc=0,scale=scalei)-s
		return F
	ni=np.zeros((m.size,1))
	scale=np.zeros((m.size,1))
	for num in np.arange(m.size):	
		# starting values
		ni_0=10.
		scale_0=1.
		z_0=np.array([ni_0,scale_0])
		m_0=m[num]
		s_0=s[num]
		# optimize 
		a=fsolve(myFunction,z_0,args=(m_0,s_0))
		ni[num,:]=a[0]
		scale[num,:]=a[1]
	return ni,scale

def p_Birnbaum_Saunders_aux(m,s):
	
	try:
		m[0]
	except:
		m=m.reshape((1,1))
		s=s.reshape((1,1))
	
	def myFunction(z,*data):
		# unpack parameters
		m,s=data
		ci=z[0]; scalei=z[1]
		# array of mean and variance deviations
		F=np.empty(2) # initialization
		F[0]=fatiguelife.mean(ci,loc=0,scale=scalei)-m
		F[1]=fatiguelife.std(ci,loc=0,scale=scalei)-s
		return F
	c=np.zeros((m.size,1))
	scale=np.zeros((m.size,1))
	for num in np.arange(m.size):
		# starting values
		c_0=10.
		scale_0=1.
		z_0=np.array([c_0,scale_0])
		m_0=m[num]
		s_0=s[num]
		# optimize 
		a=fsolve(myFunction,z_0,args=(m_0,s_0))
		c[num,:]=a[0]
		scale[num,:]=a[1]
	return c,scale



#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":

	### setup f[F_MixedLN] ###
	##########################
	## input ##
	# x=5.
	# Sm=pd.Series([5.,10.],index=['x1','x2'])
	# Ss=pd.Series([1.,2.],index=['x1','x2'])
	# SP=pd.Series([0.7,0.3],index=['x1','x2'])

	# ## parameters of constituents ##
	# r=F_MixedLN(x,Sm,Ss,SP)
	# print('for x = {0:.3}, r = {1:.3}'.format(x,r))

	# ## f[Finv_MixedLN] ##
	# Finv_MixedLN(r,Sm,Ss,SP)
	# print('for r = {0:.3}, x = {1:.3}'.format(r,x))

	# ## probability density calculation ##
	# fx=f_MixedLN(x,Sm,Ss,SP)
	# print('fx = {0:.3} for x = {1:.3}'.format(fx,x))

	# ## fractional moment calculation ##
	# alpha=0.1
	# m_alpha=m_alpha_MixedLN(alpha,Sm,Ss,SP)
	# print(m_alpha)

	# ## test alpha as pd.Series ##
	# Alpha=pd.Series(np.array([0.,0.1,0.7]),index=['a0','a1','a2'])
	# m_alpha=m_alpha_MixedLN(Alpha,Sm,Ss,SP)
	# print(m_alpha)

	### multi parameter LN ###
	##########################
	# x=pd.Series([0.1,0.2,2],index=['x1','x2','x3'])
	# m=pd.Series([2,3,4],index=['XI','XII','XIII'])
	# s=pd.Series([1,1,1],index=['XI','XII','XIII'])

	# Fx=F_Lognormal(x,m,s)
	# print(Fx)

	# print(F_Lognormal(2,3,1))

	### setup Beta ###
	##################
	# m=1
	# s=0.1
	# alpha=4
	# beta=4
	# a,b=Beta_lim(m,s,alpha,beta)

	# print(a,b)

	### setup Gamma ###
	###################

	# print(1-F_Gamma(5,k=k,l=l))

	### setup Weibull ###
	#####################

	# m=30. # MPa
	# s=0.12*30.

	# c,scale=p_Weibull(m,s)

	# x=np.arange(0,90,1)

	# print(x)
	# fx=f_Weibull(x,m,s)

	# plt.plot(x,fx)
	# plt.show()

	# print (c,scale)


	### setup Beta_alphabeta ###
	############################
	m=0.5
	s=1/6
	a=None
	b=None
	print(Beta_alphabeta(m,s,a,b))

	HGV_HRRmin=15; HGV_HRRmax=200 # [MW]
	HGV_HRRmean=60; HGV_HRRstd=30
	print(Beta_alphabeta(HGV_HRRmean,HGV_HRRstd,HGV_HRRmin,HGV_HRRmax))
	# HGVHRR_sV=stochVar.createStochVar(name='HGV_HRR',dist='uniform',dim='[MW]',theta1=HGV_HRRmin,theta2=HGV_HRRmax)

