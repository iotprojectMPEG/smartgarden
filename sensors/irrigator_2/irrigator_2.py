#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start irrigators.
"""

import json
import requests
import threading
import paho.mqtt.client as PahoMQTT
import time
import schedule

import os, sys, inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import updater

FILENAME = "conf.json"
BT = None


def irrigate(id, time=300):
    """Dummy function which simulates irrigation hardware."""
    print("Starting irrigation on %s for %s seconds" % (id, time))


class PublisherSubscriber:
    """Receives irrigation commands and publish irrigation values."""
    def __init__(self, clientID, topic, serverIP, port, devID):
        self.clientID = clientID
        self.devID = devID
        self.topic = topic
        self.messageBroker = serverIP
        self.port = int(port)
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received
        self.loop_flag = 1

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)
        print("Subscribed to %s" % self.topic)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        print ("PS - Connected to %s - Result code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        """When a message is received, it takes the duration and calls the
        publishing function. Alive messages are ignored.
        """
        msg.payload = msg.payload.decode("utf-8")
        message = json.loads(msg.payload)
        dev = self.devID
        for e in message["e"]:
            if e["n"] == 'alive':
                # print("Alive message")
                pass
            else:
                try:
                    duration = e["d"]
                    irrigate(dev, duration)
                    self.my_publish(duration, 1)
                except:
                    pass

    def my_publish(self, duration, bool):
        """Create a json which is then published via MQTT.
        This will be collected by thingspeak.py and published on ThingSpeak
        """
        timestamp = round(time.time()) - BT
        message = {
        "bn": self.devID,
        "bt": BT,
        "e":
           [{"n": "irrigation",
            "u": "boolean",
            "t": timestamp,
            "v": duration
            }]
        }
        self._paho_mqtt.publish(self.topic, json.dumps(message), 2)
        print(json.dumps(message, indent=2), "published on %s" % self.topic)


class PubData(threading.Thread):
    """Main thread for MQTT publisher and subscriber."""
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.devID, self.url, self.port) = updater.read_file(FILENAME)
        print(">>> Irrigator %s <<<\n" %(self.devID))
        (self.gardenID, self.plantID,
                        self.resources) = updater.find_me(self.devID,
                        self.url, self.port)
        (self.broker_ip, mqtt_port) = updater.broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

        self.topic = []
        self.topic.append('smartgarden/' + self.gardenID + '/'
                          + self.plantID + '/' + self.devID)

    def run(self):
        print("Topics:", self.topic)
        pubsub = PublisherSubscriber(self.devID + '_1', self.topic[0], self.broker_ip,
                          int(self.mqtt_port), self.devID)
        pubsub.start()
        while pubsub.loop_flag:
            print("Waiting for connection...")
            time.sleep(1)

        while True:
            time.sleep(1)

        pubsub.stop()


def main():
    global BT
    BT = round(time.time())

    thread1 = updater.Alive(1, "Alive")
    thread2 = PubData(2, "PubData")

    thread1.start()
    time.sleep(1)
    thread2.start()


if __name__ == '__main__':
    main()