#__author__ = "magnelPy"

####################
## MODULE IMPORTS ##
####################

import numpy as np
import pandas as pd
from copy import deepcopy

from scipy import optimize
import itertools

####################
## SURROGATE EVAL ##
####################

def y_regression(X,theta):

	htheta=np.dot(X,theta)

	return htheta

###################
## COST FUNCTION ##
###################

#---------------------------------CostFunction -----------------------------
def cost_func(X_tr,Y_tr,theta,SW_grad=False):
	""" Base cost function regression

	Parameters
	----------
	X_tr :	(m,n+1) numpy.ndarray
		n input features for m samples, including unit bias term in first column
	Y_tr :	(m,) numpy.ndarray
		target output for m samples
	theta :	(n+1,) numpy.ndarray
		regression coefficients for the bias term + n features
	SW_grad : Boolean
		return gradient of J wrt theta yes/no

	Returns
	-------
	jtheta1:	scalar
		Base cost regression
	Gjtheta1:	(n+1,) numpy.ndarray
		Gradient of cost with theta
	Reference
	---------
	No external reference

	Prior implementation
	---------
	Ranjit Chaudhary : IPW2020 code : Regression.py

	Examples
	--------
	>>> from magnelPy.ML import regression as reg
	>>> X=np.array([[1,2],[1,5]]) # data points x = 2 and x = 5
	>>> Y=np.array([2,4])
	>>> theta=np.array([1,1])
 	>>> J=reg.cost_func(X,Y,theta)
 	>>> print(J)
 	1.25
	"""
	m=np.shape(X_tr)[0];
	htheta=y_regression(X_tr,theta)
	Y_tr=Y_tr.squeeze()
	Z=np.subtract(htheta,Y_tr)
	# test=pd.DataFrame([htheta,Y_tr,Z],index=['htheta','Y_tr','Z']);print(test.T)
	jtheta1=np.sum(np.square(Z))/(2*m)

	if not SW_grad: return jtheta1
	else:
		Gjtheta1=np.matmul(Z,X_tr)/m
		return jtheta1,Gjtheta1

#--------------------------with Regularization parameter---------------
def cost_funcreg(X_tr,Y_tr,theta,lamda=0,SW_grad=False):
	""" Regularized cost function regression - ridge regression

	Parameters
	----------
	X_tr :	(m,n+1) numpy.ndarray
		n input features for m samples, including unit bias term in first column
	Y_tr :	(m,) numpy.ndarray
		target output for m samples
	theta :	(n+1,) numpy.ndarray
		regression coefficients for the bias term + n features
	lamda : scalar
		regularization coefficient
	SW_grad : Boolean
		return gradient of J wrt theta yes/no

	Returns
	-------
	jtheta:	scalar
		Regularized cost regression
	Gjtheta:	(n+1,) numpy.ndarray
		Gradient of cost with theta

	Reference
	---------
	No external reference

	Prior implementation
	---------
	Ranjit Chaudhary : IPW2020 code : Regression.py

	Examples
	--------
	>>> from magnelPy.ML import regression as reg
	>>> X=np.array([[1,2],[1,5]]) # data points x = 2 and x = 5
	>>> Y=np.array([2,4])
	>>> theta=np.array([1,1])
	>>> lamda = 0.2
 	>>> Jreg=reg.cost_funcreg(X,Y,theta,lambda)
 	>>> print(Jreg)
 	1.30
	"""
	m=np.shape(X_tr)[0]

	if not SW_grad: jtheta1 = cost_func(X_tr,Y_tr,theta)
	else: jtheta1,Gjtheta1 = cost_func(X_tr,Y_tr,theta,True)

	reg_term=(lamda/(2*m))*np.sum(np.square(theta[1:]))
	jtheta=jtheta1+reg_term

	if not SW_grad: return jtheta
	else:
		Greg=lamda*theta/m; Greg[0]=0
		Gjtheta=Gjtheta1+Greg
		return jtheta, Gjtheta

###########################
## OPTIMIZATION FUNCTION ##
###########################

