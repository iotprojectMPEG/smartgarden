#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script takes rain records on ThingSpeak channels and decide whether to
irrigate or not.
"""
import json
import sys, os
import requests
import numpy as np

FILE = "conf.json"
FIELD = 5  # Da prendere altrove.


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


def get_result(plantID, env):
    """Get the last entries on rain field and decides if it is necessary or not
    to irrigate.
    """
    readAPI, channelID = get_api(plantID)
    fieldID = str(FIELD)
    channelID = str(channelID)
    readAPI = str(readAPI)
    hours = str(12)
    string = ("https://api.thingspeak.com/channels/" + channelID + "/fields/" +
              fieldID + ".json?api_key=" + readAPI + "&hours=" + hours)
    res = json.loads(requests.get(string).text)
    data = []
    for r in res["feeds"]:
        try:
            data.append(int(r["field5"])) # Da cambiare.
        except:
            pass

    if data != []:
        m = np.mean(data)
        print("mean:", m)
        if m >= 0.6:
            return -1  # Do not irrigate.

        elif (m => 0.2) and (m < 0.6):
            return -120  # Remove 120 seconds.

        else:
            return 0  # No modifications.


def main():
    print(get_result("p_1002"))  # Example.


if __name__ == '__main__':
    main()
