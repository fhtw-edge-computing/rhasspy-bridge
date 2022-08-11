from flask import Flask
from flask import request
from flask import jsonify, render_template
from flask_socketio import SocketIO, emit, send
import requests

import json
import importlib

speechService = importlib.import_module("speechService")
actionHandler = importlib.import_module("actionHandler")
configFile = "config.json"
config = None

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
socketio = SocketIO(app)

@app.route('/action', methods = ['POST'])
def handleAction():
    json = request.get_json()
    socketio.emit('message', json)
    response = actionHandler.doAction(json, config)
    
    socketio.emit('response', response)
    text = response.get("text") or ""
    text = text.lower().replace('ü', 'ue').replace('ä', 'ae').replace('ö', 'oe').replace('ß', 'ss')
    data = {
        "speech": {
            "text": text
        }
    }

    speechService.speak(text)
    return jsonify({}) # use this in order to get Rhasspy taling: jsonify(data)
    
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('home.html')
    return "Set your Rhasspy remote HTTP intent handler to http://0.0.0.0:1234/action"
    
@socketio.on('startListeinng')
def handle_message():
    print("waking up rhasspy...")
    requests.post("http://localhost:12101/api/listen-for-command")
    
@socketio.on('stopSpeaking')
def handle_message():
    speechService.stopSpeaking()
    #print("saying rhasspy to stop speaking...")
    #requests.post("http://localhost:12101//api/play-recording")

if __name__ == '__main__':
    with open(configFile, encoding="utf-8") as f:
        config = json.load(f);
    socketio.run(app, host='0.0.0.0', port=1234)
    #app.run(host='0.0.0.0', port=1234)
