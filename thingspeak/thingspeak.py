#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import json
import paho.mqtt.client as PahoMQTT
import time
import datetime

TOPIC = 'smartgarden/+/+/+'
BROKER_IP = '192.168.1.70'


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


if __name__ == "__main__":
    sub = MySubscriber("Thingspeak", TOPIC, BROKER_IP)
    loop_flag = 1
    sub.start()

    while loop_flag:
        print("Waiting for connection...")
        time.sleep(.01)

    while True:
        time.sleep(5)

    sub.stop()
