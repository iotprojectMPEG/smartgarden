#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common functions to control strategies."""
import datetime
import json
import requests


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
    print(json.dumps(data, indent=1))
    requests.post(string, data=json.dumps(data))


def post_mod_static():
    """Send POST to catalog to change irrigation parameters.

    (Different from post_mod)
    """
    pass


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
        cat_url = data["catalogURL"]
        cat_port = data["port"]
        string = "http://" + cat_url + ":" + cat_port
        ts = json.loads(requests.get(string + '/ts').text)
        ts_url, ts_port = ts["IP"], ts["port"]
        plantID = data["plantID"]
        devID = data["devID"]
        return (cat_url, cat_port, plantID, devID, ts_url, ts_port)
