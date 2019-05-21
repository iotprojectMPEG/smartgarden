#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author = Paolo Grasso
"""

import paho.mqtt.client as PahoMQTT
import time
import datetime
import json
import requests

SEC = 10

loop_flag = 1
class MyPublisher(object):
    def __init__(self, clientID, serverIP):
        self.clientID = clientID
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect  # Association

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_publish(self, topic, message):
        self._paho_mqtt.publish(topic, message, 2)

    def my_on_connect(self, client, userdata, flags, rc):
        global loop_flag
        print ("Connected to %s - Result code: %d" % (self.messageBroker, rc))
        loop_flag = 0


def publisher(devID, resource, value):
    with open("conf.json") as f:
        config = json.loads(f.read())

    # Get broker IP from the catalog
    connected = 0
    while connected == 0:
        try:
            string = ("http://"+config["catalogURL"]+ ":" +
                       config["port"] + "/broker")
            print(string)
            broker = requests.get(string)
            broker_ip = json.loads(broker.text)["IP"]
            rest_port = json.loads(broker.text)["rest_port"]
            connected = 1
            print("Service started")
        except:
            print("The catalog is not reachable!")
            print("Retrying in %d seconds..." % SEC)
            time.sleep(SEC)

    devID = 'dht_001'
    pub = MyPublisher(devID, broker_ip)
    flag = 1
    pub.start()

    while loop_flag:
        print("Waiting for connection...")
        time.sleep(.1)

    # Update registration on catalog
    while True:
        message = {"devID": devID, resource: value}
        string = 'http://' + broker_ip + ':' + rest_port + '/info/' + devID
        info = json.loads(requests.get(string).text)
        gardenID = info["gardenID"]
        plantID = info["plantID"]
        resources = info["resources"]
        print(gardenID, plantID, resources)

        # Use "resources" to get 'temperature' instead
        pub.my_publish(gardenID + '/' + plantID + '/' + 'temperature',
                       json.dumps(message))
        time.sleep(30)

    pub.stop()

if __name__ == "__main__":
    publisher("dht_5003", "temperature", 5)
