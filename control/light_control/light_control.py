#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script...
"""
import json
import sys, os
import requests
import numpy as np

FILE = "conf.json"
FIELD = 6  # Da prendere altrove.


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


def get_result(plantID, devID, type):
    """Get the last entries on humidity field and decides if it is necessary or not
    to adjust
    """
    readAPI, channelID = get_api(plantID)

    url, port = read_file(FILE)
    string = "http://" + url + ":" + port + "/info/" + devID
    r = json.loads(requests.get(string).text)
    for i in r["resources"]:
        if i["n"]=="light":
            f=i["f"]

    fieldID = str(f)
    channelID = str(channelID)
    readAPI = str(readAPI)
    minutes = str(10)
    string = ("https://api.thingspeak.com/channels/" + channelID + "/fields/" +
              fieldID + ".json?api_key=" + readAPI + "&minutes=" + minutes)
    res = json.loads(requests.get(string).text)
    data = []
    for r in res["feeds"]:
        try:
            data.append(int(r["field"+str(f)])) #
        except:
            pass

    if data != []:
        m = np.mean(data)


    if type ==  'evening':

        if (m >= 100) and (m < 120):
            return 1800

        elif (m >= 120) and (m < 180):
            return 3600

        elif (m >= 180):
            return 7200

        elif (m >= 80 and m < 100):
            return 0

        elif (m < 80):
            return -900


    elif type == 'morning':
        if (m >= 100) and (m < 120):
            return -1800

        elif (m >= 120) and (m < 180):
            return -3600

        elif (m >= 180):
            return -7200

        elif (m >= 80 and m < 100):
            return 0

        elif (m < 80):
            return +900



    def main():
        print(get_result("p_1001"))  # Example.


    if __name__ == '__main__':
        main()
