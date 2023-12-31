import paho.mqtt.client as mqtt
import os
import csv
import json

from utils import write_to_csv, send_telegram_message, process_json_payload

from constants import *

class MQTTServer:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code: {str(rc)}")
        print(f"Subscribed to topic: {ESP32_SUBSCRIBE_TOPIC}")
        print(f"Subscribed to topic: {PRESSURE_ESP32_SUBSCRIBE_TOPIC}")
        send_telegram_message('ESP32 is up and running!')
        client.subscribe(ESP32_SUBSCRIBE_TOPIC)
        client.subscribe(PRESSURE_ESP32_SUBSCRIBE_TOPIC)

    def on_message(self, client, userdata, message):
        payload_str = message.payload.decode('utf-8')
        payload_json = json.loads(payload_str)
        
        topic = message.topic

        data = process_json_payload(payload_json, GLOBAL_JSON_KEYS)
        
        resources = {
            "main": (DYNAMIC_CSV_FILENAME, MASTER_CSV_FILENAME, JSON_KEYS),
            "pressure": (PRESSURE_DYNAMIC_CSV_FILENAME, PRESSURE_MASTER_CSV_FILENAME, PRESSURE_JSON_KEYS)
        }
        
        if topic == ESP32_SUBSCRIBE_TOPIC:
            print(data)
            write_to_csv(csv_dynamic=DYNAMIC_CSV_FILENAME, csv_main=MASTER_CSV_FILENAME, headers=JSON_KEYS, data=data)
        elif topic == PRESSURE_ESP32_SUBSCRIBE_TOPIC:
             
            write_to_csv(csv_dynamic=PRESSURE_DYNAMIC_CSV_FILENAME, csv_main=PRESSURE_MASTER_CSV_FILENAME, headers=PRESSURE_JSON_KEYS, data=data)
        
        # send_telegram_message(data)
        
        # client.publish(ESP32_PUBLISH_TOPIC, "1")
        
    def trigger(self, message='1'):
        # send_telegram_message(message)
        self.client.publish(ESP32_PUBLISH_TOPIC, message)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

if __name__ == "__main__":
    mqtt_server = MQTTServer()
    mqtt_server.start()
