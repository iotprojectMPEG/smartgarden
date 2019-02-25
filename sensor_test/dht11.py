#!/usr/bin/python

import sys
import Adafruit_DHT
import time

SENSOR = 11
PIN = 17

def main():
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)
        print 'Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity)
        time.sleep(10)

if __name__ == '__main__':
    main()
