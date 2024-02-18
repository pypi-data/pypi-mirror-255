# -*- coding: utf-8 -*-
"""
Radiation calcs for FSE / SFE 
"""
import numpy as np


############
## MODULE ##
############

def F_RectangleToCorner(h,w,d):
    """ Viewfactor from exposing rectangle (h x w) to point at distance d from corner

	Parameters
	----------	
	h : float or (m x n) np.array
		height of the radiating rectangle [distance]

	w : float or (m x n) np.array
		width of the radiating rectangle [distance]

	d : float or (m x n) np.array
		distance to the radiating rectangle [distance]

	Returns
	-------
	F : float or np.array
		 viewfactor [-]
	
	Example use
	-----------
    print("Drysdale 2nd ed, p.59")
    alpha=0.6;S=0.8;F=0.106 # data Drysdale
    h=5 # arbitrary choice
    w=S*h; d=np.sqrt(h*w/alpha)
    print("Calculated : ",F_RectangleToCorner(h, w, d))
    print("Listed by Drysdale : ",F)
    >>>Drysdale 2nd ed, p.59
    >>>Calculated :  0.10633951895326263
    >>>Listed by Drysdale :  0.106
	
	Reference
	-----------    
	Formula PGFSE THMT_Theory12b slide 32
	Code as applied in 'External Fire Spread' project
	"""
    
    X=h/d
    Y=w/d
        
    F=1/(2*np.pi)*(X/np.sqrt(1+X**2)*np.arctan(Y/np.sqrt(1+X**2))+Y/np.sqrt(1+Y**2)*np.arctan(X/np.sqrt(1+Y**2)))

    return F

def F_RectangleToCenter(H,W,d):
    """ Viewfactor from exposing rectangle (H x W) to point at distance d from corner

	Parameters
	----------	
	H : float or np.array
		height of the radiating rectangle [distance]

	W : float or np.array
		width of the radiating rectangle [distance]

	d : float or np.array
		distance to the radiating rectangle [distance]

	Returns
	-------
	F : float or np.array
		 viewfactor [-]
	
	Example use
	-----------
    see F_RectangleToCorner
	
	Reference
	-----------    
	Basic THMT; Drysdale 2nd ed., p.58
	"""
    
    return 4*F_RectangleToCorner(H/2.,W/2.,d)

#################
## MODULE-TEST ##
#################

def moduleTest():
    print("\nmagnelPy.SFE Radiation functionality active\n")

#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__":
    
    ## case 1
    print("Drysdale 2nd ed, p.59")
    alpha=0.6;S=0.8;F=0.106 # data Drysdale
    h=5 # arbitrary choice
    w=S*h; d=np.sqrt(h*w/alpha)
    print("h = {0}, w = {1}, d = {2}".format(h,w,d))
    print("Calculated : ",F_RectangleToCorner(h, w, d))
    print("Listed by Drysdale : ",F)
    
    ## case 2
    print()
    H=10
    W=S*H
    print("H = {0}, W = {1}, d = {2}".format(H,W,d))
    print("Calculated : ",F_RectangleToCenter(H, W, d))
