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


def read_file(filename):
    """Read json file to get catalogURL, port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = "http://" + data["URL"]
        port = data["thing_port"]
        return (url, port)


def get_result(plantID, devID):
    """Get the last entries on rain field and decides if it is necessary or not
    to irrigate.
    """

    resource = "rain"
    time = "hours"
    tval = str(2)
    url, port = read_file(FILE)
    string = (url + ":" + port + "/data/" + plantID + "/" + resource + "?time="
              + time + "&tval=" + tval + "&plantID=" + plantID + "&devID=" +
              devID)

    data = json.loads(requests.get(string).text)
    data = data["data"]
    if data != []:
        m = np.mean(data)
        if m >= 0.6:  # Rain for at least 60% of the time
            return -1  # Do not irrigate

        elif (m >= 0.4) and (m < 0.6):  # Rain from 40-60% of the time
            return -120  # Remove 120 seconds

        else:  # Almost no rain
            return 0  # No modifications


def main():
    print("Ex.1: add", get_result("p_1002", "d_1006"), "seconds")  # Example.


if __name__ == '__main__':
    main()
