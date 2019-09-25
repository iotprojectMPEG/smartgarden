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
FIELD = 2  # Da prendere altrove.


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


def get_result(plantID, devID, env):
    """Get the last entries on humidity field and decides if it is necessary or not
    to adjust
    """
    readAPI, channelID = get_api(plantID)

    url, port = read_file(FILE)
    string = "http://" + url + ":" + port + "/info/" + devID
    r = json.loads(requests.get(string).text)
    for i in r["resources"]:
        if i["n"]=="humidity":
            f=i["f"]

    fieldID = str(f)
    channelID = str(channelID)
    readAPI = str(readAPI)
    hours = str(3)
    string = ("https://api.thingspeak.com/channels/" + channelID + "/fields/" +
              fieldID + ".json?api_key=" + readAPI + "&hours=" + hours)
    res = json.loads(requests.get(string).text)
    print(string)
    data = []
    for r in res["feeds"]:
        try:
            data.append(int(r["field"+str(f)])) #
        except:
            pass

    if data != []:
        m = np.mean(data)

        diff = env["humidity"] - m
        v = 100 * np.arctan(0.05 * diff)  # Add 300 seconds.
        return v

    else:
        return None

def main():
    env = {"humidity": 10}
    print(get_result("p_1001", env))  # Example.
    env = {"humidity": 30}
    print(get_result("p_1001", env))  # Example.
    env = {"humidity": 70}
    print(get_result("p_1001", env))  # Example.
    env = {"humidity": 90}
    print(get_result("p_1001", env))  # Example.

if __name__ == '__main__':
    main()
