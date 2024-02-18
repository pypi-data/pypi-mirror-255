""" Control SAFIR calculations

Notes
-----
The control module support SAFIR calculations
"""

#############
## IMPORTS ##
#############

import os
import subprocess
import shutil
import json
import time

from magnelPy.admin import TimeStamp


#####################
## REFERENCE PATHS ##
#####################

pathfile_path ="C:\\Users\\rvcoile\\Documents\\paths_SAFIRshell.json"

with open(pathfile_path) as json_file:
    paths = json.load(json_file)

## system path SAFIR executable ##
SAFIRpath=paths["SAFIRpath"]
Temp_Dir=paths["Temp_Dir"]



############
## MODULE ##
############

def runSAFIR():
	## *.in file with extension ##
	infile=SAFIRin_userInput()

	## testing ##
	print(infile)
	
	## execution ##
	SAFIR_run(infile)

def SAFIR_run(file,path=SAFIRpath,SW_removeItem=True,Temp_Dir=Temp_Dir):
	# run SAFIR *.in file
	#	copy *.tem file to Python directory in case of structural analysis

	curDir=os.getcwd()
	refDir='\\'.join(file.split('\\')[0:-1]) # path to folder of *.in file

	## check type of SAFIR calcuation
	SAFIRtype=SAFIR_type(file)

	# create working directory
	worker,workDir=WorkDirCreate(Temp_Dir,file)
	os.chdir(workDir)

	## Run calculation ##
	## if Thermal2D ==> run calculation
	if SAFIRtype=='Thermal2D':
		pass
	else: ## STRUCTURAL UNDER DEVELOPMENT ##
		## move *.tem file to SAFIRpy working directory
		temfilepath,temname=SAFIR_TEMinIN(file) # determine *.tem file (full path - *.in directory assumed)
		temtargetpath=workDir+'\\'+temname
		shutil.copy(temfilepath,temtargetpath) # copy *.tem file to SAFIRpy working directory
		
	# run SAFIR and move results to original directory
	SAFIR_exe(path,worker) # run SAFIR
	os.chdir(curDir)
	WorkDirClean(workDir,refDir)



#########
## AUX ##
#########

def WorkDirClean(WorkDir,refDir):
	files=os.listdir(WorkDir)
	for file in files:
		infile=WorkDir+'\\'+file
		try: shutil.move(infile,refDir)
		except : pass
	shutil.rmtree(WorkDir)
	# shutil.copytree(WorkDir,refDir)
	# shutil.move(WorkDir,refDir)


def WorkDirCreate(Temp_Dir,file):
	## create working dir and copy files to perform calculation ##
	sub=TimeStamp()
	workDir=Temp_Dir+"\\"+sub
	os.mkdir(workDir)

	name=file.split('\\')[-1]
	worker=workDir+"\\"+name
	shutil.copy(file,worker)

	return worker,workDir

def SAFIR_TEMinIN(file):
	# returns name *.TEM file referenced in *.IN file

	with open(file) as f:
		line=f.readline()
		while len(line)>0:
			line=f.readline() # read line
			if '.tem' in line:
				line=line.rstrip() # remove newline character
				infolderpath='\\'.join(file.split('\\')[0:-1]) # path to folder of *.in file
				temfilepath=infolderpath+'\\'+line
				return temfilepath,line # returns full path and name only of *.tem file

def SAFIR_exe(path,file):

	## remove *.in extension
	file=file[0:-3] 

	## run through subprocess
	subprocess.call([path,file])

def SAFIR_type(file):
	# returns type of *.in file: Thermal2D, Structural2D, Structural3D

	with open(file,encoding="utf-8") as f:
		line=f.readline() # first line
		line=f.readline().rstrip() # second line and remove newline indication

	if line == 'Safir_Thermal_Analysis': return 'Thermal2D'
	if line == 'Safir_Static_2D_Analysis': return 'Structural2D'
	if line == 'Safir_Static_3D_Analysis': return 'Structural3D'

def SAFIRin_userInput():

	## filename
	filename=input("\nPlease provide path to input file (*.in): ")
	if filename[0]=="\"": filename=filename[1:-1] # strips quotes from path

	return filename

#########################
## STAND ALONE - DEBUG ##
#########################

if __name__ == "__main__": 

	runSAFIR()
