#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rain detection sensor.

Following components are required:
1. Rain detection module
2. Un Analog to Digital Converter PCF 8591 (with library)
3. Un modulo amplificatore LM 393

Instructions on "rain.jpg"
"""
import PCF8591 as ADC
import RPi.GPIO as GPIO
import json
import time
import threading
import paho.mqtt.client as PahoMQTT
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_dir))
import sensor_functions as sf

P = Path(__file__).parent.absolute()

TOPIC = 'smartgarden/+/+/rain'
CONF_FILE = P / "conf.json"
BT = None
DO = 27
GPIO.setmode(GPIO.BCM)


def setup():
    """Do setup GPIO pin."""
    ADC.setup(0x48)
    GPIO.setup(DO, GPIO.IN)


class MyPublisher(object):
    """MQTT Publisher."""

    def __init__(self, clientID, topic, serverIP, port):
        """Initialise MQTT client."""
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = serverIP
        self.port = port
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self.loop_flag = 1

    def start(self):
        """Start publisher."""
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        """Stop publisher."""
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        """Define custom on_connect function."""
        print("Connected to %s - Result code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_publish(self, message):
        """Define custom publish function."""
        print("Publishing on %s:" % self.topic)
        print(json.dumps(json.loads(message), indent=2))
        self._paho_mqtt.publish(self.topic, message, 2)


class PubData(threading.Thread):
    """Thread which publish MQTT data."""

    def __init__(self, ThreadID, name):
        """Initialise thread with MQTT data."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.devID, self.url, self.port) = sf.read_file(CONF_FILE)
        print(">>> Rain %s <<<\n" % (self.devID))
        (self.gardenID, self.plantID,
         self.resources) = sf.find_me(self.devID,
                                      self.url, self.port)
        (self.broker_ip, mqtt_port) = sf.broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

        self.topic = []
        self.topic.append('smartgarden/' + self.gardenID + '/' +
                          self.plantID + '/' + self.devID)

    def run(self):
        """Run thread."""
        print("Topics:", self.topic)
        pub = MyPublisher(self.devID + '_1', self.topic[0], self.broker_ip,
                          int(self.mqtt_port))
        pub.start()

        while pub.loop_flag:
            print("Waiting for connection...")
            time.sleep(1)

        while True:
            data = get_data(self.devID, self.resources)
            pub.my_publish(json.dumps(data))
            time.sleep(60)

        pub.stop()


def get_data(devID, res):
    """Get data from sensor."""
    status = GPIO.input(DO)

    timestamp = round(time.time()) - BT
    if status == 1:
        value = 0
    if status == 0:
        value = 1
    data = {
        "bn": devID,
        "bt": BT,
        "e": [{
            "n": res[0]["n"],
            "u": res[0]["u"],
            "t": timestamp,
            "v": value
        }]
    }

    return data


def main():
    """Do setup sensor and call threads."""
    global BT
    BT = round(time.time())

    setup()

    thread1 = sf.Alive(1, "Alive", CONF_FILE)
    thread2 = PubData(2, "PubData")

    thread1.start()
    time.sleep(1)
    thread2.start()


if __name__ == '__main__':
    main()
