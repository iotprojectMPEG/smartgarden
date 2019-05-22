#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real humidity and temperature sensor.
"""

import json
import sys
try:
    import Adafruit_DHT
except:
    pass

SENSOR = 11
PIN = 17


def get_data():

    # Initialization.
    humidity = -1
    temperature = -1

    # Read data from sensor
    try:
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN,
                                                        retries=3,
                                                        delay_seconds=2)
    except:
        pass

    data = {
      "data": [{
        "res": "humidity",
        "value": humidity
      }, {
        "res": "temperature",
        "value": temperature
      }]
    }

    return data


def main():
    data = get_data()
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
