#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script...
"""
import json
import sys, os
import numpy as np
import requests
import schedule
import time
import datetime
import threading
import functions

FILE = "conf.json"
TIME_LIST = []


def get_result(env, hour):
    """Get the last entries on humidity field and decides if it is necessary or
    not to modify duration of irrigation.
    """
    url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
    resource = "humidity"
    time = "minutes"
    tval = str(5*60)
    string = ("http://" + ts_url + ":" + ts_port + "/data/" + plantID + "/" +
              resource + "?time=" + time + "&tval=" + tval + "&plantID=" +
              plantID + "&devID=" + devID)
    print(string)
    data = json.loads(requests.get(string).text)
    data = data["data"]


    if data != []:
        m = np.mean(data)

        diff = env["humidity"] - m
        v = 100 * np.arctan(0.05 * diff)  # Add 300 seconds.
        v = round(v)
    else:
        v = None

    functions.post_mod(plantID, hour, v, 0, url, port)


def main():
    url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
    thread1 = SchedulingThread(1, "thread1")
    thread1.start()

    while True:
        url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
        string = ("http://" + url + ":" + port + "/info/" + plantID)
        data = json.loads(requests.get(string).text)
        hours = data["hours"]
        env = data["environment"]

        global TIME_LIST
        for h in hours:
            t = h["time"]
            delayed_hour = functions.delay_h(t, -300)
            entry = {
            "hour": t,
            "schedule_time": delayed_hour,
            # "schedule_time": "15:43",
            "env": env
            }
            TIME_LIST.append(entry)
            print("Schedule: %s - %s" % (delayed_hour, plantID))

        time.sleep(50)
        TIME_LIST = []


class SchedulingThread(threading.Thread):
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name

    def run(self):
        global TIME_LIST
        while True:
            for e in TIME_LIST:
                if e["schedule_time"] == time.strftime("%H:%M"):
                    get_result(e["env"], e["hour"])
                    TIME_LIST.remove(e)
            time.sleep(3)


if __name__ == '__main__':
    main()
