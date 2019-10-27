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


def read_file(filename):
    """Read json file to get catalogURL, port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = "http://" + data["URL"]
        port = data["thing_port"]
        return (url, port)


def get_result(plantID, devID, env):
    """Get the last entries on humidity field and decides if it is necessary or
    not to modify duration of irrigation.
    """

    resource = "humidity"
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

        diff = env["humidity"] - m
        v = 100 * np.arctan(0.05 * diff)  # Add 300 seconds.
        return v

    else:
        return None


def main():
    # Examples.
    env = {"humidity": 10}
    print("Ex.1: add ", get_result("p_1002","d_1004",env), "seconds")
    env = {"humidity": 30}
    print("Ex.2: add ", get_result("p_1002","d_1004",env), "seconds")
    env = {"humidity": 70}
    print("Ex.3: add ", get_result("p_1002","d_1004",env), "seconds")
    env = {"humidity": 90}
    print("Ex.4: add ", get_result("p_1002","d_1004",env), "seconds")

if __name__ == '__main__':
    main()
