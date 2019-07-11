#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import json
import paho.mqtt.client as PahoMQTT
import time
import datetime
import sys,os,inspect
import threading
import requests

#TOPIC = 'smartgarden/+/+/+'
loop_flag = 1

def read_file(filename):
    """Read json file to get devID, catalogURL and port.
    """
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["catalogURL"]
        topic = data["topic"]
        port = data["port"]
        return (url, port, topic)

def broker_info(url, port):
    """Send GET request to catalog in order to obrain MQTT broker info.
    """
    string = "http://"+ url + ":" + port + "/broker"
    broker = requests.get(string)
    broker_ip = json.loads(broker.text)["IP"]
    mqtt_port = json.loads(broker.text)["mqtt_port"]
    return (broker_ip, mqtt_port)

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
        print ("S - Connected to %s - Result code: %d" % (self.messageBroker, rc))
        loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        try:
            # Read conf.json file
            (self.url, self.port, self.topic) = read_file("conf.json")

            # Decode received message and find devID
            msg.payload = msg.payload.decode("utf-8")
            message = json.loads(msg.payload)
            devID = message['bn']

            # Ask catalog for plantID from devID
            string = "http://" + self.url + ":" + self.port + "/info/" + devID
            info_d = json.loads(requests.get(string).text)
            plantID = info_d["plantID"]

            # Ask catalog the thingspeakID for that specific plantID.
            string = "http://" + self.url + ":" + self.port + "/info/" + plantID
            info = json.loads(requests.get(string).text)
            thingspeakID = info['thingspeakID']

            # Ask catalog the APIs for that ThingSpeak ID.
            string = ("http://" + self.url + ":" + self.port +
                       "/api/tschannel/" + str(thingspeakID))
            info = json.loads(requests.get(string).text)
            write_API = info["writeAPI"]

            # Convert UNIX timestamp to ISO 8601
            for item in message["e"]:
                creation_time = message["bt"] + item["t"]

            creation_time = datetime.datetime.utcfromtimestamp(creation_time).isoformat()
            req_tt = ('https://api.thingspeak.com/update?api_key=' +
                      write_API + '&created_at=' + str(creation_time))

            for item in message["e"]:
                if item["n"] == 'alive':
                    pass  # Ignoring alive messages.
                else:
                    topic = item["n"]
                    for item2 in info_d["resources"]:
                        if item2["n"] == topic:
                            feed = item2["f"]

                    req_tt += ('&field' + str(feed) + '=' + str(item['v']))

            request = requests.get(req_tt)
            print("UPDATING: %s" % req_tt)

        except:
            pass


class SubData(threading.Thread):
    """Publish sensor data with MQTT every minute.
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.url, self.port, self.topic) = read_file("conf.json")
        (self.broker_ip, mqtt_port) = broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)


    def run(self):

        sub = MySubscriber("Thingspeak", self.topic, self.broker_ip)
        sub.start()

        while loop_flag:
            print("Waiting for connection...")
            time.sleep(.01)

        while True:
            time.sleep(5)

        sub.stop()


if __name__ == "__main__":
    thread1 = SubData(1, "SubData")
    thread1.start()
