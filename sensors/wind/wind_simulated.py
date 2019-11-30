#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wind intensity sensor (simulated)."""

import json
import threading
import paho.mqtt.client as PahoMQTT
import os
import sys
import inspect
import time
import numpy as np


current_dir = os.path.dirname(os.path.abspath(
                              inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import updater

INTENSITY = [(0, 10), (11, 33), (34, 64)]  # Knots.
FILENAME = "conf.json"
BT = None
PREVIOUS_VALUE = 5  # To prevent wind changing drastically from previous value.


class MyPublisher(object):
    """MQTT publisher."""

    def __init__(self, clientID, topic, serverIP, port):
        """Initialise MQTT publisher."""
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
    """Publish sensor data with MQTT every minute."""

    def __init__(self, ThreadID, name):
        """Initialise thread with MQTT data."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.devID, self.url, self.port) = updater.read_file(FILENAME)
        print(">>> Wind %s <<<\n" % self.devID)
        (self.gardenID, self.plantID,
         self.resources) = updater.find_me(self.devID,
                                           self.url, self.port)
        (self.broker_ip, mqtt_port) = updater.broker_info(self.url, self.port)
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
    """Get wind data from sensor."""
    with open("wind_demo.txt", "r") as f:
        lines = f.readlines()
    f.close()
    with open("wind_demo.txt", "w") as f:
        for i in range(len(lines)):
            if i == 0:
                row = lines[0].split(',')
                value = float(row[0])

            else:
                row = lines[i].split(',')[0]
                f.write("%s,\n" % row)
    f.close()
    try:
        intensity = np.random.choice([0, 1, 2], p=[0.6, 0.38, 0.02])
        minimum = INTENSITY[intensity][0]
        maximum = INTENSITY[intensity][1]
        value = np.random.randint(minimum, maximum+1)

        # Maximum range of change: 5
        global PREVIOUS_VALUE
        if (value > PREVIOUS_VALUE + 5):
            value = PREVIOUS_VALUE + 5

        elif (value < PREVIOUS_VALUE - 5):
            value = PREVIOUS_VALUE - 5

        PREVIOUS_VALUE = value

    except Exception:
        pass

    timestamp = round(time.time()) - BT
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
    """Start all threads."""
    global BT
    BT = round(time.time())

    # Try to connect to catalog by starting Alive process.
    connected = 0
    while connected == 0:
        try:
            thread1 = updater.Alive(1, "Alive")
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
