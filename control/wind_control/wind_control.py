#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script takes wind records on ThingSpeak channels and decide how much
irrigation is needed.
"""
import json
import sys, os
import requests
import numpy as np

FILE = "conf.json"
FIELD = 3  # Da prendere altrove.


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
#     """Get the last entries on wind field and decides if it is necessary or not
#     to irrigate.
#     """
#     readAPI, channelID = get_api(plantID)
#
#     url, port = read_file(FILE)
#     string = "http://" + url + ":" + port + "/info/" + devID
#     r = json.loads(requests.get(string).text)
#     for i in r["resources"]:
#         if i["n"] == "wind":
#             f = i["f"]
#
#     fieldID = str(f)
#     channelID = str(channelID)
#     readAPI = str(readAPI)
#     minutes = str(10)
#     hours = str(12)
#
#     string1 = ("https://api.thingspeak.com/channels/" + channelID + "/fields/" +
#               fieldID + ".json?api_key=" + readAPI + "&minutes=" + minutes)
#     res1 = json.loads(requests.get(string1).text)
#     data_short = []
#     for r in res1["feeds"]:
#         try:
#             data_short.append(int(r["field"+str(f)])) #
#         except:
#             pass
#
#     string2 = ("https://api.thingspeak.com/channels/" + channelID + "/fields/" +
#               fieldID + ".json?api_key=" + readAPI + "&hours=" + hours)
#     res2 = json.loads(requests.get(string2).text)
#     data_long = []
#     for r in res2["feeds"]:
#         try:
#             data_long.append(int(r["field"+str(f)]))  # Field number (?).
#         except:
#             pass
#
#     val1 = 0
#     val2 = 0
#
    # # During an extended period of time.
    # if data_long != []:
    #     m2 = np.mean(data_long)
    #     if (m2 >= 3) and (m2 <= 10):  # Light wind
    #         val2 = 60  # Augment duration by 60 seconds
    #     elif m2 > 10:  # Strong wind
    #         val2 = 120  # Augment duration by 120 seconds
    #     else:  # No wind
    #         val2 = 0  # No modification
    #
    # # In real time.
    # if data_short != []:
    #     m1 = np.mean(data_short)
    #     if (m1 >= 3) and (m1 <= 10):  # Light wind
    #         val1 = 90  # Augment duration by 90 seconds
    #     elif m1 > 10:  # Strong wind
    #         val1 = 150  # Augment duration by 150 seconds
    #     else:  # No wind
    #         val1 = 0  # No modification
    #
    # return val1 + val2


def get_result(plantID, devID):
    """Get the last entries on wind field and decides if it is necessary or not
    to irrigate.
    """

    plantID = plantID
    devID = devID
    resource = "wind"
    time1 = "minutes"
    time2 = "hours"
    tval1 = str(10)
    tval2 = str(12)
    url, port = read_file(FILE)
    data_long = []
    data_short = []

    string1 = (url + ":" + port + "/data/" + plantID + "/" + resource + "?time="
              + time1 + "&tval=" + tval1 + "&plantID=" + plantID + "&devID=" +
              devID)

    string2 = (url + ":" + port + "/data/" + plantID + "/" + resource + "?time="
              + time2 + "&tval=" + tval2 + "&plantID=" + plantID + "&devID=" +
              devID)

    #"http://127.0.0.1:8081/data/p_1002/wind?time=minutes&tval=10&plantID=p_1002&devID=d_1002"
    #"http://127.0.0.1:8081/data/p_1002/wind?time=hours&tval=12&plantID=p_1002&devID=d_1002"

    data_short = json.loads(requests.get(string1).text)
    data_short = data_short["data"]

    data_long = json.loads(requests.get(string2).text)
    data_long = data_long["data"]

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

    return val1 + val2




def main():
    print(get_result("p_1001","d_1002"))  # Example.


if __name__ == '__main__':
    main()
