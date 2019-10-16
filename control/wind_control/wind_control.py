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


def read_file(filename):
    """Read json file to get catalogURL, port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = "http://" + data["URL"]
        port = data["thing_port"]
        return (url, port)


def get_result(plantID, devID):
    """Get the last entries on humidity field and decides if it is necessary or
    not to modify duration of irrigation.
    """

    resource = "wind"
    time1 = "minutes"
    time2 = "minutes"  # "hours" is not allowed
    tval1 = str(10)
    tval2 = str(12*60)  # 12 hours * 60 (in minutes)
    url, port = read_file(FILE)
    data_long = []
    data_short = []

    string1 = (url + ":" + port + "/data/" + plantID + "/" + resource + "?time="
              + time1 + "&tval=" + tval1 + "&plantID=" + plantID + "&devID=" +
              devID)

    string2 = (url + ":" + port + "/data/" + plantID + "/" + resource + "?time="
              + time2 + "&tval=" + tval2 + "&plantID=" + plantID + "&devID=" +
              devID)


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
    print("Ex: add", get_result("p_1001","d_1002"), "seconds")  # Example.


if __name__ == '__main__':
    main()