#----------------------------Gradient Descent Algorithm-----------------------
def Gradient_descentalg(X_tr,Y_tr,lamda,theta,alpha,cost_tol=10**(-5),maxiter=10**4,SW_fullOutput=False,SW_debug=False):
	""" Train regularized regression - Gradient descent algorithm

	Parameters
	----------
	X_tr :	(m,n+1) numpy.ndarray
		n input features for m samples, including unit bias term in first column
	Y_tr :	(m,) numpy.ndarray
		target output for m samples
	lamda : scalar
		regularization coefficient
	theta :	(n+1,) numpy.ndarray
		regression coefficients for the bias term + n features
	alpha : scalar
		step-size update gradient descent algorithm
	cost_tol : scalar
		convergence criterium : cost tolerance in regularized cost calculation  
	maxiter : integer
		convergence criterium : maximum number of iterations
	SW_fullOutput : Boolean
		switch for calculation step logging and return

	Returns
	-------
	theta:	(n+1,) numpy.ndarray
		regression coefficients for the bias term + n features

	if SW_fullOutput :
	fullOutput :	Dict
		Dict with logged calculations

	Reference
	---------
	No external reference

	Prior implementation
	---------
	Ranjit Chaudhary : IPW2020 code : Regression.py

	Examples
	--------
	>>> from magnelPy.ML import regression as reg
	>>> X=np.array([[1,2],[1,5]]) # data points x = 2 and x = 5
	>>> Y=np.array([2,4])
	>>> theta=np.array([1,1])
	>>> lamda = 0.
	>>> alpha=0.05
 	>>> theta,fullOutput=reg.Gradient_descentalg(X,Y,lamda,theta,alpha,cost_tol=10**-7,maxiter=10,SW_fullOutput=True)
 	>>> print(fullOutput['thetalist'])
				   0         1
		0   1.000000  1.000000
		1   0.925000  0.700000
		2   0.906250  0.630625
		3   0.900578  0.614828
		4   0.897954  0.611477
		5   0.896048  0.611014
		6   0.894318  0.611220
		7   0.892639  0.611580
		8   0.890980  0.611973
		9   0.889336  0.612371
		10  0.887704  0.612768
	# note: analytical result : theta_0=theta_1=2./3
	"""
	# squeeze for dimension issue
	Y_tr=Y_tr.squeeze()

	# initial cost and approximation
	cost = cost_funcreg(X_tr,Y_tr,theta,lamda)
	htheta=y_regression(X_tr,theta) # current regression approximation
	# calc parameters
	m,n=np.shape(X_tr); 
	lamda_v=lamda*np.ones(n); lamda_v[0]=0.
	# gradient descent iteration setup
	iterate=True; niter=0
	if SW_fullOutput: 
		fullOutput={} # Dict of calc info
		Jlist=[cost]; thetalist=pd.DataFrame(theta,columns=[0]); Yapproxlist=pd.DataFrame(htheta,columns=[0])
	# gradient descent iteration
	while iterate:
		niter+=1
		## matrix implementation
		if not SW_debug:
			A=alpha/m*np.matmul(np.transpose(X_tr),y_regression(X_tr,theta)-Y_tr) # update matrix, excl. regression
			B=1-alpha*lamda_v/m
			theta=np.multiply(theta,B)-A
		if SW_debug:
		## original step-wise - maintained for demonstration purposes : set SW_debug == True
			for i in np.arange(len(theta)):
				redn= alpha/m*np.sum(np.multiply(htheta-Y_tr,X_tr[:,i]))
				if i==0:
					theta[i]=theta[i]-redn
				else:
					theta[i]=theta[i]*(1-alpha*lamda/m)-redn
		new_cost = cost_funcreg(X_tr,Y_tr,theta,lamda)
		htheta=y_regression(X_tr,theta) # current regression approximation
		if SW_fullOutput: Jlist.append(new_cost); thetalist[niter]=theta; Yapproxlist[niter]=htheta
		if abs(new_cost-cost)<=cost_tol: iterate=False
		if niter==maxiter: iterate=False
		cost = new_cost
	if SW_fullOutput:
		fullOutput['Jlist']=Jlist; fullOutput['thetalist']=thetalist.T; fullOutput['Yapproxlist']=Yapproxlist.T
		return theta,fullOutput
	else: return theta

def train_regularizedRegression(X_tr,Y_tr,lamda,theta0,SW_optimObject=False):
	"""  Train regularized regression - apply fmin_cg

	WIP - TO BE COMPLETED

	SW_optimObject : Boolean
		switch for return of optimObject; if False only optim values are returned

	"""

	## package arguments
	args=(X_tr,Y_tr,lamda)

	## optimization options
		# maxiter 	: int 		- Maximum number of iterations to perform. Default is 200 * len(x0)
		# disp		: Boolean	- If True, return a convergence message, followed by xopt
		# gtol		: float		- Stop when the norm of the gradient is less than gtol
	opts={'maxiter' : None,
         'disp' : False,
         'gtol' : 1e-5}

	## optimize	
	res=optimize.minimize(packed_cost_funcreg, theta0, jac=True, args=args, method='CG',options=opts)

	if not SW_optimObject: return res.x
	else: return res

##################
## FEATURE PREP ##
##################

