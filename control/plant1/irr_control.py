#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Irrigation control strategy.

This script check all parameters stored in dynamic catalog and publish MQTT
messages to start irrigations with specific delays and durations, depending
on such parameters. Those parameters are then reset for next irrigations.
"""
import json
import requests
import time
import threading
import functions
import paho.mqtt.client as PahoMQTT
from pathlib import Path

P = Path(__file__).parent.absolute()
FILE = P / "irr.json"
TIME_LIST = []


class SchedulingThread(threading.Thread):
    """Scheduling thread to call strategy."""

    def __init__(self, ThreadID, name):
        """Initialise thread."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name

    def run(self):
        """Run thread.

        Check if current hour correspond to one entry in the timetable, if so
        call the strategy and remove the current hour from the timetable.
        """
        global TIME_LIST

        url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
        string2 = "http://" + url + ":" + port + "/broker"
        broker_info = json.loads(requests.get(string2).text)
        broker_ip = broker_info["IP"]
        mqtt_port = broker_info["mqtt_port"]

        act = Actuator('my_ID', broker_ip, mqtt_port)
        while True:
            for e in TIME_LIST:
                if e["schedule_time"] == time.strftime("%H:%M"):
                    act.irr(e["plantID"], e["hour"], e["devID"], url, port)
                    TIME_LIST.remove(e)
            time.sleep(10)


class Actuator(object):
    """This class performs actual irrigations by sending MQTT messages.

    Read irrigations information on dynamic catalog and send MQTT
    messages in order to start irrigation.
    If an irrigation has to be postponed, it calls a scheduler which has a
    there that has a countdown.
    """

    def __init__(self, ID, IP, mqtt_port):
        """Initialise thread."""
        self.pub = MyPublisher(ID, IP, mqtt_port)
        self.pub.start()

    def publish(self, duration, topic):
        """Publish MQTT messages."""
        message = {
                   "e": [{
                            "n": "irrigate",
                            "d": duration
                        }]
                   }

        if duration > 0:
            self.pub.my_publish(json.dumps(message), topic)
        else:
            print("No irrigation due to rainy day.")

    def irr(self, plantID, hour, devID, url, port):
        """Compute irrigation  delay and duration.

        It checks the irrigation parameters stored in dynamic catalog and then
        computer total irrigation delay and duration. Then it calls other
        functions to publish immediately or after a delay the MQTT message
        which actually starts irrigation.
        """
        # Get dynamic catalog.
        string = "http://" + url + ":" + port + "/dynamic"
        data = json.loads(requests.get(string).text)

        # Get device topic.
        string_dev = "http://" + url + ":" + port + "/info/" + devID
        data_dev = json.loads(requests.get(string_dev).text)
        topic = data_dev["topic"]

        # Find hour modifications.
        for g in data["gardens"]:
            for p in g["plants"]:
                if p["plantID"] == plantID:
                    for h in p["hours"]:
                        if h["time"] == hour:
                            duration = h["duration"]
                            delay = h["delay"]
                            break

        string = "http://" + url + ":" + port + "/info/" + plantID
        data = json.loads(requests.get(string).text)
        water = data["environment"]["water"]
        duration = duration + water
        # Reset data about duration and delay on catalog. Next day it will be
        # generated again.
        functions.reset_mod(plantID, h, url, port)

        # If there is no delay: publish via MQTT irrigation and duration.
        if delay == 0:
            if topic is not None:
                self.publish(duration, topic)

        # If the irrigation has to be anticipated do the same as before but
        # write on catalog that the next day it has to be anticipated.
        elif delay < 0:
            if topic is not None:
                self.publish(duration, topic)

            new_h = functions.delay_h(h, delay)
            functions.post_delay(plantID, h, new_h, url, port)

        # If there is a delay: start thread with a countdown and then publish.
        elif delay > 0:
            delayed_irrigation = DelayedIrrigation(devID.replace('d_', ''),
                                                   devID + "_sch",
                                                   delay, self.pub, duration,
                                                   topic)
            delayed_irrigation.start()


class DelayedIrrigation(threading.Thread):
    """Thread to schedule posticipated irrigations.

    It starts a timer in this separate thread. When the timer ends it sends
    MQTT message to activate the irrigation.
    """

    def __init__(self, ThreadID, name, delay, pub, mod, topic):
        """Initialise thread."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name
        self.delay = delay
        self.publisher = pub
        self.mod = mod
        self.topic = topic
        self.pub = pub

    def run(self):
        """Run thread."""
        print("Thread status: Waiting %d seconds" % self.delay)
        time.sleep(self.delay)
        self.publish(self.mod, self.topic)

    def publish(self, duration, topic):
        """Publish MQTT message to start the (delayed) irrigation."""
        message = {
                   "e": [{
                     "n": "irrigate", "d": duration
                        }]
                   }

        if duration > 0:
            self.pub.my_publish(json.dumps(message), topic)
        else:
            print("No irrigation due to rainy day.")


class MyPublisher(object):
    """MQTT publisher."""

    def __init__(self, clientID, serverIP, port):
        """Initialise MQTT client."""
        self.clientID = clientID + '_pub'
        self.devID = clientID
        self.port = int(port)
        self.messageBroker = serverIP
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
        print("P - Connected to %s - Res code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_publish(self, message, topic):
        """Define custom publish function."""
        self._paho_mqtt.publish(topic, message, 2)
        print("Publishing on %s:" % topic)
        print(json.dumps(json.loads(message), indent=2))


def main():
    """Start all threads."""
    url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
    thread1 = SchedulingThread(1, "thread1")
    thread1.start()

    while True:
        url, port, plantID, devID, ts_url, ts_port = functions.read_file(FILE)
        string = ("http://" + url + ":" + port + "/info/" + plantID)
        data = json.loads(requests.get(string).text)
        hours = data["hours"]

        global TIME_LIST
        for h in hours:
            t = h["time"]
            s_t = h["time"]
            entry = {
                "hour": t,
                "schedule_time": s_t,
                "plantID": plantID,
                "devID": devID
            }
            TIME_LIST.append(entry)
            print("Schedule: %s - %s" % (t, plantID))

        time.sleep(86400)
        TIME_LIST = []


if __name__ == '__main__':
    main()
