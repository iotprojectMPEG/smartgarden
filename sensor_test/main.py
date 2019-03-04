#!/usr/bin/env python3

from dht11 import dht11
import time

def main():
    while True:
        humidity, temperature = dht11()
        print('Temp: %.1f  Humidity: %.1f' %(temperature, humidity))
        time.sleep(10)

if __name__ == '__main__':
    main()
