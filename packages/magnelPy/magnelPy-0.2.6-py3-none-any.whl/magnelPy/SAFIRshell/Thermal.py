"""Thermal input file generation

Notes
-----
The Thermal module allows thermal input file generation for SAFIR.
"""

#############
## IMPORTS ##
#############

######################
## MODULE FUNCTIONS ##
######################

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
	>>> import magnelPy.SAFIRshell as SAFIRshell
	>>> SAFIRshell.Thermal.Test()
	Default sentence
 	>>> SAFIRshell.Thermal.Test("Another test")
 	Another test
	"""
	print(sentence)

## Local testing ##
###################

if __name__ == "__main__":

	Test()
	Test('Another test')
	help(Test)
