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


FILE1 = "conf.json"
LIST = []

#
# def write_catalog(filename):


def read_file(filename):
    """Read json file to get catalogURL, port and gardenID."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["catalogURL"]
        port = data["port"]
        gardenID = data["gardenID"]
        return (url, port, gardenID)


def rain(plantID):
    if rain_control.get_result(plantID):
        # Write on catalog.
        pass

def light(plantID):
    sec = rain_control.get_result(plantID)
    # Write on catalog.
    pass

def wind(plantID):
    sec = wind_control.get_result(plantID)
    # Write on catalog.
    pass

def hum(plantID):
    sec = hum_control.get_result(plantID)
    # Write on catalog.
    pass

def temp(plantID):
    sec = temp_control.get_result(plantID)
    # Write on catalog.
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
                            print("Scheduling %s for %s at %s" % (res, p["plantID"], h))
                            schedule.every().day.at(h).do(rain, p["plantID"])
                        if res == 'light':
                            print("Scheduling %s for %s at %s" % (res, p["plantID"], h))
                            schedule.every().day.at(h).do(light, p["plantID"])
                        if res == 'wind':
                            print("Scheduling %s for %s at %s" % (res, p["plantID"], h))
                            schedule.every().day.at(h).do(wind, p["plantID"])
                        if res == 'humidity':
                            print("Scheduling %s for %s at %s" % (res, p["plantID"], h))
                            schedule.every().day.at(h).do(hum, p["plantID"])
                        if res == 'temperature':
                            print("Scheduling %s for %s at %s" % (res, p["plantID"], h))
                            schedule.every().day.at(h).do(temp, p["plantID"])

        # Check schedules every 30 seconds.
        while True:
            schedule.run_pending()
            time.sleep(30)


        # Keep on schedules.
        #
        # if 'rain' in self.resources:
        #     do_not_irrigate = rain_control.get_result("p_1002")
        #     print("Do NOT irrigate:", do_not_irrigate)
        #
        # if 'light' in self.resources:
        #     sec = light_control.get_result()
        #     h = datetime.datetime.strptime(self.hours, '%H:%M')
        #     h = h + datetime.timedelta(seconds=sec)
        #     h = format(h, '%H:%M')
        #     print(h)

        ######################################################################
        # TO DO: write modification on dynamic part of the catalog.
        ######################################################################

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
                        # new_list.append(p["plantID"])
                        new_list.append(p)

            if LIST != new_list:
                LIST = new_list
                print("New list!")#: ", LIST)

                # Stop thread
                try:
                    planter.stop()
                except:
                    pass

                planter = Plant(101, "Planter", new_list)
                planter.start()
                # Restart thread



            else:
                print("List is up to date.")

            time.sleep(86400)


def create_schedules():
    pass


def dummy_schedule(string):
    print("Executed dummy schedule. String: ", string)

def main():
    upd = UpdateList(1, "UpdateList")
    upd.start()

    #plt = Plant(2, "Plant", "p_1001", "08:00")
    #plt.start()

if __name__ == '__main__':
    main()
