#!/usr/bin/env python3
# Sono necessari i seguenti componenti (edo_fax li ha):
# 1. Rain detection module
# 2. Un Analog to Digital Converter PCF 8591 (e installare la libreria)
# 3. Un modulo amplificatore LM 393

#Istruzioni montaggio figura "rain.jpg"
##################
# Rain Detection #
##################

import PCF8591 as ADC
import RPi.GPIO as GPIO
import time
import math

DO = 17
GPIO.setmode(GPIO.BCM)

def setup():
    ADC.setup(0x48)
    GPIO.setup(DO, GPIO.IN)

def Print(x):
    if x == 1:
        print('Not raining')
    if x == 0:
        print('Raining')

def get_data():
    status = GPIO.input(DO)
    return status

if __name__ == '__main__':
    setup()
    status=get_data()
    Print(status)

