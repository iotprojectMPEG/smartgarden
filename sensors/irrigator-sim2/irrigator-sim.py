#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simulated irrigator device."""

import json
import threading
import paho.mqtt.client as PahoMQTT
import time
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_dir))
import sensor_functions as sf

P = Path(__file__).parent.absolute()
CONF_FILE = P / "conf.json"
BT = None


def irrigate(id, time=300):
    """Simulate irrigation hardware."""
    print("Starting irrigation on %s for %s seconds" % (id, time))


class PublisherSubscriber:
    """Receive irrigation commands and publish irrigation values."""

    def __init__(self, clientID, topic, serverIP, port, devID):
        """Initialise MQTT client."""
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
        """Start MQTT client."""
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)
        print("Subscribed to %s" % self.topic)

    def stop(self):
        """Stop MQTT client."""
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        """Define custom on_connect function."""
        print("PS - Connected to %s - Result code: %d" % (self.messageBroker,
                                                          rc))
        self.loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        """Define custom on_message function.

        When a message is received, it takes the duration and calls the
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
                except Exception:
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
        """Initialise thread with MQTT data."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.devID, self.url, self.port) = sf.read_file(CONF_FILE)
        print(">>> Irrigator %s <<<\n" % self.devID)
        (self.gardenID, self.plantID, self.resources) = sf.find_me(
                                            self.devID, self.url, self.port)
        (self.broker_ip, mqtt_port) = sf.broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

        self.topic = []
        self.topic.append('smartgarden/' + self.gardenID + '/'
                          + self.plantID + '/' + self.devID)

    def run(self):
        """Run thread."""
        print("Topics:", self.topic)
        pubsub = PublisherSubscriber(self.devID + '_1', self.topic[0],
                                     self.broker_ip, int(self.mqtt_port),
                                     self.devID)
        pubsub.start()
        while pubsub.loop_flag:
            print("Waiting for connection...")
            time.sleep(1)

        while True:
            time.sleep(1)

        pubsub.stop()


def main():
    """Run all threads."""
    global BT
    BT = round(time.time())

    thread1 = sf.Alive(1, "Alive", CONF_FILE)
    thread2 = PubData(2, "PubData")

    thread1.start()
    time.sleep(1)
    thread2.start()


if __name__ == '__main__':
    main()
