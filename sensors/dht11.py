#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real humidity and temperature sensor.
"""

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

    return (humidity, temperature)


def main():
    hum, temp = get_data()
    print('Temp: %.1f  Humidity: %.1f' %(temp, hum))


if __name__ == '__main__':
    main()
