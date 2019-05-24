#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Activates sensors in specific moments of the day.
"""

import dht11 as dht
import wind

import json
import requests
import schedule
import time
import sys
import paho.mqtt.client as Pub

FILENAME = "conf.json"
SEC = 10


class MyPublisher(object):
    def __init__(self,clientID, ip, port):
        print(ip)
        print(port)
        self.clientID = clientID
        self.publisher = Pub.Client(self.clientID, False)
        self.publisher.on_publish = self.onpublish
        self.ip = ip
        self.port = int(port)

    def onpublish(self, client, userdata, mid):
        print("Message published on the message broker")

    def start(self):
        self.publisher.connect(self.ip, self.port)
        self.publisher.loop_start()

    def stop(self):
        self.publisher.loop_stop()
        self.publisher.disconnect()

    def myPublish(self,topic,message):
        self.publisher.publish(topic, message, qos=2)


def call_sensors(devices, ip, port):
    print(devices)

    sensor_list = {
        "sensors": []
    }
    for i in range(len(devices)):
        id={
            "devID":devices[i]
        }
        sensor_list["sensors"].insert(i,id)

    publisher = MyPublisher("Sens_list", ip, port)
    publisher.myPublish("smartgarden/commands", json.dumps(sensor_list))


def main():

    with open(FILENAME, "r") as f:
        conf = json.loads(f.read())

    url = conf["catalogURL"]
    port = conf["port"]

    string = "http://" + url + ":" + port + "/static"
    broker_string = "http://" + url + ":" + port + "/broker"

    connected = 0
    while connected == 0:
        try:
            static = json.loads(requests.get(string).text)
            broker_info = json.loads(requests.get(broker_string).text)
            broker_ip = broker_info["IP"]
            mqtt_port = broker_info["mqtt_port"]
            connected = 1
            print("Service started")
        except:
            print("The catalog (%s) is not reachable!" % string)
            print("Retrying in %d seconds..." % SEC)
            time.sleep(SEC)

    for g in static["gardens"]:
        for p in g["plants"]:
            hours = p["hours"]
            devices = []
            for d in p["devices"]:
                devices.append(d["devID"])

            hours = ['16:33']
            for h in hours:
                schedule.every().day.at(h).do(call_sensors, devices,
                                              broker_ip, mqtt_port)
                print("Schedule: %s > %s > %s" %(p["plantID"], h, devices))

    while True:
        schedule.run_pending()
        time.sleep(3)

if __name__ == '__main__':
    main()
