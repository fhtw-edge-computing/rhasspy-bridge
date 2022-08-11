import os
import importlib

speechService = importlib.import_module("speechService")

actionHandlerMap = {}

def init():
	moduleName = 'actions'
	obj = os.scandir(moduleName)
	for entry in obj:
		name = entry.name
		if entry.is_file() and name.endswith('.py') and (not name.startswith('_')):
			handler = importlib.import_module(f'{moduleName}.{name.replace(".py", "")}')
			actionType = None
			if handler and callable(getattr(handler, 'getActionTypes', None)) and callable(getattr(handler, 'doAction', None)):
				actionTypes = handler.getActionTypes()
			if len(actionTypes) > 0:
				for actionType in actionTypes:
					actionHandlerMap[actionType] = handler
			else:
				print(f'WARN: coudn\'t import file "{name}" as action handler!')
			
init()

def doAction(json, config):
	result = {
		"text": "Keine Aktion gefunden",
		"error": True
	}
	#print(json)
	print("//////////////////////////////////////////////////////////////")
	print("--------------------- got Rhasspy action ---------------------")
	
	intentName = json["intent"]["name"] 
	print(f'Intent: {intentName}')
	if intentName == "STOP":
		speechService.stopSpeaking()
		return {"steps": ["Ausgabe gestoppt"]}
	intentMappings = config.get("intentMappings") or {}
	intentMapping = next(filter(lambda x: x.get("intentName") == intentName, intentMappings), None)
	requestSlots = json.get("slots") or {}
	print(f'Slots: {requestSlots}')
	print("-------------------")
	actionType = None
	if intentMapping:
		actionType = intentMapping.get("actionType")
		matchSlotList = intentMapping.get("matchSlotList")
		mappedParamsList = intentMapping.get("mappedParamsList")
		intentMapping["slots"] = requestSlots
		if len(requestSlots.keys()) == 0:
			intentMapping["params"] = []
		else:
			for i, matchSlots in enumerate(matchSlotList):
				containsAll = True
				for key in matchSlots.keys():
					if matchSlots.get(key) != requestSlots.get(key):
						containsAll = False
				if containsAll:
					intentMapping["params"] = mappedParamsList[i]
		
	actionType = actionType or intentName
	if actionHandlerMap.get(actionType):
		handler = actionHandlerMap.get(actionType)
		if callable(getattr(handler, 'doAction', None)):
			result = handler.doAction(actionType, intentMapping, config)
	
	if isinstance(result, str):
		result = {"text": result}	
	print(f'Got result: "{result.get("text")}"')
	print("//////////////////////////////////////////////////////////////")
	return result
	
