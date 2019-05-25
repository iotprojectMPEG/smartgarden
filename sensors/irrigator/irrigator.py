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

import os, sys, inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import updater

TOPIC = 'smartgarden/+/+/irrigation'
FILENAME = "conf.json"


def irrigate(id, time=300):
    print("Starting irrigation on %s" % id)


class PublisherSubscriber:
    def __init__(self, clientID, topic, serverIP, port):
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = serverIP
        self.port = port
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received
        self.loop_flag = 1

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        print ("Connected to %s - Result code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        msg.payload = msg.payload.decode("utf-8")
        message = json.loads(msg.payload)
        dev = message["devID"]
        try:
            duration = message["duration"]
            irrigate(dev, duration)
        except:
            irrigate(dev)


class PubData(threading.Thread):
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.devID, self.url, self.port) = updater.read_file("conf.json")
        print(">>> Irrigator %s <<<\n" %(self.devID))
        (self.gardenID, self.plantID,
                        self.resources) = updater.find_me(self.devID,
                        self.url, self.port)
        (self.broker_ip, mqtt_port) = updater.broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

        self.topic = []
        for r in self.resources:
            self.topic.append('smartgarden/' + self.gardenID + '/'
                              + self.plantID + '/' + r)

    def run(self):
        print("Topics:", self.topic)
        pubsub = PublisherSubscriber(self.devID + '_1', self.topic[0], self.broker_ip,
                          int(self.mqtt_port))
        pubsub.start()

        while pubsub.loop_flag:
            print("Waiting for connection...")
            time.sleep(1)

        while True:
            time.sleep(60)

        pubsub.stop()


def main():
    thread1 = updater.Alive(1, "Alive")
    thread2 = PubData(2, "PubData")

    thread1.start()
    time.sleep(1)
    thread2.start()


if __name__ == '__main__':
    main()
