#app.py
from flask import Flask, json, request, jsonify, redirect, url_for
import os
import urllib.request
from werkzeug.utils import secure_filename
import requests
import json
 
import cv2
from ML.opencv import compare_image

from mqtt_server import MQTTServer

from utils import read_csv
from constants import *
from utils import *
 
app = Flask(__name__, static_folder='../static')
 
mqtt_server = MQTTServer()
mqtt_server.start()
 
UPLOAD_FOLDER = os.path.join('static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
def allowed_filetype(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/')
def main():
    return 'Homepage'
 
@app.route('/esp32toggle')
def esp32_test():
    mqtt_server.trigger()
    return 'ESP32 Was Triggered!'

@app.route('/gestures', methods = ['POST'])
def gesture_toggle():
    data = request.get_json()
    gesture = data.get("gesture")
    
    mqtt_server.trigger(gesture)
    # POC showing that telegram messaging works
    send_telegram_message(f'Gesture Received: {gesture}')
    
    print(f'Gesture Received: {gesture}')
    
    resp = jsonify({
        'message': 'message received, esp32 is notified',
        'gesture_received': gesture
    })
    
    
    resp.status_code = 200
    return resp

@app.route('/data', methods = ['GET'])
def get_esp32_data():
    esp32_data = read_csv('esp32_dynamic.csv', 50)
    data = {}
    for i in range(len(JSON_KEYS)):
        data[JSON_KEYS[i]] = esp32_data[i]
    resp = jsonify(data)
    resp.status_code = 200
    return resp

@app.route('/<path:path>')
def fallback(path):
    return "Wrong Endpoint!"
 
@app.route('/cam_output')
def some_func():
    return 'some output'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)