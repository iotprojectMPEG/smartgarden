#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Light control strategy.

This script takes light records on ThingSpeak channels and decide how to
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
FILE = P / "light.json"
TIME_LIST = []


def get_result(env, hour):
    """Get data from ThingSpeak adaptor and decide.

    Get the last entries on light field and decides if it is necessary or
    not to modify duration of irrigation.
    """
    url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
    resource = "light"
    time = "minutes"
    tval = str(2*60)  # Check light trending in previous hours
    string = ("http://" + ts_url + ":" + ts_port + "/data/" + plantID + "/" +
              resource + "?time=" + time + "&tval=" + tval + "&plantID=" +
              plantID + "&devID=" + devID)
    print(string)
    data = json.loads(requests.get(string).text)
    data = data["data"]

    # Light strategy.
    if data != []:
        m = np.mean(data)
    if type == 'evening':
        if (m >= 140) and (m < 160):  # Very dark
            delay = -1800  # Anticipation of 30 minutes

        elif (m >= 110) and (m < 140):  # Dark
            delay = -900  # Anticipation of 15 minutes

        elif (m >= 90 and m < 110):  # Ideal
            delay = 0  # Ideal time, no delay

        elif (m >= 70 and m < 90):  # Bright
            delay = 1800  # Posticipation of 30 minutes

        elif (m < 70):  # Very bright
            delay = 3600  # Posticipation of 60 minutes

    elif type == 'morning':

        if (m >= 140) and (m < 160):  # Very dark
            delay = 3600  # Posticipation of 60 minutes

        elif (m >= 110) and (m < 140):  # Dark
            delay = 1800  # Posticipation of 30 minutes

        elif (m >= 90 and m < 110):  # Ideal
            delay = 0  # Ideal time, no delay

        elif (m >= 70 and m < 90):  # Bright
            delay = -900  # Anticipation of 15 minutes

        elif (m < 70):  # Very bright
            delay = -1800  # Anticipation of 30 minutes

    if delay is not None:
        functions.post_mod(plantID, hour, 0, delay, url, port)


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
            print("Light check at: %s - %s" % (delayed_hour, plantID))

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
