#!/usr/bin/env python3

"""
Use this to test all sensors.
"""

import dht11
import wind
import time


def main():
    while True:
        # DHT11 (real)
        humidity, temperature = dht11.get_data()
        print('Temp: %.1f  Humidity: %.1f' %(temperature, humidity))

        # Wind (simulated)
        wind = wind.get_data()
        print('Wind: %d N' %(wind))
        time.sleep(10)


if __name__ == '__main__':
    main()
