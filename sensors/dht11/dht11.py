#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real humidity and temperature sensor.
"""

try:
    import Adafruit_DHT
except:
    pass

import json
import time
import paho.mqtt.client as PahoMQTT
import threading

import os, sys, inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import updater

SENSOR = 11
PIN = 17

def get_data():
    """Get humidity and temperature from sensor. Return two jsons.
    """
    # Initialization.
    humidity = -1
    temperature = -1

    # Read data from sensor
    try:
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN,
                                                        retries=3,
                                                        delay_seconds=2)
    except:
        pass

    data_h = {
        "res": "humidity",
        "value": humidity
        }

    data_t = {
        "res": "temperature",
        "value": temperature
    }

    return (data_h, data_t)


class PubData(threading.Thread):
    """Publish sensor data with MQTT every minute.
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.devID, self.url, self.port) = updater.read_file("conf.json")
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

        pub1 = MyPublisher(self.devID + '_1', self.topic[0], self.broker_ip,
                          int(self.mqtt_port))
        pub1.start()
        pub2 = MyPublisher(self.devID + '_2', self.topic[1], self.broker_ip,
                          int(self.mqtt_port))
        pub2.start()

        while (pub1.loop_flag or pub2.loop_flag):
            print("Waiting for connection...")
            time.sleep(1)

        while True:
            (hum, temp) = get_data()
            pub1.my_publish(json.dumps(hum))
            pub2.my_publish(json.dumps(temp))
            time.sleep(60)

        sub.stop()


class MyPublisher(object):
    def __init__(self, clientID, topic, serverIP, port):
        self.clientID = clientID + '_pub'
        self.devID = clientID
        self.topic = topic
        self.port = port
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self.loop_flag = 1

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        print ("Connected to %s - Res code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_publish(self, message):
        print("Publishing %s on %s" %(message, self.topic))
        self._paho_mqtt.publish(self.topic, message, 2)


def main():
    thread1 = updater.Alive(1, "Alive")
    thread2 = PubData(2, "PubData")

    thread1.start()
    time.sleep(1)
    thread2.start()


if __name__ == '__main__':
    main()
