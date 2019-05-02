# Sono necessari i seguenti componenti (edo_fax li ha):
# 1. Photoresistor module
# 2. Un Analog to Digital Converter PCF 8591 (e installare la libreria)

#Istruzioni montaggio figura "light.jpg"
###################
# Light Intensity #
###################
import PCF8591 as ADC
import RPi.GPIO as GPIO
import time

DO = 17
GPIO.setmode(GPIO.BCM)

def setup():
    ADC.setup(0x48)
    GPIO.setup(DO, GPIO.IN)

def get_data():
    value = ADC.read(0)
    return value

if __name__ == '__main__':
    setup()
    value=get_data()
    print 'Value: ', value
