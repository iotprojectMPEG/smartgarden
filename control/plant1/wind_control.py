#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wind control strategy.

This script takes wind records on ThingSpeak channels and decide how to
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
FILE = P / "wind.json"
TIME_LIST = []


def get_result(env, hour):
    """Get data from ThingSpeak adaptor and decide.

    Get the last entries on wind field and decides if it is necessary or
    not to modify duration of irrigation.
    """
    url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
    resource = "wind"
    time = "minutes"

    # Check wind trending in previous minutes (short term).
    tval = str(10)
    string = ("http://" + ts_url + ":" + ts_port + "/data/" + plantID + "/" +
              resource + "?time=" + time + "&tval=" + tval + "&plantID=" +
              plantID + "&devID=" + devID)
    print(string)
    data = json.loads(requests.get(string).text)
    data_short = data["data"]

    # Check wind trending in previous hours (long term).
    tval = str(10*60)
    string = ("http://" + ts_url + ":" + ts_port + "/data/" + plantID + "/" +
              resource + "?time=" + time + "&tval=" + tval + "&plantID=" +
              plantID + "&devID=" + devID)
    print(string)
    data = json.loads(requests.get(string).text)
    data_long = data["data"]

    # Wind strategy.

    val1 = 0
    val2 = 0

    # During an extended period of time.
    if data_long != []:
        m2 = np.mean(data_long)
        if (m2 >= 3) and (m2 <= 10):  # Light wind
            val2 = 60  # Augment duration by 60 seconds
        elif m2 > 10:  # Strong wind
            val2 = 120  # Augment duration by 120 seconds
        else:  # No wind
            val2 = 0  # No modification

    # In real time.
    if data_short != []:
        m1 = np.mean(data_short)
        if (m1 >= 3) and (m1 <= 10):  # Light wind
            val1 = 90  # Augment duration by 90 seconds
        elif m1 > 10:  # Strong wind
            val1 = 150  # Augment duration by 150 seconds
        else:  # No wind
            val1 = 0  # No modification

    duration = val1 + val2
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
            print("Wind check at: %s - %s" % (delayed_hour, plantID))

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
