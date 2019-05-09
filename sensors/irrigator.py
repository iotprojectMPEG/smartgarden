#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start irrigators.
"""

import json
import requests
import threading
import paho.mqtt.client as PahoMQTT
import time

TOPIC = 'smartgarden/+/+/irrigate'
FILENAME = "conf.json"

class MySubscriber:
    def __init__(self, clientID, topic, serverIP):
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        global loop_flag
        print ("Connected to %s - Result code: %d" % (self.messageBroker, rc))
        loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        msg.payload = msg.payload.decode("utf-8")
        message = json.loads(msg.payload)
        print(message)
        dev = message["devID"]
        print(message)
        print("Starting irrigation on %!" %(dev))




if __name__ == '__main__':
    with open("conf.json") as f:
        config = json.loads(f.read())

    # Get broker IP from the catalog
    string = "http://" + config["catalogURL"] + ":" + config["port"] + "/broker"
    broker = requests.get(string)
    broker_ip = json.loads(broker.text)["IP"]
    rest_port = json.loads(broker.text)["rest_port"]

    sub = MySubscriber("Irrigator_sub", TOPIC, broker_ip)

    loop_flag = 1
    sub.start()

    while loop_flag:
        print("Waiting for connection...")
        time.sleep(.1)

    while True:
        time.sleep(1)

    sub.stop()
