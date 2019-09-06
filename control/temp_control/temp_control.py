#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script...
"""
import json
import sys, os
import numpy as np
import requests

FILE = "conf.json"
FIELD = 1  # Da prendere altrove.


def read_file(filename):
    """Read json file to get catalogURL, port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["catalogURL"]
        port = data["port"]
        return (url, port)


def get_api(plantID):
    """Asks catalog readAPI and channelID."""
    url, port = read_file(FILE)
    string = "http://" + url + ":" + port + "/info/" + plantID
    r = json.loads(requests.get(string).text)
    channel = r["thingspeakID"]
    string = "http://" + url + ":" + port + "/api/tschannel/" + str(channel)
    r = json.loads(requests.get(string).text)
    readAPI = r["readAPI"]
    return readAPI, channel


def get_result(plantID):
    """Get the last entries on humidity field and decides if it is necessary or not
    to adjust
    """
    readAPI, channelID = get_api(plantID)
    fieldID = str(FIELD)
    channelID = str(channelID)
    readAPI = str(readAPI)
    hours = str(11)
    string = ("https://api.thingspeak.com/channels/" + channelID + "/fields/" +
              fieldID + ".json?api_key=" + readAPI + "&hours=" + hours)
    res = json.loads(requests.get(string).text)
    print(string)
    data = []
    for r in res["feeds"]:
        try:
            data.append(int(r["field1"]))  # Field number (?).
        except:
            pass

    if data != []:
        m = np.mean(data)

        v = 80 * np.arctan(0.05 * m)  # Add 300 seconds.
        return v

    else:
        return None

def main():

    print(get_result("p_1001"))  # Example.

if __name__ == '__main__':
    main()