def poly_model(Xmain,k,interaction=True):
	""" Polynomial expansion of feature set + bias addition

	Parameters
	----------
	Xmain :	(m,n) pd.DataFrame
		n input features for m samples
	k	:	scalar
		degree of feature polynomial
	interaction : Boolean
		include interation terms yes/no

	Returns
	-------
	X	:	(m,N +1) numpy.ndarray
		data for kth order polynomial regression; N ifo interaction yes/no

	Reference
	---------
	No external reference

	Prior implementation
	---------
	Ranjit Chaudhary : IPW2020 code : Regression.py

	Future development
	------------------
	List 'XX' as 'X2' etc for higher order features

	Examples
	--------
	WIP
	>>> from magnelPy.ML import regression as reg
	>>> X=np.array([[1,2],[1,5]]) # data points x = 2 and x = 5
	>>> Y=np.array([2,4])
	>>> theta=np.array([1,1])
	"""

	## setup
	X=deepcopy(Xmain)
	columns=list(X.columns); n=len(X.columns); m=len(X.index) # number of features

	## feature mapping
	comb_list = num_pol_terms(k,n,interaction)
	out=pd.DataFrame()

	for tup in comb_list:
		if len(tup)==1:
			header=columns[tup[0]-1]
			out[header]=X[header]
		else:
			val=np.ones(m); header=[]
			for j in tup:
				feature=columns[j-1]
				val*=X[feature]
				header+=feature
			out["".join(header)]=val

	return out

def addBias(data):

	## add bias
	columns=list(data.columns)
	columns=['bias']+columns
	data['bias']=1

	return data[columns]

#----------------------------Data (feature) scaling-----------------------
def DataScale(data,scale_param=None):
	""" Data feature / output scaling

	Parameters
	----------
	data :	np.ndarray or pd.DataFrame
		m realizations in rows; n different features in columns (or single feature)

	Returns
	-------
	x	:	np.ndarray
		m x n array of scaled features
	WIP

	Reference
	---------
	No external reference

	Examples
	--------
	WIP
	>>> from magnelPy.ML import regression as reg
	>>> X=np.array([[1,2],[1,5]]) # data points x = 2 and x = 5

	"""

	if not isinstance(scale_param,pd.DataFrame):
		## scaling from scratch
		# transform pd objects to np.ndarray for consistency standard deviation calc
		if isinstance(data,pd.DataFrame):
			SW_df=True; index=data.index; column=data.columns
			data=data.values
		else: SW_df=False
		# scale
		x,m,std=scale(data)
		# output - differentiation for output naming columns (overkill)
		if SW_df:
			x=pd.DataFrame(x,index=index,columns=column)
			scale_param=pd.DataFrame(np.array([m,std]),index=['mean','std'],columns=column)
		else:
			x=pd.DataFrame(x); scale_param=pd.DataFrame(np.array([m,std]),index=['mean','std'])
		return x,scale_param
	else:
		## scaling with pre-specified scaling parameters
		x=(data-scale_param.loc['mean'])/scale_param.loc['std']
		return x



##################
## AUX FUNCTION ##
##################

def scale(x,SW_sample_std=True):
	""" scales data as ksi = (x-x.mean())/x.std()

	Parameters
	----------
	x :	np.ndarray
		m observations (rows) x n features (columns)
	SW_sample_std : Boolean
		True for sample standard deviation : conform Matlab Coursera

	Note
	----------
	x.std() is defined differently for np.ndarray and pd.Series (division sqrt.(m) vs. sqrt(m-1))
	"""
	m=x.shape[0]
	mean=x.mean(axis=0)
	std=x.std(axis=0)
	if SW_sample_std: std=std*np.sqrt(m)/np.sqrt(m-1)
	return (x-mean)/std,mean,std

def packed_cost_funcreg(theta,*args):

	## unpacking args
	(X_tr,Y_tr,lamda)=args

	## call regularized cost function
	jtheta, Gjtheta=cost_funcreg(X_tr,Y_tr,theta,lamda,SW_grad=True)

	return jtheta,Gjtheta

def num_pol_terms(PolDegree,nVar,interaction=True):
	""" Combination list for polynomial feature mapping

	Parameters
	----------
	PolDegree 	:	int
		degree of polynomial
	nVar		:	int
		number of features
	interaction	:	Boolean
		feature interaction yes/no

	Returns
	-------
	Combination :	list of tuples
		list of tuples with feature combinations (featurs 1 to n)

	Reference
	---------
	No external reference

	Prior implementation
	---------
	Ranjit Chaudhary : IPW2020 code : Regression.py (full copy)

	Examples
	--------
	>>> from magnelPy.ML import regression as reg
	>>> k=2; n=3; SW_interaction=False
	>>> comb=reg.num_pol_terms(k,n,SW_interaction); print(comb)
	[(1,), (1, 1), (2,), (2, 2), (3,), (3, 3)]
	>>> SW_interaction=True
	>>> comb=reg.num_pol_terms(k,n,SW_interaction); print(comb)
	[(1,), (1, 1), (1, 2), (1, 3), (2,), (2, 2), (2, 3), (3,), (3, 3)]

	"""
	var = np.arange(nVar)+1
	for num in np.arange(PolDegree):
		if num==0:
			combination = list(itertools.combinations_with_replacement(var,num+1))
		else:
			comb= list(itertools.combinations_with_replacement(var,num+1))
			combination=combination+comb
	combination.sort(); ncombo=[]
	if not interaction:
		for tup in combination:
			if len(tup)>=1 and all(np.in1d(tup, tup[0])):
				ncombo.append(tup)
		combination = ncombo
	return combination

