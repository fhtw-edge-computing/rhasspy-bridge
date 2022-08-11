import time
from datetime import datetime
import locale

def getActionTypes():
	return ["CURRENT_TIME", "CURRENT_DATE"]

def doAction(actionType, config, totalConfig):
	locale.setlocale(locale.LC_ALL, '') # to use current system locale
	if actionType == "CURRENT_TIME":
		unixTime = getUnixTime()
		if not unixTime:
			return {"text": "Ich kann die Uhrzeit nicht abrufen", "error": True}
		else:
			return f'Es ist {getTimeReadable(unixTime)} Uhr'
				
	elif actionType == "CURRENT_DATE":
		unixTime = getUnixTime()
		if not unixTime:
			return {"text": "Ich kann das Datum nicht abrufen", "error": True}
		else:
			return f'Heute ist {getDateReadable(unixTime)}'

def getUnixTime():
	return time.time()
					
def getUnixTimeOnline():
	unixTime = None
	try:
		return int(requests.get("https://time.asterics-foundation.org/").content)
	except:
		return None

def getTimeReadable(unixTime):
	return datetime.fromtimestamp(unixTime).strftime("%H:%M")
	
def getDateReadable(unixTime):
	return datetime.fromtimestamp(unixTime).strftime("%A, %d. %B %Y")
