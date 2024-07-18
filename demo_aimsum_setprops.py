from PyANGBasic import *
from PyANGKernel import *
from PyANGConsole import *

# this script shows how to find an experiment,
# and set various poperties of it
# it can be used inside an Aimsun script

def getScenarioByName(name):
	scenarios = GK.GetObjectsOfType(model.getType("GKGenericScenario"))
	
	for s in scenarios:
		if s.getName() == name:
			return s

	return None

def getScenarioExperimentByName(scenario, name):
	exps = scenario.getExperiments()
	
	for e in exps:
		if e.getName() == name:
			return e
	
	return None

def getExperimentReplicationByName(exp, name):
    reps = exp.getReplications()
    
    for r in reps:
        if r.getName() == name:
            return r
    
    return None

def getObjProperty(obj, propertyName):
	propID = getattr(obj, propertyName)
	
	return obj.getDataValueByID(propID)

def setObjProperty(obj, propertyName, value):
	propID = getattr(obj, propertyName)

	obj.setDataValueByID(propID, value)




scenario = getScenarioByName("Network - 100% Checks")
exp = getScenarioExperimentByName(scenario, "Meso DUE gradient")
rep = getExperimentReplicationByName(exp, "100% Checks")

print(rep.getName())

print(getObjProperty(exp, "reactionTimeAtt"))
setObjProperty(exp, "reactionTimeAtt", 1.1)
setObjProperty(exp, "reactionAtTrafficLightMesoAtt", 1.3)
