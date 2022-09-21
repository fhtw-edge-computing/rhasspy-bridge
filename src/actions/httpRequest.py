import requests

def getActionTypes():
	return ["HTTP_REQUEST"]

def doAction(actionType, config, totalConfig):
	globalGlobalParams = totalConfig.get("globalParams") or {}
	steps = []
	intentName = config.get("intentName")
	actionType = config.get("actionType")
	slots = config.get("slots") or {}
	params = config.get("params") or {}
	globalParams = config.get("globalParams") or {}
	httpMethod = params.get("httpMethod") or globalParams.get("httpMethod") or "GET"
	textTemplate = params.get("textTemplate") or globalParams.get("textTemplate") or ""
	textReplace = params.get("textReplace") or globalParams.get("textReplace") or {}
	resultParam = params.get("resultParam") or globalParams.get("resultParam") or ""
	sendParam = params.get("sendParam") or globalParams.get("sendParam") or ""
	sendValue = slots.get(sendParam)
	
	error = False
	try:
		url = params.get("url") or ""
		url = url.format(**globalGlobalParams)
		steps.append(f'HTTP {httpMethod} "{sendValue}" to "{url}"')
		print(steps[-1])
		response = requests.request(httpMethod, url, data=str(sendValue), timeout=1.5)
	except requests.exceptions.RequestException as e:
		print(e)
		error = True
	json = {}
	try:
		json = response.json()
	except:
		pass
	preText = "Fehler" if error else "OK"
	result = json.get(resultParam)
	params["result"] = result
	textParams = params | slots
	text = textTemplate.format(**textParams)
	for key in textReplace.keys():
		text = text.replace(key, textReplace.get(key))
	return {"text": f'{preText} {text}', "error": error, "steps": steps}
