import requests
from lxml import html
import urllib.parse

def getActionTypes():
	return ["EXTRACT_WEBSITE"]


def doAction(actionType, config, totalConfig):
	slots = config.get("slots") or {}
	params = config.get("params") or {}
	
	url = params.get("url") or ""
	url = url.format(**slots)
	xpath = params.get("xpath")
	fallback = params.get("fallback") or None
	
	print(f'Extracting from {url} with xpath expression "{xpath}"')
	
	text, error = getActionText(url, xpath, fallback)
	return {"text": text, "error": error, "steps": [f'Extracting from <a href="{url}">{url}</a> with xpath expression "{xpath}"']}
	
def getActionText(url, xpath, fallback=None):
	if (not url):
		return None
	text = extractFromWebsite(url, xpath)
	error = False if text else True
	fallback = fallback if fallback else "Ich konnte die Website nicht abrufen"
	text = text if text else fallback
	return text, error
		
def extractFromWebsite(url, xpath):
	xpath = xpath or "//body//text()"
	try:
		content = requests.get(url).content
		tree = html.fromstring(content)
		return " ".join(tree.xpath(xpath)).replace("'", "").replace('"', '')
	except:
		return ""
