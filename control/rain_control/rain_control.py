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


# def read_file(filename):
#     """Read json file to get catalogURL, port."""
#     with open(filename, "r") as f:
#         data = json.loads(f.read())
#         url = data["catalogURL"]
#         port = data["port"]
#         return (url, port)

def read_file(filename):
    """Read json file to get catalogURL, port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = "http://" + data["URL"]
        port = data["thing_port"]
        return (url, port)

# def get_api(plantID):
#     """Asks catalog readAPI and channelID."""
#     url, port = read_file(FILE)
#     string = "http://" + url + ":" + port + "/info/" + plantID
#     r = json.loads(requests.get(string).text)
#     channel = r["thingspeakID"]
#     string = "http://" + url + ":" + port + "/api/tschannel/" + str(channel)
#     r = json.loads(requests.get(string).text)
#     readAPI = r["readAPI"]
#     return readAPI, channel


# def get_result(plantID, devID):
    # """Get the last entries on rain field and decides if it is necessary or not
    # to irrigate.
    # """
#     readAPI, channelID = get_api(plantID)
#
#     url, port = read_file(FILE)
#     string = "http://" + url + ":" + port + "/info/" + devID
#     r = json.loads(requests.get(string).text)
#     for i in r["resources"]:
#         if i["n"]=="rain":
#             f=i["f"]
#
#     fieldID = str(f)
#     channelID = str(channelID)
#     readAPI = str(readAPI)
#     hours = str(12)
#     string = ("https://api.thingspeak.com/channels/" + channelID + "/fields/" +
#               fieldID + ".json?api_key=" + readAPI + "&hours=" + hours)
#     res = json.loads(requests.get(string).text)
#     data = []
#     for r in res["feeds"]:
#         try:
#             data.append(int(r["field"+str(f)])) #
#         except:
#             pass
#
    # if data != []:
    #     m = np.mean(data)
    #     print("mean:", m)
    #     if m >= 0.6:  # Rain for at least 60% of the time
    #         return -1  # Do not irrigate
    #
    #     elif (m >= 0.4) and (m < 0.6):  # Rain from 40-60% of the time
    #         return -120  # Remove 120 seconds
    #
    #     else:  # Almost no rain
    #         return 0  # No modifications


def get_result(plantID, devID):
    """Get the last entries on rain field and decides if it is necessary or not
    to irrigate.
    """

    plantID = plantID
    devID = devID
    resource = "Rain"
    time = "hours"
    tval = str(2)
    url, port = read_file(FILE)
    string = (url + ":" + port + "/data/" + plantID + "/" + resource + "?time="
              + time + "&tval=" + tval + "&plantID=" + plantID + "&devID=" +
              devID)

    #"http://127.0.0.1:8081/data/p_1002/temperature?time=hours&tval=11&plantID=p_1001&devID=d_1001"
    data = json.loads(requests.get(string).text)
    data = data["data"]
    if data != []:
        m = np.mean(data)
        print("mean:", m)
        if m >= 0.6:  # Rain for at least 60% of the time
            return -1  # Do not irrigate

        elif (m >= 0.4) and (m < 0.6):  # Rain from 40-60% of the time
            return -120  # Remove 120 seconds

        else:  # Almost no rain
            return 0  # No modifications


def main():
    print(get_result("p_1002", "d_1006"))  # Example.


if __name__ == '__main__':
    main()
