from flask import Flask
from flask import request
from flask import jsonify, render_template
from flask_socketio import SocketIO, emit, send
import requests
from pynput import keyboard
import os
import time

import json
import importlib

speechService = importlib.import_module("speechService")
actionHandler = importlib.import_module("actionHandler")
configFile = "config.json"
config = None

shutdown = False
counter = 0

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
def handle_start_listening():
    print("waking up rhasspy...")
    requests.post("http://localhost:12101/api/listen-for-command")
    
@socketio.on('stopSpeaking')
def handle_stop_speaking():
    speechService.stopSpeaking()
    #print("saying rhasspy to stop speaking...")
    #requests.post("http://localhost:12101//api/play-recording")

def on_key_press(key):
    global counter, shutdown

    if key == keyboard.Key.right:
        counter += 1
        if counter > 40 and not shutdown:
            shutdown = True
            speechService.stopSpeaking()
            speechService.speak("auf wiedersehen")
            time.sleep(2)
            os.system('poweroff')

def on_key_release(key):
    global counter
    # print('{0} released'.format(key))
    if key == keyboard.Key.right and not shutdown:
        counter = 0
        speechService.stopSpeaking()
        requests.post("http://localhost:12101/api/listen-for-command")
        

if __name__ == '__main__':
    with open(configFile, encoding="utf-8") as f:
        config = json.load(f);
    listener = keyboard.Listener(on_release=on_key_release, on_press=on_key_press)
    listener.start()
    print("HELLO")
    socketio.run(app, host='0.0.0.0', port=1234)
    #app.run(host='0.0.0.0', port=1234)
