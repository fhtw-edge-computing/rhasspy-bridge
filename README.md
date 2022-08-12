# Rhasspy Bridge
This project is a small, customizable and lightweight bridge for connecting [Rhasspy](https://rhasspy.readthedocs.io/en/latest/) and its recognized intents from speech-to-text (STT) commands to any other either own project or existing platform like [openHAB](https://www.openhab.org/).

We're using this Rhasspy Bridge with the following configuration, but it's probably possible to also run it on a different one:
* Raspberry Pi 4, Model B, 4GB RAM
* Current Raspberry Pi OS, 32bit
* [Jabra Speak 510](https://www.jabra.com.de/supportpages/jabra-speak-510#/#7510-209)

## Getting started
To use `Rhasspy Bridge` a running instance of Rhasspy is needed. We followed [these steps for installing Rhasspy in their docs](https://rhasspy.readthedocs.io/en/latest/installation/#debian). We didn't use `Docker`, but the native install on `Debian`. For our Raspberry Pi 4 with 32bit OS the `armhf` package is the correct one. See [Hints](README.md#hints) if you're running into problems while installing Rhasspy.

You can start with an own Rhasspy configuration, however if you want to see Rhasspy Bridge in action you can use the (German) backup file in this repo in the folder [/rhasspy/rhasspy-backup-profile.zip](https://github.com/fhtw-edge-computing/rhasspy-bridge/tree/main/rhasspy). It works out of the box along with the [config.json](https://github.com/fhtw-edge-computing/rhasspy-bridge/blob/main/src/config.json) of the bridge.

After running Rhasspy, also start the `server.py` from this repo in a differnt terminal:
* `cd src`
* `python3 server.py`

These web based user interfaces are available after running both Rhasspy and Rhasspy Bridge:
* Rhasspy UI: [http://localhost:12101](http://localhost:12101)
* Rhasspy Bridge Visualization: [http://localhost:1234](http://localhost:1234)

**Important:** In oder to connect Rhasspy and Rhasspy Bridge do the following:
* Open Rhasspy UI
* Go to `Settings -> Intent Handling` and select `Remote Server` there. Also see [Rhasspy docs for setting remote server intent handling](https://rhasspy.readthedocs.io/en/latest/intent-handling/#remote-server)
* Set `http://localhost:1234/action` as URL where Rhasspy should send the intents to

### Text-to-Speech
Currently it's not possible to stop TTS messages done by Rhasspy (see [issue on github](https://github.com/rhasspy/rhasspy/issues/117)). Therefore Rhasspy Bridge currently uses the external `Pico TTS` for text-to-speech instead of Rhasspy. In order to use it, it's required to install `Pico TTS` with `sudo apt-get install libttspico-utils`. If you want to use TTS from Rhasspy instead, see this [line in server.py](https://github.com/fhtw-edge-computing/rhasspy-bridge/blob/main/src/server.py#L35).

## Concept of Rhasspy Bridge
Rhasspy Bridge is basically just a set of Python scripts that start a server to receive the intent descriptions sent by Rhasspy as JSON. These are then mapped to an arbitrary and fully customizable action.

These are the most important files/folders in this repo in the `src` directory:
* `server.py`: entry point and sets up the server for receiving the intents from Rhasspy
* `config.json`: contains the JSON config for mappings that require additional parameters
* folder `actions`: contains scripts that are used to actually perform actions

### Action scripts
The folder `actions` contains scripts that handle actual actions. Two methods are mandatory:
* `getActionTypes()`: returns an array of action names (strings) this script can handle.
* `doAction(actionType, config, totalConfig)`: is called, if the action should be performed. Available parameters are:
   * **actionType**: name of the current action (string) 
   * **config**: corresponding mapped config (dictionary) for this action, containing keys `slots` and `params` containing the Rhasspy slots and the mapped parameters for these slots for the current action.
   * **totalConfig**: complete configuration dictionary parsed from `config.json`

The name of the files in folder `actions` doesn't matter as long as they are Python scripts `*.py`.

#### Return value
The method `doAction()` can return two possible values:
* `string`: the text value to speak with TTS
* `dictionary`: with keys `text:<text to speak>`, `error: <True/False>` and `steps:['log1'. 'log2', ...]`. All values are optional and are used (next to TTS) in order to create the visualization of Rhasspy Bridge at `http://localhost:1234`.

### Basic actions without parameters
Some actions doesn't need any additional parameters, e.g. telling the current time. For these it's possible to directly trigger actions from Rhasspy without additional mapping.

Example in Rhasspy `sentences.ini`:
```
[CURRENT_TIME]
\[uhr] zeit
wie spaet [ist es]
```

This script in `actions` handles the action without additional mapping:
```
def getActionTypes():
	return ["CURRENT_TIME", "CURRENT_DATE"]

def doAction(actionType, config, totalConfig):
    if actionType == "CURRENT_TIME":
        # retrieve current time and return text to speak
    elif actionType == "CURRENT_DATE":
	    # retrieve current date and return text to speak
```

### Advanced actions with additional parameters
Some actions need additional parameters which are not embedded in the intent description received by Rhasspy. This is where the mapping in `config.json` is used.

Example in Rhasspy `sentences.ini`:
```
[ChangeLightState]
light_state = (ein:ON | aus:OFF) {value}
light_name = (esstisch | kochtisch | wohnzimmertisch){name}
licht <light_name> <light_state>
```

This will create the intent `ChangeLightState` with slots `name` for the name of the light and `value=ON/OFF`.

In order to map these actions to an action in openHAB triggered over the openHAB REST API this is the corresponding configuration of `config.json`:
```
{
    "intentName": "ChangeLightState",
    "actionType": "HTTP_REQUEST",
    "matchSlotList": [
        {"name": "esstisch"},
        {"name": "kochtisch"},
        {"name": "wohnzimmertisch"}
    ],
    "mappedParamsList": [
        {"url": "http:/<ip-open-hab>:<port>/rest/items/Kueche1_KNX_Licht_Schalten"},
        {"url": "http:/<ip-open-hab>:<port>/rest/items/Kueche2_KNX_Licht_Schalten"},
        {"url": "http:/<ip-open-hab>:<port>/rest/items/WZ_KNX_Licht_Schalten"
        }
    ],
    "globalParams": {
        "httpMethod": "POST",
        "sendParam": "value",
        "textTemplate": "Licht {name} {value}",
        "textReplace": {
            "ON": "ein",
            "OFF": "aus"
        }
    }
}
```

The value `intentName` is the Rhasspy intent name which is mapped to the action handler of type `actionType` to handle this action. The array `matchSlotList` contains different combinations of slots/values (in this case single slot name/value) that as mapped to the corresponding parameters in `mappedParamsList`. So if the Rhasspy intent contains the slot `{"name": "kochtisch"}` the mapped params will contain `{"url": "http:/<ip-open-hab>:<port>/rest/items/Kueche2_KNX_Licht_Schalten"}`. Global parameters are used to define general properties for the corresponding actions. The param `config` in `doAction(actionType, config, totalConfig)` of the action handler will then include this mapping and additionally `slots` (current slots of the intent) and `params` (mapped parameters) in order to supply the information needed for performing the action.

In this example these are the properties for the action of type `HTTP_REQUEST` implemented in [actions/httpRequest.py](https://github.com/fhtw-edge-computing/rhasspy-bridge/blob/main/src/actions/httpRequest.py):
* **url**: URL where to send the HTTP request is sent to
* **httpMethod**: which HTTP method to use (e.g. `GET, POST, PUT, ...`)
* **sendParam**: which of the values from "slots" is used to send as payload to the request (in this case the slot with name `value`)
* **textTemplate**: text template that is used to create the response text. Values in curly braces are replaced with the values from `slots` or `params`
* **textReplace**: values that should be replaced in the response text, e.g. replace `ON` with the German word `ein`

## Adapting the configuration
The current configuration has implemented action handlers for the following types:
* `CURRENT_TIME`, `CURRENT_DATE`: action to receive the current time or date
* `HTTP_REQUEST`: action for doing arbitrary HTTP requests, currently used for openHAB REST API
* `EXTRACT_WEBSITE`: action for extracting text from a website using an `xpath` expression. Currently used for retrieving weather forecast or random jokes.

In order to extend these possibilities just:
* adapt existing actions handlers to your needs
* add needed parameters to the mapping in `config.json`
* write new action handlers containing the methods `getActionTypes()` and `doAction(actionType, config, totalConfig)`

If you have questions or additional ideas, feel free to open an [issue on github](https://github.com/fhtw-edge-computing/rhasspy-bridge/issues).

## Hints
This section contains some hints for getting everything working and solutions for problems we faced with our hardware configuration.

### Rhasspy: libffi.so.6 not found
After installing Rhasspy, there was an error stating `libffi.so.6 not found` in the console. The fix was to run `sudo apt-get install libffi6`, also see [this issue on libffi.so.6 not found on github](https://github.com/rhasspy/rhasspy/issues/290).

### Rhasspy: training failed for German configuration
The initial German Rhasspy config and also the generated number string contain special characters like `ä, ö, ü, ß`. Rhasspy seems to currently be unable to handle these and throws a `Training Failed` exception. The solution was to replace all special characters in `sentences.ini` of Rhasspy and apply a fix in the code that converts numbers to words, also see this [issue on training failed exception on github](https://github.com/rhasspy/rhasspy/issues/294).

### Rhasspy: audio recording not working
We didn't get audio recording working with the recommended `PyAudio` option in Rhasspy. Switching to `arecord` at first still has shown some exceptions but nevertheless worked in the end. See this [issue on audio recording on github](https://github.com/rhasspy/rhasspy/issues/293).

### Rhasspy: use other wake words for Porcupine
We're using the wakeword engine from [Picovoice/Porcupine](https://picovoice.ai/platform/porcupine/) because it performs best. In order to get wake words different from "Porcupine" working, it's necessary to follow the [instruction in the Rhasspy docs](https://rhasspy.readthedocs.io/en/latest/wake-word/#porcupine) and to not use the latest models from Picovoice on github, but [older ones on the tag `1.9`](https://github.com/Picovoice/porcupine/tree/v1.9/resources/keyword_files). This is because for the newer ones offline capabilities without AccessKey from Picovoice have been disabled, also see [this issue in the Picovoice github repo](https://github.com/Picovoice/porcupine/issues/617).

### Rhasspy: avoid too complex config
At first we tried to create a very complex sentence configuration in Rhasspy like this (in German):
```
[ChangeLightState]
alle = (alle lichter | alle leuchten):alle
esstisch = (([licht beim] esstisch) | (esstisch [licht])):esstisch
kochtisch = (([licht beim] (kochtisch | kochfeld)) | ((kochtisch | kochfeld) [licht])):kochtisch
wohnzimmer = (([licht beim] wohnzimmertisch) | (wohnzimmertisch [licht]) | (haengelampe [im] wohnzimmer) | (haengelampe [beim] wohnzimmertisch) | haengelampe):wohnzimmertisch
wand = ((wandlicht [schlafzimmer]) | ([schlafzimmer] wandlicht)):wand
bad = ((licht [im] bad) | badlicht):bad
gang = ((licht am gang) | ganglicht):gang
light_state = (ein:ON | aus:OFF) {value}
light_name = (alle | esstisch | kochtisch | wohnzimmer | wand | bad | gang){name}
\[schalte] [das | die] <light_name> <light_state>
\[das] [licht] [(am | im | in (der | dem))] <light_name> <light_state>[schalten]
```

It seems to be great, because you theoretically can say everything very naturally and it should cover many variations of the same intent and sentences like these should all be correctly recognized:
* `wandlicht schlafzimmer aus`
* `schalte das wandlicht im schlafzimmer aus`
* `wandlicht im schlafzimmer ausschalten`
* `schlafzimmer wandlicht aus`

However it turned out that for our tests this leads to very poor recognition rates and many things are understood wrongly. Therefore we switched to much easier sentences with less flexibility but much better recognition instead:
```
[ChangeLightState]
light_state = (ein:ON | aus:OFF) {value}
light_name = (esstisch | kochtisch | wohnzimmertisch | wand | bad | gang){name}
licht <light_name> <light_state>
((alle lichter):alle){name} <light_state>
```