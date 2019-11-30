#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rain control strategy.

This script takes rain records on ThingSpeak channels and decide whether to
irrigate or not.
"""
import json
import requests
import numpy as np
import functions
import time
import threading

FILE = "conf.json"
TIME_LIST = []


def read_file(filename):
    """Read json file to get catalogURL, port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = "http://" + data["URL"]
        port = data["thing_port"]
        return (url, port)


def get_result(plantID, devID):
    """Get data from ThingSpeak and decide.

    Get the last entries on rain field and decides if it is necessary or not
    to irrigate.
    """
    resource = "rain"
    time = "hours"
    tval = str(2)
    url, port = read_file(FILE)
    string = (url + ":" + port + "/data/" + plantID + "/" + resource + "?time="
              + time + "&tval=" + tval + "&plantID=" + plantID + "&devID=" +
              devID)

    data = json.loads(requests.get(string).text)
    data = data["data"]
    if data != []:
        m = np.mean(data)
        if m >= 0.6:  # Rain for at least 60% of the time
            return -1  # Do not irrigate

        elif (m >= 0.4) and (m < 0.6):  # Rain from 40-60% of the time
            return -120  # Remove 120 seconds

        else:  # Almost no rain
            return 0  # No modifications


def main():
    """Schedule and run strategy."""
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
    """Scheduling thread to call strategy."""

    def __init__(self, ThreadID, name):
        """Initialise thread."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name

    def run(self):
        """Run thread."""
        global TIME_LIST
        while True:
            for e in TIME_LIST:
                if e["schedule_time"] == time.strftime("%H:%M"):
                    get_result(e["env"], e["hour"])
                    TIME_LIST.remove(e)
            time.sleep(3)


if __name__ == '__main__':
    main()
