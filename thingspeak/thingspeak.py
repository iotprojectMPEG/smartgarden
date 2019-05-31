#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import json
import paho.mqtt.client as PahoMQTT
import time
import datetime
import sys,os,inspect
import threading
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import updater
#TOPIC = 'smartgarden/+/+/+'

def get_API_key(thingspeakID):
    with open("api.json", "r") as f:
        data = json.loads(f.read())
        for item in data["channels"]:
            if item["ID"]==thingspeakID:
                return item["writeAPI"]

def publish_thingspeak(num_api,field):
    RequestToThingspeak = 'https://api.thingspeak.com/update?api_key='+num_api

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
        msg.topic= msg.topic.decode("utf-8")
        url=msg.topic.split('/')
        sensor_ID=url[3]
        message = json.loads(msg.payload)
        # Funzione che ritorna thingspeakID
        thingspeakID= updater.get_thingspeak_channel("static.json",url)
        #Funzione che associa thingspeakID con writeAPI
        writeapi=get_API_key(thingspeakID)
        #Funzione che pubblica su Thingspeak (Gennaro)

        

class SubData(threading.Thread):
    """Publish sensor data with MQTT every minute.
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.url, self.port, self.topic) = updater.read_file("conf.json")
        (self.broker_ip, mqtt_port) = updater.broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)


    def run(self):

        sub = MySubscriber("Thingspeak", self.topic, self.broker_ip,
                          int(self.mqtt_port))
        loop_flag = 1
        sub.start()

        while loop_flag:
            print("Waiting for connection...")
            time.sleep(.01)

        while True:
            time.sleep(5)

        sub.stop()
        # sub.start()
        # # pub2 = MyPublisher(self.devID + '_2', self.topic[1], self.broker_ip,
        #                   # int(self.mqtt_port))
        # # pub2.start()
        #
        # while pub.loop_flag:
        #     print("Waiting for connection...")
        #     time.sleep(1)
        #
        # while True:
        #     data = get_data(self.devID, self.resources)
        #     pub.my_publish(json.dumps(data))
        #     # pub2.my_publish(json.dumps(temp))
        #     time.sleep(60)
        #
        # sub.stop()


if __name__ == "__main__":
