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

FILENAME = "conf.json"
SEC = 10

def call_sensors(devices):
    # Call sensors.

    for dev in devices:
        d = dev[0:dev.find('_')]
        try:
            func = d + '.get_data()'
            print(eval(func))
        except:
            print("%s is not available!" % d)

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

            #hours = ['17:46']
            for h in hours:
                schedule.every().day.at(h).do(call_sensors, devices)
                print("Schedule: %s > %s > %s" %(p["plantID"], h, devices))

    while True:
        schedule.run_pending()
        time.sleep(3)

if __name__ == '__main__':
    main()
