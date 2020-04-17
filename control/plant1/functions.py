#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common functions to control strategies."""
import datetime
import json
import requests
from cmath import rect, phase
from math import radians, degrees


# def return_info(ID):
#
#     string = "http://" + url + ":" + str(port) + "/info"
#     info = requests.get(string, data=json.dumps(data))
#     print(info)
#     return info



def delay_h(h, delta):
    """Add seconds to a given hour.

    Takes as inputs an hour in format "XX:XX" and a number of seconds which
    has to be added. Returns the delayed hour in format "XX:XX".
    """
    h = datetime.datetime.strptime(h, '%H:%M')
    h = h + datetime.timedelta(seconds=delta)
    h = format(h, '%H:%M')
    return h


def post_mod(plantID, hour, duration, delay, url, port):
    """Send POST to catalog to change irrigation parameters."""
    data = {
        "plantID": plantID,
        "hour": hour,
        "duration": duration,
        "delay": delay
    }

    # POST on catalog.
    string = "http://" + url + ":" + str(port) + "/edit_hour"
    print("Publishing:\n", json.dumps(data, indent=1))
    requests.post(string, data=json.dumps(data))


def post_mod_hour(plantID, vector, url, port):
    """Send POST to catalog to change irrigation parameters."""
    data = {
        "plantID": plantID,
        "hours": vector
    }

    # POST on catalog.
    string = "http://" + url + ":" + str(port) + "/update/time"
    print("Publishing:\n", json.dumps(data, indent=1))
    requests.post(string, data=json.dumps(data))


def post_delay(plantID, hour, new_hour, url, port):
    """Send POST to catalog to change irrigation parameters.

    (Different from post_mod)
    """
    data = {
        "plantID": plantID,
        "hour": hour,
        "new_hour": new_hour
    }

    # POST on catalog.
    string = "http://" + url + ":" + str(port) + "/edit_hour_delay"
    print(json.dumps(data, indent=1))
    requests.post(string, data=json.dumps(data))


def reset_mod(plantID, hour, url, port):
    """Send POST to catalog to reset irrigation parameters."""
    data = {
        "plantID": plantID,
        "hour": hour
    }

    # POST on catalog.
    string = "http://" + url + ":" + str(port) + "/reset_hour"
    print(json.dumps(data, indent=1))
    requests.post(string, data=json.dumps(data))


def read_file(filename):
    """Read json file to get catalogURL, port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        cat_url = data["cat_ip"]
        cat_port = data["cat_port"]
        string = "http://" + cat_url + ":" + cat_port
        ts = json.loads(requests.get(string + '/ts').text)
        ts_url, ts_port = ts["IP"], ts["port"]
        plantID = data["plantID"]
        devID = data["devID"]
        return (cat_url, cat_port, plantID, devID, ts_url, ts_port)


def mean_angle(deg):
    return degrees(phase(sum(rect(1, radians(d)) for d in deg)/len(deg)))


def mean_time(times):
    t = (time.split(':') for time in times)
    seconds = ((float(s) + int(m) * 60 + int(h) * 3600)
               for h, m, s in t)
    day = 24 * 60 * 60
    to_angles = [s * 360. / day for s in seconds]
    mean_as_angle = mean_angle(to_angles)
    mean_seconds = mean_as_angle * day / 360.
    if mean_seconds < 0:
        mean_seconds += day
    h, m = divmod(mean_seconds, 3600)
    m, s = divmod(m, 60)
    return '%02i:%02i' % (h, m)
