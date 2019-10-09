#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ThingSpeak adaptor.
It collects SenML-formatted json files from sensors via MQTT and publish them
on ThingSpeak every 15 seconds.
"""
import numpy as np
import json
import paho.mqtt.client as PahoMQTT
import time
import datetime
import sys,os,inspect
import threading
import requests
import cherrypy


loop_flag = 1
time_flag = 1


############################ Functions ############################
def ts_publish(list, url):
    """Take a list of jsons and publish them via REST on ThingSpeak."""
    for item in list:
        print("Publishing:")
        print(json.dumps(item))
        r = requests.post(url, data=item)


def read_file(filename):
    """Read json file to get devID, catalogURL and port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["catalogURL"]
        topic = data["topic"]
        port = data["port"]
        ts_url = data["thingspeakURL"]
        return (url, port, topic, ts_url)


def broker_info(url, port):
    """Send GET request to catalog in order to obrain MQTT broker info."""
    string = "http://" + url + ":" + port + "/broker"
    broker = requests.get(string)
    broker_ip = json.loads(broker.text)["IP"]
    mqtt_port = json.loads(broker.text)["mqtt_port"]
    return (broker_ip, mqtt_port)


############################ Classes ############################
class Timer(threading.Thread):
    """15-second timer. It is used to prevent publishing on ThingSpeak too
    often.
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):
        global time_flag
        while True:
            time_flag = 1  # Start timer.
            time.sleep(15)  # Wait 15 seconds.
            time_flag = 0  # Stop timer.
            time.sleep(1)  # 1-sec cooldown.


class Database(object):
    """Manage a database with info collected from sensors which have to be
    published later on ThingSpeak.
    """
    def __init__(self):
        self.list_ID = []
        self.list_data = []

        # Current time in ISO 8601
        now = time.time()
        self.created_at = datetime.datetime.utcfromtimestamp(now).isoformat()

    def create(self, plantID, api_key):
        """Check if there is an entry corresponding to the plantID, if not
        create a new entry with the new writeAPI.
        """
        if plantID in self.list_ID:
            pass  # The plantID is already in the database.

        else:
            # Create a new entry with the current plantID and writeAPI.
            self.list_data.append(self.create_new(api_key))
            self.list_ID.append(plantID)

    def create_new(self, api_key):
        """Create a new json with writeAPI and timestamp (ISO 8601)."""
        data = {
            "api_key": api_key,
            "created_at": self.created_at,
        }
        return data

    def update_data(self, api_key, fieldID, value):
        """Append or update field and value to the current json."""
        print("Collected: field%s=%s (%s)" %(str(fieldID), value, api_key))
        up = {
                "field" + str(fieldID): value,
             }

        cnt = 0

        for data in self.list_data:
            if data["api_key"] == api_key:
                self.list_data[cnt].update(up)
            cnt += 1

    def reset(self):
        """Reset lists and time."""
        self.list_ID = []
        self.list_data = []
        now = time.time()
        self.created_at = datetime.datetime.utcfromtimestamp(now).isoformat()


class MySubscriber(object):
    def __init__(self, clientID, topic, serverIP):
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received
        self.db = Database()

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        global loop_flag
        print ("S - Connected to %s - Result code: %d" % (self.messageBroker, rc))
        loop_flag = 0


    def send_data(self):
        """Takes data from database, empties the database, returns data."""
        data = self.db.list_data
        self.db.reset()
        return data

    def my_on_message_received(self, client, userdata, msg):
        # try:
        # Read conf.json file
        (self.url, self.port, self.topic, self.ts_url) = read_file("conf.json")

        # Decode received message and find devID
        msg.payload = msg.payload.decode("utf-8")
        message = json.loads(msg.payload)
        devID = message['bn']

        # Ask catalog for plantID from devID
        string = "http://" + self.url + ":" + self.port + "/info/" + devID
        info_d = json.loads(requests.get(string).text)
        plantID = info_d["plantID"]

        # Ask catalog the thingspeakID for that specific plantID.
        string = "http://" + self.url + ":" + self.port + "/info/" + plantID
        info = json.loads(requests.get(string).text)
        thingspeakID = info['thingspeakID']

        # Ask catalog the APIs for that ThingSpeak ID.
        string = ("http://" + self.url + ":" + self.port +
                   "/api/tschannel/" + str(thingspeakID))
        info = json.loads(requests.get(string).text)
        write_API = info["writeAPI"]

        # Update values in the database.
        self.db.create(plantID, str(write_API))
        for item in message["e"]:
            if item["n"] == 'alive':
                pass
            else:
                topic = item["n"]
                for item2 in info_d["resources"]:
                    if item2["n"] == topic:
                        feed = item2["f"]

                value = item["v"]
                self.db.update_data(str(write_API), feed, value)

        # except:
        #     print("Invalid message type")
        #     pass


############################ Threads ############################
class SubmitData(threading.Thread):
    """Main thread which calls MQTT subscriber, database and publishing classes
    and functions.
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.url, self.port, self.topic, self.ts_url) = read_file("conf.json")
        (self.broker_ip, mqtt_port) = broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

    def run(self):
        global time_flag

        # Start subscriber.
        sub = MySubscriber("Thingspeak", self.topic, self.broker_ip)
        sub.start()

        while True:

            while time_flag == 0:
                time.sleep(.1)

            # Connection callback.
            while loop_flag:
                print("Waiting for connection...")
                time.sleep(.01)

            # Collecting data for 15 seconds. When time is expired, time_flag
            # becomes equal to 0.
            while time_flag == 1:
                time.sleep(.1)

            # Publish json data in different channels.
            ts_publish(sub.send_data(), self.ts_url)


# class CherryThread(threading.Thread):
#     def __init__(self, ThreadID, name):
#         threading.Thread.__init__(self)
#         self.ThreadID = ThreadID
#         self.name = name
#         (self.url, self.port, self.topic, self.ts_url) = read_file("conf.json")
#         (self.broker_ip, mqtt_port) = broker_info(self.url, self.port)
#         self.mqtt_port = int(mqtt_port)
#
#     def run(self):
#         try:
#             cherrypy.tree.mount(WebServer(), '/', config=CHERRY_CONF)
#             cherrypy.config.update(CHERRY_CONF)
#             cherrypy.engine.start()
#             cherrypy.engine.block()
#         except KeyboardInterrupt:
#             print ("Stopping the engine")
#             return
#
# class WebServer():
#     """CherryPy webserver."""
#     exposed = True
#
#     @cherrypy.tools.json_out()
#     def GET(self, *uri, **params):
#
#         catalog = Catalog(JSON_STATIC, JSON_DYNAMIC)
#         catalog.load_file()
#
#         if uri[0] == 'data':
#             uri[1] == plantID
#             uri[2] == resource
#             time = param["time"]
#             time_value = param["tval"]
#             plantID = param["plantID"]
#
#     string2 = ("https://api.thingspeak.com/channels/" + channelID + "/fields/" +
#               fieldID + ".json?api_key=" + readAPI + "&hours=" + hours)

if __name__ == "__main__":
    thread1 = SubmitData(1, "SubmitData")
    thread1.start()
    thread2 = Timer(2, "Timer")
    thread2.start()
    # thread3 = CherryThread(3, "CherryServer")
    # thread3.start()