#################
## FUNCTION RC ##
#################

#---------Performs polynomial expansions and writes in csv file to make easy read during optimization
def Data_Scaling(LearningPath,Ypath,PolDegree,interaction=True):
	wbx=load_workbook(LearningPath); sheets = wbx.sheetnames
	data1=pd.ExcelFile(LearningPath); data2=pd.ExcelFile(Ypath)
	Xmain=data1.parse("X_tr"); Ymain=data2.parse("X_tr")
	if not 'X_cv'in sheets:
		ntotal=np.shape(Xmain.values)[0]
		num_tr=int(0.8*ntotal); num_cv=int(0.15*ntotal); num_test=int(0.05*ntotal)
		X=poly_model(Xmain.values,PolDegree,interaction);Y=Ymain.values[:,1]
		X_tr=X[:num_tr,:];X_cv=X[num_tr:num_tr+num_cv,:]
		X_test=X[num_tr+num_cv:num_tr+num_cv+num_test,:]
		Y_tr=Y[:num_tr];Y_cv=Y[num_tr:num_tr+num_cv]
		Y_test=Y[num_tr+num_cv:num_tr+num_cv+num_test]
	else:
		cvx=data1.parse("X_cv"); cvy=data2.parse("X_cv")
		X_tr=poly_model(Xmain.values,PolDegree,interaction); Y_tr=Ymain.values[:,1]
		splitnum=np.shape(cvx.values)[0]
		X_cv=poly_model(cvx.values,PolDegree,interaction); Y_cv=cvy.values[:,1]
		X_test=X_cv[:int(splitnum*0.5),:];Y_test=Y_cv[:int(splitnum*0.5)]
		X_cv=X_cv[int(splitnum*0.5):,:];Y_cv=Y_cv[int(splitnum*0.5):]

	meanX_tr = np.mean(X_tr,axis = 0);stdX_tr = np.std(X_tr,axis = 0)
	# Scaling the input variables using sklearn library in python
	scaler = StandardScaler()
	X_tr[:,1:] =scaler.fit_transform(X_tr[:,1:]); X_cv[:,1:] =scaler.transform(X_cv[:,1:])
	meanY_tr = np.mean(Y_tr);stdY_tr = np.std(Y_tr)
	Y_tr=(Y_tr-meanY_tr)/stdY_tr;Y_cv=(Y_cv-meanY_tr)/stdY_tr;
	meanX_tr=np.append(meanX_tr,meanY_tr);stdX_tr=np.append(stdX_tr,stdY_tr)
	return X_tr,X_cv,X_test,Y_tr,Y_cv,Y_test,meanX_tr,stdX_tr


# Fits the X-data into the polynomial expression for all the training sets
def poly_model_RC(Xmain,PolDegree,interaction=True):
	comb_list = num_pol_terms(PolDegree,np.shape(Xmain)[1]-1,interaction)
	X=np.zeros((np.shape(Xmain)[0],len(comb_list)+1), dtype=float)
	X[:,0]=np.ones(np.shape(Xmain)[0])
	for ncombo in np.arange(len(comb_list)):
		if len(comb_list[ncombo])==1:
			X[:,ncombo+1]=Xmain[:,int(comb_list[ncombo][0])]
		else:
			for nlocal in np.arange(len(comb_list[ncombo])):
				if nlocal==0:
					X[:,ncombo+1]=Xmain[:,int(comb_list[ncombo][nlocal])]
				else:
					X[:,ncombo+1]=X[:,ncombo+1]*Xmain[:,int(comb_list[ncombo][nlocal])]
	return X

#########################
## STAND ALONE - DEBUG ##
#########################

## Test Function ##
###################

def Test(sentence='Default sentence'):
	""" Print sentence to screen - Test module activation

	Parameters
	----------
	sentence :	str
		input sentence

	Returns
	-------
	None

	Returns
	-------
	None

	Reference
	---------
	None

	Examples
	--------
	>>> import magnelPy.ML as ML
	>>> ML.regression.Test()
	Default sentence
 	>>> ML.regression.Test("Another test")
 	Another test
	"""
	print(sentence)

if __name__ == "__main__":

	Test()
	Test('Another test')
	help(Test)