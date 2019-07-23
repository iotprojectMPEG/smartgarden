#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script...
"""
import json
import sys, os
import threading
import requests
import time
import datetime
import schedule
from rain_control import rain_control
from light_control import light_control
from wind_control import wind_control
from hum_control import hum_control
from temp_control import temp_control

FILE1 = "conf.json"
LIST = []  # Plant list
URL = None  # Catalog URL
PORT = None  # Catalog port


def read_file(filename):
    """Read json file to get catalogURL, port and gardenID."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["catalogURL"]
        port = data["port"]
        gardenID = data["gardenID"]

        global URL
        URL = url
        global PORT
        PORT = port

        return (url, port, gardenID)


def post_mod(plantID, h, mod):
    data = {
        "plantID": plantID,
        "hour": h,
        "mod": mod
    }
    string = "http://" + URL + ":" +str(PORT) + "/hours"

    # Write on catalog.
    print(string)
    print(json.dumps(data))
    r = requests.post(string, data=json.dumps(data))


def rain(plantID, h, type):
    if rain_control.get_result(plantID):
        pass


def light(plantID, h, type):
    print(plantID, type)
    sec = rain_control.get_result(plantID)
    pass


def wind(plantID, h, type):
    sec = wind_control.get_result(plantID)
    post_mod(plantID, h, sec)
    pass


def hum(plantID, h, type):
    sec = hum_control.get_result(plantID)
    pass


def temp(plantID, h, type):
    sec = temp_control.get_result(plantID)
    pass


class Plant(threading.Thread):
    def __init__(self, ThreadID, name, list):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        self.list = list

    def run(self):
        # Create schedules.
        for p in self.list:
            for h in p["hours"]:
                for d in p["devices"]:
                    for r in d["resources"]:
                        res = r["n"]
                        if res == 'rain':
                            print("Scheduling %s for %s at %s" % (res, p["plantID"], h["time"]))
                            schedule.every().day.at(h["time"]).do(rain, p["plantID"], h["time"], h["type"])
                        if res == 'light':
                            print("Scheduling %s for %s at %s" % (res, p["plantID"], h["time"]))
                            schedule.every().day.at(h["time"]).do(light, p["plantID"], h["time"], h["type"])
                        if res == 'wind':
                            print("Scheduling %s for %s at %s" % (res, p["plantID"], h["time"]))
                            schedule.every().day.at(h["time"]).do(wind, p["plantID"], h["time"], h["type"])
                        if res == 'humidity':
                            print("Scheduling %s for %s at %s" % (res, p["plantID"], h["time"]))
                            schedule.every().day.at(h["time"]).do(hum, p["plantID"], h["time"], h["type"])
                        if res == 'temperature':
                            print("Scheduling %s for %s at %s" % (res, p["plantID"], h["time"]))
                            schedule.every().day.at(h["time"]).do(temp, p["plantID"], h["time"], h["type"])

        # Check schedules every 30 seconds.
        while True:
            schedule.run_pending()
            time.sleep(30)


        # To do later:
        # if 'light' in self.resources:
        #     sec = light_control.get_result()
        #     h = datetime.datetime.strptime(self.hours, '%H:%M')
        #     h = h + datetime.timedelta(seconds=sec)
        #     h = format(h, '%H:%M')
        #     print(h)


class UpdateList(threading.Thread):
    """Updates global list of plants every day. If the list is the same as
    before, it does not update it.
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name

    def run(self):
        global LIST
        while True:
            new_list = []
            url, port, gardenID = read_file(FILE1)
            string = "http://" + url + ":" + port + "/static"
            data = json.loads(requests.get(string).text)
            for g in data["gardens"]:
                if g["gardenID"] == gardenID:
                    for p in g["plants"]:
                        new_list.append(p)

            if LIST != new_list:
                LIST = new_list
                print("Updated list!")

                # Stop thread.
                try:
                    planter.stop()
                except:
                    pass

                # (Re)start thread.
                planter = Plant(101, "Planter", new_list)
                planter.start()

            else:
                print("List is up to date.")

            time.sleep(86400)


def main():
    upd = UpdateList(1, "UpdateList")
    upd.start()


if __name__ == '__main__':
    main()
