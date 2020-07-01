#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Humidity control strategy.

This script takes humidity records on ThingSpeak channels and decide how to
edit irrigation parameters.
"""
import json
import requests
import numpy as np
import time
import threading
import functions
from pathlib import Path

P = Path(__file__).parent.absolute()
FILE = P / "hum.json"
TIME_LIST = []


def get_result(env, hour):
    """Get data from ThingSpeak adaptor and decide.

    Get the last entries on humidity field and decides if it is necessary or
    not to modify duration of irrigation.
    """
    url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
    resource = "humidity"
    time = "minutes"
    tval = str(5*60)  # Check humidity trending in previous hours
    string = ("http://" + ts_url + ":" + ts_port + "/data/" + plantID + "/" +
              resource + "?time=" + time + "&tval=" + tval + "&plantID=" +
              plantID + "&devID=" + devID)
    print(string)
    data = json.loads(requests.get(string).text)
    data = data["data"]

    # Humidity strategy.
    if data != []:
        m = np.mean(data)

        diff = np.abs(env["humidity"] - m)
        duration = 100 * np.arctan(0.05 * diff)  # Add 300 seconds.
        duration = round(duration)
    else:
        duration = None

    if duration is not None:
        functions.post_mod(plantID, hour, duration, 0, url, port)


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
            TIME_LIST.append(entry)  # Fill timetable.
            print("Humidity check at: %s - %s" % (delayed_hour, plantID))

        time.sleep(86400)  # One day
        TIME_LIST = []  # Reset timetable


class SchedulingThread(threading.Thread):
    """Scheduling thread to call strategy."""

    def __init__(self, ThreadID, name):
        """Initialise thread."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name

    def run(self):
        """Run thread.

        Check if current hour correspond to one entry in the timetable, if so
        call the strategy and remove the current hour from the timetable.
        """
        global TIME_LIST
        while True:
            for e in TIME_LIST:
                if e["schedule_time"] == time.strftime("%H:%M"):
                    get_result(e["env"], e["hour"])
                    TIME_LIST.remove(e)
            time.sleep(3)


if __name__ == '__main__':
    main()
