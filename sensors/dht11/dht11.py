#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real humidity and temperature sensor.
"""

import json
import time
import sys
import threading
from .. import updater

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
    thread1 = updater.Alive(1, "Alive")
    thread2 = updater.When(2, "When")

    thread1.start()
    time.sleep(1)
    thread2.start()

if __name__ == '__main__':
    main()
