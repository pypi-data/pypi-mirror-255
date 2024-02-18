"""
magnelPy.Abaqus
============
Provides
  1. Input Data for concrete material models in a Abaqus Heat Transfer Analysis
  2. Input Data for concrete and steel material models in a Abaqus Heat Thermal Stress Analysis

"""
### get submodules ###
from magnelPy.SFE import ThermalTools, MechanicalTools
from magnelPy.Abaqus import ThermalProperties, MechanicalProperties
from magnelPy.Abaqus import AbaqusPropertiesMaster