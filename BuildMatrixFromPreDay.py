import pandas as pd
import sys
from importlib import reload

# Add Aimsum path to module resolution
sys.path.append('C:/Program Files/Aimsun/Aimsun Next 23/plugins/python')

from PyANGBasic import *
from PyANGKernel import *
from PyANGConsole import *

import os
import SortByMode
reload(SortByMode)

# ==============
# Configuration
# ==============
MODES = ['Car']

PROJECT_PATH = 'C:\\Users\\mehou\\Documents\\Aimsum\\BaseCase1122'
das_fn = os.path.join(PROJECT_PATH, 'November_Base_Case_Aggregate')
id_fn = os.path.join(PROJECT_PATH, 'Id.csv')

START_TIMES_RANGE = list(range(6, 24))
# only do first 10 for now
START_TIMES_RANGE = START_TIMES_RANGE[0:4]

# ==============


def readDAS():
	#das.columns = ['person_id', 'tour_no', 'tour_type', 'stop_no', 'stop_type', 'stop_location', 'stop_zone','stop_mode', 'primary_stop', 'arrival_time', 'departure_time', 'prev_stop_location', 'prev_stop_zone', 'prev_stop_departure_time', 'drivetrain', 'make', 'model']
	return pd.read_csv(das_fn,header='infer')

def readCentIDs():
	return pd.read_csv(id_fn,header='infer')

def getStartTimes():
	# all start time possible
	res = []
	for i in START_TIMES_RANGE:
		res.append(QTime(i,0,0,0))
		res.append(QTime(i,30,0,0))
	
	return res

def getMatrixNames(mode):
	res = []
	for i in START_TIMES_RANGE:
		res.append(f'matrix_{i+0.25:0>5.2f}_{mode}')
		res.append(f'matrix_{i+0.75:0>5.2f}_{mode}')

	return res

def getSimmobilityTimes():
	res = []
	for i in START_TIMES_RANGE:
		res.append(i+0.25)
		res.append(i+0.75)
	
	return res

def getActiveCentroid(model):
	c=model.getType("GKCentroidConfiguration")
	d=GK.GetObjectsOfType(c) #### d is list of all CentroidConfiguration
	for cent in d:
		if(cent.isActive()==True) :    ## Onlly 1  CentroidConfiguration  is True and active
			return cent
	return None

def getVehicleByName(model, name):
	vvt_list=GK.GetObjectsOfType(model.getType("GKVehicle"))  ##  the vechule type list
	for vvt in vvt_list :
		if  (vvt.getName()==name): ### if the vecyle type is the mode (in this code : car)
			return vvt
	return None

def updateExistingMatrix(model,mat,OD_data_list,matrix_start_time,mode):
	mat.setTripsFromList(OD_data_list) ### update matrix by the list
	mat.setDataValue(model.getColumn( "GKTrafficDemandItem::durationAtt"),QTime(0,30,0,0)) ## ubdate interval time of metrix to 30 min
	mat.setDataValue(model.getColumn( "GKTrafficDemandItem::fromAtt"),matrix_start_time) ## to ubdate the time we need get the Coulome of start time ,thiis colum + out time is the atrgument to set time in (GK object)ODMATRIX
	mat.setVehicle(getVehicleByName(model, mode))  ### update the vehicle type in the matrix


def createNewMatrix(model,active_centroid):
	cmd = model.createNewCmd( model.getType( "GKODMatrix" )) ##Builed object type ODMATRIX
	cmd.setCentroidConfiguration(active_centroid)  ## Set is Centroied Configure be thats one is active
	model.getCommander().addCommand(cmd) ## comment the model
	mat = cmd.createdObject() ##crate.
	
	return mat

def getMatrixByName(active_centroid, name):
	for mat in active_centroid.getODMatrices():
		if(mat.getName()==name):
			return mat
	return None


def build(model):
	### Choose the mode
	das = readDAS()
	centroid_ids = readCentIDs()

	matrix_start_times = getStartTimes()
	simmobility_times = getSimmobilityTimes()

	for mode in MODES:
		### all name posible
		matrix_names = getMatrixNames(mode)

		### for all time from start to end
		for t in range(len(matrix_start_times))  :
			OD_data=SortByMode.sort(das,mode,t,centroid_ids, simmobility_times) ## Builed trips matrix in external founctuin by mode and time
			OD_data_list=OD_data.values.tolist() ### make list from this dataframe

			active_centroid = getActiveCentroid(model)
			matrix_name = matrix_names[t]
			matrix_start_time = matrix_start_times[t]

			mat = getMatrixByName(active_centroid, matrix_name)

			if mat is None:
				# failed to find matrix, create new one
				print(f'Creating new matrix {matrix_name}')
				mat = createNewMatrix(model,active_centroid)
				mat.setName(matrix_name)
			else:
				print(f'Updating existing matrix {matrix_name}')
			
			updateExistingMatrix(model,mat,OD_data_list,matrix_start_time,mode)
			