#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simulated humidity and temperature sensor."""
import json
import time
import paho.mqtt.client as PahoMQTT
import threading
import sys
import datetime
import random
from pathlib import Path
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_dir))
import sensor_functions as sf

P = Path(__file__).parent.absolute()
CONF_FILE = P / 'conf.json'
SENSOR = 11
PIN = 17
BT = None  # Basetime


def get_data(devID, res):
    """Get humidity and temperature from sensor. Return data."""
    # Initialization.
    now = datetime.datetime.now()
    line_number = now.hour*60 + now.minute

    with open(P / "hum_demo.txt", "r") as f:
        lines = f.readlines()
    f.close()
    humidity = int(lines[line_number].replace('\n', ''))

    with open(P / "temp_demo.txt", "r") as f:
        lines = f.readlines()
    f.close()
    temperature = int(lines[line_number].replace('\n', ''))

    temperature += random.randint(-1, 1)
    if temperature <= 0:
        temperature = 1
    humidity += random.randint(-1, 1)
    if humidity <= 0:
        humidity = 1

    timestamp = round(time.time()) - BT
    data = {
        "bn": devID,
        "bt": BT,
        "e":
            [{"n": res[0]["n"],
              "u": res[0]["u"],
              "t": timestamp,
              "v": humidity
              },
             {
              "n": res[1]["n"],
              "u": res[1]["u"],
              "t": timestamp,
              "v": temperature
              }]
             }

    return data


class PubData(threading.Thread):
    """Publish sensor data with MQTT every minute."""

    def __init__(self, ThreadID, name):
        """Initialise thread with MQTT data."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.devID, self.url, self.port) = sf.read_file(CONF_FILE)
        (self.gardenID, self.plantID,
         self.resources) = sf.find_me(self.devID, self.url, self.port)
        (self.broker_ip, mqtt_port) = sf.broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

        self.topic = []
        self.topic.append('smartgarden/' + self.gardenID + '/' +
                          self.plantID + '/' + self.devID)

    def run(self):
        """Run thread."""
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


class MyPublisher(object):
    """MQTT publisher."""

    def __init__(self, clientID, topic, serverIP, port):
        """Initialise MQTT client."""
        self.clientID = clientID + '_pub'
        self.devID = clientID
        self.topic = topic
        self.port = port
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self.loop_flag = 1

    def start(self):
        """Start publisher."""
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        """Stop subscriber."""
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        """Define custom on_connect function."""
        print("Connected to %s - Res code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_publish(self, message):
        """Define custom publish function."""
        print("Publishing on %s:" % self.topic)
        print(json.dumps(json.loads(message), indent=2))
        self._paho_mqtt.publish(self.topic, message, 2)


def main():
    """Start all threads."""
    global BT
    BT = round(time.time())

    # Try to connect to catalog by starting Alive process.
    connected = 0
    while connected == 0:
        try:
            thread1 = sf.Alive(1, "Alive", CONF_FILE)
            connected = 1  # Catalog is available
        except Exception:
            print("Catalog is not reachable... retry in 5 seconds")
            time.sleep(5)

    thread2 = PubData(2, "PubData")

    # Start threads.
    thread1.start()
    time.sleep(1)
    thread2.start()


if __name__ == '__main__':
    main()
