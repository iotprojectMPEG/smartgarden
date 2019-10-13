#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collection of functions and classes which are used by other sensor scripts.
It includes catalog related GET functions and a thread to send "alive" messages
in order to update timestamps on catalog.
"""

import paho.mqtt.client as PahoMQTT
import time
import datetime
import json
import requests
import sys
import threading


def read_file(filename):
    """Read json file to get devID, catalogURL and port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["catalogURL"]
        devID = data["devID"]
        port = data["port"]
        return (devID, url, port)


def find_me(devID, url, port):
    """Send GET request to catalog with devID in order to obtain gardenID,
    plantID, resources associated to the sensor.
    Used by the sensors in order to build the MQTT topic.
    """
    string = "http://" + url + ":" + port + "/info/" + devID
    info = json.loads(requests.get(string).text)
    gardenID = info["gardenID"]
    plantID = info["plantID"]
    resources = info["resources"]
    return (gardenID, plantID, resources)


def broker_info(url, port):
    """Send GET request to catalog in order to obtain MQTT broker IP and
    port.
    """
    string = "http://"+ url + ":" + port + "/broker"
    broker = requests.get(string)
    broker_ip = json.loads(broker.text)["IP"]
    mqtt_port = json.loads(broker.text)["mqtt_port"]
    return (broker_ip, mqtt_port)


class Alive(threading.Thread):
    """Thread which sends "alive" messages via MQTT to update devices timestamp
    on dynamic catalog. Alive message contains also the sensor topic which
    will be updated on dynamic part of the catalog.
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.devID, self.url, self.port) = read_file("conf.json")
        (self.gardenID, self.plantID, self.resources) = find_me(self.devID,
                                                        self.url, self.port)
        (self.broker_ip, mqtt_port) = broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

    def run(self):
        pub = PubImAlive(self.devID, self.broker_ip, self.mqtt_port)
        pub.start()

        while pub.loop_flag:
            print("Waiting for connection...")
            time.sleep(1)

        topic = ('smartgarden/' + self.gardenID + '/'
                 + self.plantID + '/' + self.devID)
        message = {
          "bn": self.devID,
          "e": [{
            "n": "alive",
            "t": time.time(),
            "v": 1,
            "topic": topic
            }]
        }

        while True:
            for r in self.resources:
                topic = ('smartgarden/' + self.gardenID + '/'
                         + self.plantID + '/' + self.devID)
                print("Publishing %s on %s" %(message, topic))
                pub.my_publish(topic, json.dumps(message))
                time.sleep(300)

        pub.stop()


class PubImAlive(object):
    """Standard MQTT publisher."""
    def __init__(self, clientID, serverIP, port):
        self.clientID = clientID + '_pub'
        self.messageBroker = serverIP
        self.port = port
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self.loop_flag = 1

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        print ("P - Connected to %s - Res code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_publish(self, topic, message):
        self._paho_mqtt.publish(topic, message, 2)
