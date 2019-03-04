#!/usr/bin/env python3

import sys
import Adafruit_DHT

SENSOR = 11
PIN = 17

def dht11():
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN, retries=3, delay_seconds=2)

        if humidity == None:
            humidity = -1

        if temperature == None:
            temperature = -1

        return (humidity, temperature)



