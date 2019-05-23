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
    def __init__(self,clientID):
        self.clientID=clientID
        self.publisher=Pub.Client(self.clientID,False)
        self.publisher.on_publish=self.onpublish
    def onpublish(self,client, userdata, mid):
        print("Message published on the message broker")
    def start(self):
        self.publisher.connect("iot.eclipse.org")
        self.publisher.loop_start()
    def stop(self):
        self.publisher.loop_stop()
        self.publisher.disconnect()
    def myPublish(self,topic,message):
        self.publisher.publish(topic,message,qos=1)
    pass


def call_sensors(devices):
    print(devices)

    """
    1. Create a json:
    {
        "sensors": [{
            "devID": "dht_001"
        }, {
            "devID": "dht_002"
        }]
    }
    where "dht_001", "dht_002", are inside "devices"

    

    2. Publish a MQTT message in 'smartgarden/commands' with that json
    """

    sensor_list={
        "sensors": []
    }
    for i in range(len(devices)):
        id={
            "devID":devices[i]
        }
        sensor_list["sensors"].insert(i,id)

    publisher=MyPublisher("Sens_list")
    publisher.myPublish("smartgarden/commands",json.dumps(sensor_list))
def main():

    with open(FILENAME, "r") as f:
        conf = json.loads(f.read())

    url = conf["catalogURL"]
    port = conf["port"]

    string = "http://" + url + ":" + port + "/static"

    connected = 0
    while connected == 0:
        try:
            static = json.loads(requests.get(string).text)
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

            hours = ['15:23']
            for h in hours:
                schedule.every().day.at(h).do(call_sensors, devices)
                print("Schedule: %s > %s > %s" %(p["plantID"], h, devices))

    while True:
        schedule.run_pending()
        time.sleep(3)

if __name__ == '__main__':
    main()
