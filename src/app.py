#app.py
from flask import Flask, json, request, jsonify, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
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
from ML.model import RegModel
 
app = Flask(__name__, static_folder='../static')

# ML Model Initialization
model = RegModel()

# MQTT Server Initialization
mqtt_server = MQTTServer()
mqtt_server.start()
 
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=lambda: requests.get('http://127.0.0.1:5000/anomaly'), trigger='interval', minutes=1)
scheduler.start()
 
UPLOAD_FOLDER = os.path.join('static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
def allowed_filetype(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/')
def main():
    return "LifeESP32tancy+++ GO GO GO"
 
@app.route('/esp32toggle')
def esp32_test():
    mqtt_server.trigger()
    return 'ESP32 Was Triggered!'

@app.route('/anomaly', methods = ['GET'])
def anomaly_check():
    df = model.read_data()
    print(df)
    results = model.get_error(df)
    print(results)    
    results = anomaly_threshold_check(results)
    print(results)
    features_anomaly = format_anomaly_threshold(results)
    
    results = format_anomaly_message(features_anomaly)

    if results:
        send_telegram_message(results)
        send_telegram_message(results, TELEGRAM_ELLIA)
    
    resp = jsonify({
        'message': 'Anomaly Detection Successful'
    })
    resp.status_code = 200
    
    return resp

@app.route('/gestures', methods = ['POST'])
def gesture_toggle():
    data = request.get_json()
    gesture = data.get("gesture")
    print(gesture)
    
    if gesture == 'Palm':
        mqtt_server.trigger('1')
        
    elif gesture == 'Fist':
        mqtt_server.trigger('0')
        
    elif gesture == 'Cheese':
        send_telegram_message('Ignore previous message!')    
        send_telegram_message('Ignore previous message!', TELEGRAM_HANNAH)

    elif gesture == 'Thumbs Up':
        send_telegram_message('Assistance required!')
        send_telegram_message('Assistance required!', TELEGRAM_HANNAH)
        
    else:
        send_telegram_message('Something went wrong', TELEGRAM_GORDON)
    
    # POC showing that telegram messaging works
    # send_telegram_message(f'Gesture Received: {gesture}')
    
    print(f'Gesture Received: {gesture}')
    
    resp = jsonify({
        'message': 'message received, esp32 is notified',
        'gesture_received': gesture
    })
    
    
    resp.status_code = 200
    return resp

@app.route('/data', methods = ['GET'])
def get_esp32_data():
    esp32_data = read_csv(60)
    data = {}
    for i in range(len(GLOBAL_JSON_KEYS)):
        data[GLOBAL_JSON_KEYS[i]] = esp32_data[i]
    resp = jsonify(data)
    resp.status_code = 200
    return resp

@app.route('/dashboard', methods = ['GET'])
def get_dashboard_data():
    esp32_data = read_csv(1)
    data = {}
    for i in range(len(GLOBAL_JSON_KEYS)):
        data[GLOBAL_JSON_KEYS[i]] = esp32_data[i]
    resp = jsonify(data)
    resp.status_code = 200
    return resp

@app.route('/<path:path>')
def fallback(path):
    return "Wrong Endpoint!"
 
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
