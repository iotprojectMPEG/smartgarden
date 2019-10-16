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

def get_result(plantID, devID):
    """Get the last entries on humidity field and decides if it is necessary or
    not to modify duration of irrigation.
    """

    resource = "temperature"
    time = "days"
    tval = str(3)
    url, port = read_file(FILE)
    string = (url + ":" + port + "/data/" + plantID + "/" + resource + "?time="
              + time + "&tval=" + tval + "&plantID=" + plantID + "&devID=" +
              devID)

    data = json.loads(requests.get(string).text)
    data = data["data"]
    if data != []:
        m = np.mean(data)
        v = 80 * np.arctan(0.05 * m)
        return v

    else:
        return None

def main():
    print(get_result("p_1001", "d_1001"))  # Example.

if __name__ == '__main__':
    main()
