#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import json
import paho.mqtt.client as PahoMQTT
import time
import datetime
import sys,os,inspect
import threading
import requests


loop_flag = 1
time_flag = 1

class TheThread(threading.Thread):
    """Timer
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):


        # thepub = TSPublisher()

        global time_flag
        while True:
            time_flag = 1
            # print("ThingSpeak not available")
            time.sleep(15)
            time_flag = 0
            time.sleep(1)
            # print("ThingSpeak is available again")


# class TheTest(threading.Thread):
#     """Complex thing
#     """
#     def __init__(self, ThreadID, name):
#         threading.Thread.__init__(self)
#         self.ThreadID = ThreadID
#         self.name = self.name
#
#     def run(self):
#         while True:
#             global time_flag
#
#             while time_flag == 0:
#                 time.sleep(.1)
#
#             while time_flag == 1:
#                 print("Raccolgo dati...")
#
#
#
#
#
#                 time.sleep(.1)
#
#             print("Pubblico i dati...")


class TSPublisher:
    def __init__(self):
        self.list_pub = []

    def get_data(self, data_list):
        self.list_pub.extend(data_list)

    def publish_data(self):
        for item in self.list_pub:
            print("Publishing:")
            print(json.dumps(item))
            r = requests.post('https://api.thingspeak.com/update.json',
                              data=item)

        self.list_pub = []


class TheClass:
    def __init__(self):
        self.list_ID = []
        self.list_data = []

        # Current time in ISO 8601
        now = time.time()
        self.created_at = datetime.datetime.utcfromtimestamp(now).isoformat()

    def create(self, plantID, api_key):
        # print("Checking %s and %s" %(plantID, api_key))
        if plantID in self.list_ID:
            pass

        else:
            # print("Creating!")
            # print(api_key)
            self.list_data.append(self.create_new(api_key))
            self.list_ID.append(plantID)

            # print(self.list_data)

    def create_new(self, api_key):
        data = {
            "api_key": api_key,
            "created_at": self.created_at,
        }
        return data

    def update_data(self, api_key, fieldID, value):
        print("Collected: field%s=%s (%s)" %(str(fieldID), value, api_key))
        up = {
                "field"+str(fieldID): value,
             }

        cnt = 0

        for data in self.list_data:
            if data["api_key"] == api_key:
                self.list_data[cnt].update(up)
            cnt += 1

    def export(self):
        data = self.list_data
        return data

    def clear(self):
        self.list_ID = []
        self.list_data = []
        self.time = datetime.datetime.now().isoformat()

def read_file(filename):
    """Read json file to get devID, catalogURL and port.
    """
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["catalogURL"]
        topic = data["topic"]
        port = data["port"]
        return (url, port, topic)

def broker_info(url, port):
    """Send GET request to catalog in order to obrain MQTT broker info.
    """
    string = "http://"+ url + ":" + port + "/broker"
    broker = requests.get(string)
    broker_ip = json.loads(broker.text)["IP"]
    mqtt_port = json.loads(broker.text)["mqtt_port"]
    return (broker_ip, mqtt_port)

class MySubscriber:
    def __init__(self, clientID, topic, serverIP):
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received

        self.classer = TheClass()

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)


        # Update data
        # GET request with body


        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        global loop_flag
        print ("S - Connected to %s - Result code: %d" % (self.messageBroker, rc))
        loop_flag = 0


    def send_data(self):
        data = self.classer.export()
        self.classer.clear()
        return data

    def my_on_message_received(self, client, userdata, msg):
        try:
            # Read conf.json file
            (self.url, self.port, self.topic) = read_file("conf.json")

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

            self.classer.create(plantID, str(write_API))
            for item in message["e"]:
                if item["n"] == 'alive':
                    pass
                else:
                    topic = item["n"]
                    for item2 in info_d["resources"]:
                        if item2["n"] == topic:
                            feed = item2["f"]

                    value = item["v"]
                    self.classer.update_data(str(write_API), feed, value)

            # Convert UNIX timestamp to ISO 8601
            # for item in message["e"]:
            #     creation_time = message["bt"] + item["t"]
            #
            # creation_time = datetime.datetime.utcfromtimestamp(creation_time).isoformat()
            # req_tt = ('https://api.thingspeak.com/update?api_key=' +
            #           write_API + '&created_at=' + str(creation_time))

            # for item in message["e"]:
            #     if item["n"] == 'alive':
            #         pass  # Ignoring alive messages.
            #     else:
            #         topic = item["n"]
            #         for item2 in info_d["resources"]:
            #             if item2["n"] == topic:
            #                 feed = item2["f"]
            #
            #         req_tt += ('&field' + str(feed) + '=' + str(item['v']))
            #
            # request = requests.get(req_tt)
            # print("UPDATING: %s" % req_tt)

        except:
            pass


class SubData(threading.Thread):
    """Publish sensor data with MQTT every minute.
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.url, self.port, self.topic) = read_file("conf.json")
        (self.broker_ip, mqtt_port) = broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)


    def run(self):
        global time_flag

        # Start subscriber.
        sub = MySubscriber("Thingspeak", self.topic, self.broker_ip)
        sub.start()

        # Start REST ThingSpeak publisher.
        p = TSPublisher()

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
            p.get_data(sub.send_data())
            p.publish_data()



if __name__ == "__main__":
    thread1 = SubData(1, "SubData")
    thread1.start()
    thread2 = TheThread(2, "Timer")
    thread2.start()
    # thread3 = TheTest(3, "Test")
    # thread3.start()
