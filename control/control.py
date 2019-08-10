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


def post_mod(plantID, h, mod=0, modh=0):
    data = {
        "plantID": plantID,
        "hour": h,
        "mod": mod,
        "modh": modh
    }
    string = "http://" + URL + ":" +str(PORT) + "/hours"

    # Write on catalog.
    print(string)
    print(json.dumps(data))
    r = requests.post(string, data=json.dumps(data))


def rain(plantID, h, type, env):
    if rain_control.get_result(plantID, env):
        pass


def light(plantID, h, type, env):
    """Type: morning/evening.
    Morning: anticipate irrigation if there is too much light.
    Evening: posticipate irrigation if there is too much light.
    """
    print(plantID, type)
    sec = rain_control.get_result(plantID, env, type)
    pass


def wind(plantID, h, type, env):
    sec = wind_control.get_result(plantID, env)
    post_mod(plantID, h, sec)
    pass


def hum(plantID, h, type, env):
    sec = hum_control.get_result(plantID, env)
    pass


def temp(plantID, h, type, env):
    sec = temp_control.get_result(plantID, env)
    pass


def delay_h(h, delta):
    """Takes as inputs an hour in format "XX:XX" and a number of seconds which
    has to be added. Returns the delayed hour in format "XX:XX".
    """
    h = datetime.datetime.strptime(h, '%H:%M')
    h = h + datetime.timedelta(seconds=delta)
    h = format(h, '%H:%M')
    return h


class Plant(threading.Thread):
    def __init__(self, ThreadID, name, list):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        self.list = list

    def run(self):
        # Create schedules.
        for p in self.list:
            pID = p["plantID"]
            env = p["environment"]
            for h in p["hours"]:
                t = delay_h(h["time"], -600)
                ty = h["type"]
                for d in p["devices"]:
                    for r in d["resources"]:
                        res = r["n"]
                        if res == 'rain':
                            print("Schedule: %s - %s - %s" % (t, pID, res))
                            schedule.every().day.at(t).do(rain, pID, t, ty, env)
                        if res == 'light':
                            print("Schedule: %s - %s - %s" % (t, pID, res))
                            schedule.every().day.at(t).do(light, pID, t, ty, env)
                        if res == 'wind':
                            print("Schedule: %s - %s - %s" % (t, pID, res))
                            schedule.every().day.at(t).do(wind, pID, t, ty, env)
                        if res == 'humidity':
                            print("Schedule: %s - %s - %s" % (t, pID, res))
                            schedule.every().day.at(t).do(hum, pID, t, ty, env)
                        if res == 'temperature':
                            print("Schedule: %s - %s - %s" % (t, pID, res))
                            schedule.every().day.at(t).do(temp, pID, t, ty, env)

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
