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
import sys

import dht11 as dht
import wind

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

            string = ("http://"+config["catalogURL"]+ ":" +
                       config["port"] + "/static")
            static = json.loads(requests.get(string).text)
            connected = 1
            print("Service started")
        except:
            print("The catalog is not reachable!")
            print("Retrying in %d seconds..." % SEC)
            time.sleep(SEC)

    pub = MyPublisher(devID, broker_ip)
    flag = 1
    pub.start()


    while loop_flag:
        print("Waiting for connection...")
        time.sleep(.1)

    # Update registration on catalog
    while True:
        for g in static["gardens"]:
            for p in g["plants"]:
                for d in p["devices"]:
                    devID = d["devID"]

                    (gardenID, plantID, resources, status) = check_device(devID, broker_ip, rest_port)

                    message = {"devID": devID}
                    if status == 1:
                        for r in resources:
                            print("Updating %s" % devID)
                            pub.my_publish(gardenID + '/' + plantID + '/' +
                                           r, json.dumps(message))
                    else:
                        print("%s is not working now!" % devID)

                    time.sleep(2)  # Let the catalog write json files.
        time.sleep(60)  # Wait 60 seconds and then repeat.

    pub.stop()

def check_device(devID, broker_ip, rest_port):
    string = 'http://' + broker_ip + ':' + rest_port + '/info/' + devID
    info = json.loads(requests.get(string).text)
    gardenID = info["gardenID"]
    plantID = info["plantID"]
    resources = info["resources"]

    if (1 == 1): # Check if the sensor is active...
        d = devID[0:devID.find('_')]

        try:
            func = d + '.get_data()'
            data = eval(func)

            # Add data control...

            status = 1
        except:
            status = 0

    return (gardenID, plantID, resources, status)

if __name__ == "__main__":
    publisher("dht_5003", "temperature", 5)
