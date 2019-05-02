#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dht11
import wind
import time

import json
import requests
import threading

def read_all():
    while True:
        # DHT11 (real)
        humidity, temperature = dht11.get_data()
        print('Temp: %.1f  Humidity: %.1f' %(temperature, humidity))

        # Wind (simulated)
        intensity = wind.get_data()
        print('Wind: %d N' %(intensity))

        # Light (real)


        # Rain (real)



        time.sleep(10)


def main():
    # Read conf file
    with open("conf.json") as f:
        conf = json.loads(f.read())

    read_all()


if __name__ == '__main__':
    main()
