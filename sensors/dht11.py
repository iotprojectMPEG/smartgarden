#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real humidity and temperature sensor.
"""

import sys
import Adafruit_DHT

SENSOR = 11
PIN = 17


def get_data():
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN,
                                                    retries=3,
                                                    delay_seconds=2)

    if humidity == None:
        humidity = -1

    if temperature == None:
        temperature = -1

    return (humidity, temperature)


def main():
    hum, temp = get_data()
    print('Temp: %.1f  Humidity: %.1f' %(temp, hum))


if __name__ == '__main__':
    main()
