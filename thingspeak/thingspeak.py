#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ThingSpeak adaptor.

It collects SenML-formatted json files from sensors via MQTT and publish them
on ThingSpeak every 15 seconds.
"""
import json
import paho.mqtt.client as PahoMQTT
import time
import datetime
import threading
import requests
import cherrypy

loop_flag = 1
time_flag = 1
CHERRY_CONF = "cherrypyconf"
FILE = "conf.json"


# Functions
def ts_publish(list, url):
    """Take a list of jsons and publish them via REST on ThingSpeak."""
    for item in list:
        print("Publishing:")
        print(json.dumps(item))
        requests.post(url, data=item)


def read_file(filename):
    """Read json file to get catalogURL, port, topic and ThingSpeak URL."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["cat_ip"]
        topic = data["topic"]
        port = data["cat_port"]
        ts_url = data["thingspeakURL"]
        return (url, port, topic, ts_url)


def read_file_short(filename):
    """Read json file to get catalogURL and port."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["cat_ip"]
        port = data["cat_port"]
        return (url, port)


def broker_info(url, port):
    """Send GET request to catalog in order to obtain MQTT broker info."""
    string = "http://" + url + ":" + port + "/broker"
    broker = requests.get(string)
    broker_ip = json.loads(broker.text)["IP"]
    mqtt_port = json.loads(broker.text)["mqtt_port"]
    return (broker_ip, mqtt_port)


# Classes
class Timer(threading.Thread):
    """15-second timer.

    It is used to prevent publishing on ThingSpeak too often.
    """

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):
        """Run thread."""
        global time_flag
        while True:
            time_flag = 1  # Start timer.
            time.sleep(15)  # Wait 15 seconds.
            time_flag = 0  # Stop timer.
            time.sleep(1)  # 1-sec cooldown.


class Database(object):
    """Manage a database with data from sensors.

    Manage a database with info collected from sensors which have to be
    published later on ThingSpeak. The database is filled with data and every
    15 seconds it is emptied and these data are sent to ThingSpeak in a single
    POST. It is to prevent sending too much messages to ThingSpeak which can
    update a channel only every 15 seconds (free version).
    Data are stored in a list of jsons. Every json contains an API_key which
    refers to a specific channel, a creation time and field values of a plant.
    Example:
    [{
            "api_key": 00000,
            "created_at": 18-23-43T43..
            "field1": 50,
            "field4": 30
    }]

    """

    def __init__(self):
        """Initialise database with an empty list."""
        self.list_ID = []
        self.list_data = []

        # Current time in ISO 8601
        now = time.time()
        self.created_at = datetime.datetime.utcfromtimestamp(now).isoformat()

    def create(self, plantID, api_key):
        """Create a new entry given plantID and api_key.

        Check if there is an entry corresponding to the plantID, if not
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
        print("Collected: field%s=%s (%s)" % (str(fieldID), value, api_key))
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
    """MQTT subscriber."""

    def __init__(self, clientID, topic, serverIP):
        """Initialise MQTT client."""
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received
        self.db = Database()

    def start(self):
        """Start subscriber."""
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop(self):
        """Stop subscriber."""
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        """Define custom on_connect function."""
        global loop_flag
        print("S - Connected to %s - Result code: %d" % (self.messageBroker,
                                                         rc))
        loop_flag = 0

    def send_data(self):
        """Take data from database, empty the database, return data."""
        data = self.db.list_data
        self.db.reset()
        return data

    def my_on_message_received(self, client, userdata, msg):
        """Define custom on_message function."""
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


# Threads
class SubmitData(threading.Thread):
    """Main thread of the ThingSpeak adaptor.

    Main thread which calls MQTT subscriber, database and publishing classes
    and functions.
    Data are collected for 15 seconds and then published.
    """

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.url, self.port, self.topic, self.ts_url) = read_file("conf.json")
        (self.broker_ip, mqtt_port) = broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

    def run(self):
        """Run thread."""
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


class CherryThread(threading.Thread):
    """Thread to run CherryPy webserver."""

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.url, self.port, self.topic, self.ts_url) = read_file("conf.json")
        (self.broker_ip, mqtt_port) = broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

    def run(self):
        """Run thread."""
        try:
            cherrypy.tree.mount(WebServer(), '/', config=CHERRY_CONF)
            cherrypy.config.update(CHERRY_CONF)
            cherrypy.engine.start()
            cherrypy.engine.block()
        except KeyboardInterrupt:
            print("Stopping the engine")
            return


class WebServer():
    """CherryPy webserver.

    It works as an adaptor for strategies scripts.
    It receives GETs from control strategies and send GETs to ThingSpeak in
    order to get information and return them back to strategies.

    For example: temp. strategy asks the adaptor data about temp values of
    plant p_1001 over the last five hours. The adaptor asks ThingSpeak and
    receives the data. The adaptor sends back a json with the list of temp.
    values.
    """

    exposed = True
    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        """Define GET HTTP method for RESTful webserver."""
        if uri[0] == 'data':
            plantID = uri[1]
            resource = uri[2]
            time = params["time"]
            time_value = str(params["tval"])
            plantID = params["plantID"]
            devID = params["devID"]

        readAPI, channelID = get_api(plantID)
        fieldID = str(get_field(resource, devID))

        string2 = ("https://api.thingspeak.com/channels/" + str(channelID) +
                   "/fields/" + fieldID + ".json?api_key=" + str(readAPI) +
                   "&" + str(time) + "=" + str(time_value))
        print("\n", string2, "\n\n")
        res = json.loads(requests.get(string2).text)

        try:
            wanttime = int(params["wanttime"])
            print("OK")
        except Exception:
            wanttime = 0

        print(wanttime)
        data = []
        if wanttime == 0:
            for r in res["feeds"]:
                if r["field"+str(fieldID)] is not None:
                    data.append(float(r["field"+str(fieldID)]))
                else:
                    pass

        elif wanttime == 1:
            for r in res["feeds"]:
                if r["field"+str(fieldID)] is not None:
                    data.append(r["created_at"])
                else:
                    pass

        data = {"data": data}
        return data


def get_api(plantID):
    """Asks catalog readAPI and channelID."""
    url, port = read_file_short(FILE)
    string = "http://" + url + ":" + port + "/info/" + plantID
    r = json.loads(requests.get(string).text)
    channel = r["thingspeakID"]
    string = "http://" + url + ":" + port + "/api/tschannel/" + str(channel)
    r = json.loads(requests.get(string).text)
    readAPI = r["readAPI"]
    return readAPI, channel


def get_field(resource, devID):
    """Get field number for a specific resource.

    The number is used on TS to
    identify a channel field. It is also stored in the catalog associated to
    the sensor in the resource list.
    """
    url, port = read_file_short(FILE)
    string = "http://" + url + ":" + port + "/info/" + devID
    print("\n", string, "\n")
    r = json.loads(requests.get(string).text)
    for i in r["resources"]:
        if i["n"] == resource:
            f = i["f"]

    fieldID = str(f)
    return fieldID


if __name__ == "__main__":
    thread1 = SubmitData(1, "SubmitData")
    thread1.start()
    thread2 = Timer(2, "Timer")
    thread2.start()
    thread3 = CherryThread(3, "CherryServer")
    thread3.start()

#ciao ragazzi
