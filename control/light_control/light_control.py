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


def read_file(filename):
    """Read json file to get catalogURL, port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = "http://" + data["URL"]
        port = data["thing_port"]
        return (url, port)


def get_result(plantID, devID, type):
    """Get the last entries on humidity field and decides if it is necessary or
    not to modify the time of irrigation.
    """

    resource = "light"
    time = "minutes"  # "hours" is not allowed
    tval = str(2*60)  # 12 hours * 60 (in minutes)
    url, port = read_file(FILE)
    string = (url + ":" + port + "/data/" + plantID + "/" + resource + "?time="
              + time + "&tval=" + tval + "&plantID=" + plantID + "&devID=" +
              devID)

    data = json.loads(requests.get(string).text)
    data = data["data"]

    if data != []:
        m = np.mean(data)

    try:
        if type ==  'evening':

            if (m >= 140) and (m < 160):  # Very dark
                return -1800  # Anticipation of 30 minutes

            elif (m >= 110) and (m < 140):  # Dark
                return -900  # Anticipation of 15 minutes

            elif (m >= 90 and m < 110):  # Ideal
                return 0  # Ideal time, no delay

            elif (m >= 70 and m < 90):  # Bright
                return 1800  # Posticipation of 30 minutes

            elif (m < 70):  # Very bright
                return 3600  # Posticipation of 60 minutes


        elif type == 'morning':

            if (m >= 140) and (m < 160):  # Very dark
                return 3600  # Posticipation of 60 minutes

            elif (m >= 110) and (m < 140):  # Dark
                return 1800  # Posticipation of 30 minutes

            elif (m >= 90 and m < 110):  # Ideal
                return 0  # Ideal time, no delay

            elif (m >= 70 and m < 90):  # Bright
                return -900  # Anticipation of 15 minutes

            elif (m < 70):  # Very bright
                return -1800  # Anticipation of 30 minutes

    except:
        return 0


def main():
    print(get_result("p_1002","d_1005","morning"))  # Example.


if __name__ == '__main__':
    main()
