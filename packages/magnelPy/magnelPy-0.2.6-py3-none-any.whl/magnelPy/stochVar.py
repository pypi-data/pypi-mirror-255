#__author__ = "magnelPy"
# test 1

#--------------------------------------------------------------------------------------------------------
# Standard formatting stochastic variables
#--------------------------------------------------------------------------------------------------------

####################
## MODULE IMPORTS ##
####################

import numpy as np
import scipy as sp
from magnelPy import statFunc as sf

##############
## FUNCTION ##
##############

def createStochVar(name='',dist='normal',mean=0.,std=1.,dim='[-]',comment='',theta1=None,theta2=None):
	## standard formatting of stochastic variables ##
	# name = name of stochastic variable
	# dist = distribution type
	# 'normal';'lognormal';'mixedlognormal';'gumbel';'deterministic';'beta';'gamma';'uniform';'weibull';'lognormal_truncated'
	# mean = mean value
	# std = standard deviation
	# dim = dimension
	# comment = free notes
	# theta1 = first additional parameter - when appropriate - can be improved
	# theta2 = second additional parameter - when appropriate - can be improved
	return {'name':name,'dist':dist,'dim':dim,'m':mean,'s':std,'info':comment,'theta1':theta1,'theta2':theta2}

def fx(varDict,xArray,SW_log=False):
	DistType=varDict['dist']
	if DistType=='normal':
		return sf.f_Normal(xArray,varDict['m'],varDict['s'],SW_log)
	if DistType=='lognormal':
		return sf.f_Lognormal(xArray,varDict['m'],varDict['s'])
	if DistType=='mixedlognormal':
		return sf.f_MixedLN(xArray,varDict['mi'],varDict['si'],varDict['Pi'])
	if DistType=='gumbel':
		return sf.f_Gumbel(xArray,varDict['m'],varDict['s'])
	if DistType=='beta':
		return sf.f_Beta_ab(xArray,varDict['theta1'],varDict['theta2'],varDict['m'],varDict['s'],SW_log)
	if DistType=='gamma':
		return sf.f_Gamma(xArray,varDict['m'],varDict['s'])
	if DistType=='uniform':
		return sf.f_Uniform(xArray,varDict['theta1'],varDict['theta2'])
	if DistType=='weibull':
		return sf.f_Weibull(xArray,varDict['m'],varDict['s'])
	if DistType=='lognormal_truncated':
		return sf.f_Lognormal_truncated(xArray,varDict['m'],varDict['s'],varDict['theta1'])

def Fx(varDict,xArray):
	DistType=varDict['dist']
	if DistType=='normal':
		return sf.F_Normal(xArray,varDict['m'],varDict['s'])
	if DistType=='lognormal':
		return sf.F_Lognormal(xArray,varDict['m'],varDict['s'])
	if DistType=='mixedlognormal':
		return sf.F_MixedLN(xArray,varDict['mi'],varDict['si'],varDict['Pi'])
	if DistType=='gumbel':
		return sf.F_Gumbel(xArray,varDict['m'],varDict['s'])
	if DistType=='beta':
		return sf.F_Beta_ms(xArray,varDict['m'],varDict['s'],varDict['theta1'],varDict['theta2'])
	if DistType=='gamma':
		return sf.F_Gamma(xArray,varDict['m'],varDict['s'])
	if DistType=='uniform':
		return sf.F_Uniform(xArray,varDict['theta1'],varDict['theta2'])
	if DistType=='weibull':
		return sf.F_Weibull(xArray,varDict['m'],varDict['s'])
	if DistType=='lognormal_truncated':
		return sf.F_Lognormal_truncated(xArray,varDict['m'],varDict['s'],varDict['theta1'])

def Finvx(varDict,rArray):
	DistType=varDict['dist']
	if DistType=='normal':
		return sf.Finv_Normal(rArray,varDict['m'],varDict['s'])
	if DistType=='lognormal':
		return sf.Finv_Lognormal(rArray,varDict['m'],varDict['s'])
	if DistType=='mixedlognormal':
		return sf.Finv_MixedLN(rArray,varDict['mi'],varDict['si'],varDict['Pi'])
	if DistType=='gumbel':
		return sf.Finv_Gumbel(rArray,varDict['m'],varDict['s'])
	if DistType=='beta':
		return sf.Finv_Beta_ms(rArray,varDict['m'],varDict['s'],varDict['theta1'],varDict['theta2'])
	if DistType=='gamma':
		return sf.Finv_Gamma(rArray,varDict['m'],varDict['s'])
	if DistType=='uniform':
		return sf.Finv_Uniform(rArray,varDict['theta1'],varDict['theta2'])
	if DistType=='weibull':
		return sf.Finv_Weibull(rArray,varDict['m'],varDict['s'])
	if DistType=='lognormal_truncated':
		return sf.Finv_Lognormal_truncated(rArray,varDict['m'],varDict['s'],varDict['theta1'])

## RF transformation ##
#######################

def RF_fxN_FxN(x,muN,sigN):
    uN=(x-muN)/sigN
    FxN=sf.F_Normal(uN,0,1)
    fxN=1/sigN*sf.f_Normal(uN,0,1)
    return FxN,fxN

def RF_deviation(parN,x,varDict):
    muN=parN[0];sigN=parN[1]
    fxx=fx(varDict,x); Fxx=Fx(varDict,x)
    FxN,fxN=RF_fxN_FxN(x,muN,sigN)
    return Fxx-FxN,fxx-fxN

def RF_muN_sigN_solver(x,varDict):
    out=sp.optimize.fsolve(RF_deviation,[varDict['m'],varDict['s']],args=(x,varDict))
    muN=out[0];sigN=out[1]
    return muN,sigN

def RF_transform(x,varDict):
    muN,sigN=RF_muN_sigN_solver(x,varDict)
    return (x-muN)/sigN,muN,sigN

    
##################
## AUX FUNCTION ##
##################


#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":

	rebar = 0.01  #rebar diameter [m]
	dist = 0.1  #distance between rebars [m]
	w = 1.    #slab width [m]	

	As=createStochVar(dist='normal',mean=0.25*(np.pi)*rebar**2*(w/dist)*1.02,std=0.02*0.25*(np.pi)*rebar**2*(w/dist)*1.02,dim='[m2]',name='As [m2]')
	fck=30; Vfc=0.15 # [MPa]; [-]
	fc=createStochVar(dist='lognormal',mean=fck/(1-2*Vfc),std=fck/(1-2*Vfc)*Vfc,dim='[MPa]',name='fc20 [MPa]')

	StochVarDict={'As':As,'fc':fc}

	nameList=[StochVarDict[key]['name'] for key in StochVarDict.keys()]

	print(StochVarDict.keys())    
