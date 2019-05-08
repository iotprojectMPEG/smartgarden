#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Activates sensors in specific moments of the day.
"""

import json
import requests
import schedule
import time

FILENAME = "conf.json"

def call_sensors():
    #Call sensors
    print("Calling...")
    pass

def main():

    with open(FILENAME, "r") as f:
        conf = json.loads(f.read())

    url = conf["catalogURL"]
    port = conf["port"]

    string = "http://" + url + ":" + port + "/static"
    static = json.loads(requests.get(string).text)

    for g in static["gardens"]:
        hours = g["hours"]

    # Schedule times.
    for h in hours:
        schedule.every().day.at(h).do(call_sensors)

while True:
    schedule.run_pending()
    time.sleep(60)

if __name__ == '__main__':
    main()
