#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common functions to control strategies."""
import json
import requests
import time
import threading
import functions
import datetime
from pathlib import Path

P = Path(__file__).parent.absolute()
FILE = P / "time.json"
TIME_LIST = []


def get_result():
    """Get data from ThingSpeak adaptor and decide.

    Get the last entries on irrigation field and decides if it is necessary or
    not to modify duration of irrigation.
    """
    url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
    resource = "irrigation"
    time = "days"
    tval = str(7)  # Check irrigation trending in previous days
    string = ("http://" + ts_url + ":" + ts_port + "/data/" + plantID + "/" +
              resource + "?time=" + time + "&tval=" + tval + "&plantID=" +
              plantID + "&devID=" + devID + "&wanttime=1")
    data = json.loads(requests.get(string).text)
    data = data["data"]

    # Time strategy.
    start = '23:59:59'
    end = '12:00:00'

    if data != []:
        morning = []
        evening = []

        for k in data:
            datetime_object = datetime.datetime.strptime(k,
                                                         '%Y-%m-%dT%H:%M:%SZ')
            time = datetime_object.strftime("%H:%M:%S")  # -> "hh:mm:ss"

            if time > start and time < end:  # if is in the morning
                morning.append(time)
            else:  # if is in the evening
                evening.append(time)

        if morning == []:
            mean_evening = functions.mean_time(evening)
            info = json.loads(requests.get("http://" + url + ":" + port +
                                           "/info/" + plantID).text)
            print(info)
            vector = [{"time": info["hours"][0]["time"], "type": "morning"},
                      {"time": mean_evening, "type": "evening"}]

        elif evening == []:
            mean_morning = functions.mean_time(morning)
            info = json.loads(requests.get("http://" + url + ":" + port +
                                           "/info/" + plantID).text)
            vector = [{"time": mean_morning, "type": "morning"},
                      {"time": info["hours"][1]["time"], "type": "evening"}]

        else:
            mean_evening = functions.mean_time(evening)
            mean_morning = functions.mean_time(morning)
            vector = [{"time": mean_morning, "type": "morning"},
                      {"time": mean_evening, "type": "evening"}]
    else:
        return

    functions.post_mod_hour(plantID, vector, url, port)  # POST to catalog


def main():
    """Schedule and run strategy."""
    url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
    thread1 = SchedulingThread(1, "thread1")
    thread1.start()

    while True:
        url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
        string = ("http://" + url + ":" + port + "/info/" + plantID)
        data = json.loads(requests.get(string).text)
        env = data["environment"]

        global TIME_LIST
        entry = {
            "schedule_time": "18:47",
            "env": env
            }
        TIME_LIST.append(entry)  # Fill timetable.
        print("Time check at: 12:00 - %s" % (plantID))

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
                    get_result()
                    TIME_LIST.remove(e)
            time.sleep(3)


if __name__ == '__main__':
    main()
