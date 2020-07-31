#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resource catalog."""
import json
import cherrypy
import time
import requests
import threading
import paho.mqtt.client as PahoMQTT
from pathlib import Path

# Global variables
P = Path(__file__).parent.absolute()
JSON_STATIC = P / 'static.json'
JSON_DYNAMIC = P / 'dynamic.json'
APIFILE = P / 'api.json'
CHERRY_CONF = str(P / 'cherrypyconf')
CONFIG = P / 'conf.json'
OLD_MAX = 300
REMOVE_AFTER = 600


# Functions
def read_config(filename):
    """Read config file.

    Read conf.json file and return URL of catalog, REST port and general
    MQTT topic of the garden.
    """
    with open(filename, "r") as file:
        f = json.loads(file.read())
        cat_ip = f["cat_ip"]
        cat_port = f["cat_port"]
        topic = f["topic"]
    return (cat_ip, cat_port, topic)


# Classes
class Catalog(object):
    """Resource catalog class."""

    def __init__(self, filename_static, filename_dynamic):
        """Set filename of static and dynamic jsons."""
        self.filename_s = filename_static
        self.filename_d = filename_dynamic

    def load_file(self):
        """Load static and dynamic parts of catalog.

        Load data (static, dynamic) from json files and get MQTT broker IP
        and MQTT broker port saved on static file.
        """
        loaded = 0
        while not loaded:
            try:
                with open(self.filename_s, "r") as fs:
                    self.static = json.loads(fs.read())
                with open(self.filename_d, "r") as fd:
                    self.dynamic = json.loads(fd.read())
                loaded = 1
            except Exception:
                print("Problem in loading catalog, retrying...")
                time.sleep(.5)

        self.broker_ip = self.static["broker"]["IP"]
        self.mqtt_port = self.static["broker"]["mqtt_port"]

    def write_static(self):
        """Write data on static json file."""
        with open(self.filename_s, "w") as fs:
            json.dump(self.static, fs, ensure_ascii=False, indent=2)
            fs.write("\n")

    def write_dynamic(self):
        """Write data on dynamic json file."""
        with open(self.filename_d, "w") as fd:
            json.dump(self.dynamic, fd, ensure_ascii=False, indent=2)
            fd.write("\n")

    def add_garden(self, garden_json):
        """Add a new garden in the static catalog.

        The new gardenID is auto-generated.
        """
        # Look at the existing garden IDs.
        self.load_file()
        list_id = []

        for g in self.static["gardens"]:
            list_id.append(g["gardenID"])

        # Generate a new gardenID starting from 1000 and taking the first free
        # number which is available.
        numID = 1001
        new_id = 'g_' + str(numID)

        while new_id in list_id:
            numID += 1
            new_id = 'g_' + str(numID)

        garden_json["plants"] = []
        garden_json["users"] = []
        garden_json["gardenID"] = new_id
        print(garden_json)

        self.static["gardens"].append(garden_json)
        garden_dyn_json = {
            "gardenID": garden_json["gardenID"],
            "plants": []
        }
        self.dynamic["gardens"].append(garden_dyn_json)
        self.write_static()
        self.write_dynamic()

    def add_plant(self, plant_json):
        """Add a new plant in the static catalog.

        The new plantID is auto-generated.
        """
        self.load_file()
        list_id = []

        # Generate list of all plantIDs
        for g in self.static["gardens"]:
            for p in g["plants"]:
                list_id.append(p["plantID"])

        # Find specific garden element in static and dynamic jsons.
        for g in self.static["gardens"]:
            if g["gardenID"] == plant_json["gardenID"]:
                break

        for gd in self.dynamic["gardens"]:
            if gd["gardenID"] == plant_json["gardenID"]:
                break

        # Generate a new plantID.
        numID = 1001
        new_id = 'p_' + str(numID)

        while new_id in list_id:
            numID += 1
            new_id = 'p_' + str(numID)

        del plant_json["gardenID"]
        plant_json["plantID"] = new_id
        plant_json["devices"] = []

        g["plants"].append(plant_json)
        plant_dyn_json = {
            "plantID": plant_json["plantID"],
            "devices": [],
            "hours": []
        }
        for h in plant_json["hours"]:
            entry = {
                "time": h["time"],
                "duration": 0,
                "delay": 0
            }
            plant_dyn_json["hours"].append(entry)

        gd["plants"].append(plant_dyn_json)

        self.write_static()
        self.write_dynamic()

    def add_device(self, dev_json):
        """Add a new device in the static catalog.

        The new deviceID is auto-generated.
        """
        self.load_file()

        list_id = []
        for g in self.static["gardens"]:
            for p in g["plants"]:
                for d in p["devices"]:
                    list_id.append(d["devID"])

        for g in self.static["gardens"]:
            if g["gardenID"] == dev_json["gardenID"]:
                break
        for p in g["plants"]:
            if p["plantID"] == dev_json["plantID"]:
                break

        # Generate a new devID.
        numID = 1001
        new_id = 'd_' + str(numID)

        while new_id in list_id:
            numID += 1
            new_id = 'd_' + str(numID)

        del dev_json["gardenID"]
        del dev_json["plantID"]
        dev_json["devID"] = new_id

        p["devices"].append(dev_json)
        self.write_static()

    def update_device(self, gardenID, plantID, devID, topic):
        """Update timestamp of a device.

        Update timestamp or insert it again in the dynamic catalog if it has
        expired.
        """
        data = {'devID': devID, 'timestamp': time.time(), 'topic': topic}
        self.load_file()

        for g in self.dynamic["gardens"]:
            if g['gardenID'] == gardenID:
                break

        for p in g['plants']:
            if p['plantID'] == plantID:
                break

        found = 0
        for d in p['devices']:
            if d['devID'] == devID:
                found = 1
                print("Updating %s timestamp." % devID)
                d['timestamp'] = time.time()
                d['topic'] = topic

        if not found:  # Insert again the device

            # But first check if device is allowed from the static catalog.
            for g2 in self.static["gardens"]:
                if g2['gardenID'] == gardenID:
                    break

            for p2 in g2['plants']:
                if p2['plantID'] == plantID:
                    break

            for d2 in p2['devices']:
                if d2['devID'] == devID:  # In static JSON
                    allowed = 1
                    print("%s reconnected!" % devID)
                    p['devices'].append(data)  # In dynamic JSON

            if not allowed:
                print("Device %s wants to be updated but it seems to be not', \
                      'present in the catalog, please check." % devID)

        self.write_dynamic()

    def remove_old_device(self):
        """Remove old devices whose timestamp is expired.

        Check all the devices whose timestamps are old and remove them from
        the dynamic catalog.
        """
        self.load_file()

        for g in self.dynamic["gardens"]:
            for p in g['plants']:
                removable = []
                for counter, d in enumerate(p['devices']):
                    print(counter, d)
                    if time.time() - d['timestamp'] > OLD_MAX:
                        print("Removing... %s" % (d['devID']))
                        removable.append(counter)
                for index in sorted(removable, reverse=True):
                    del p['devices'][index]

        print(self.dynamic)
        self.write_dynamic()

    def info(self, ID):
        """Return all information about a garden/plant/device" given an ID."""
        self.load_file()
        for g in self.static["gardens"]:
            if g["gardenID"] == ID:
                info = {"gardenID": ID, "plants": g["plants"],
                        "name": g["name"]}
                return info

            for p in g["plants"]:
                if p["plantID"] == ID:
                    info = {"gardenID": g["gardenID"], "plantID": ID,
                            "name": p["name"],
                            "thingspeakID": p["thingspeakID"],
                            "devices": p["devices"],
                            "hours": p["hours"],
                            "environment": p["environment"]}
                    return info

                topic = None
                for d in p["devices"]:
                    if d["devID"] == ID:
                        try:
                            for g2 in self.dynamic["gardens"]:
                                for p2 in g2["plants"]:
                                    for d2 in p2["devices"]:
                                        if d2["devID"] == ID:
                                            topic = d2["topic"]
                        except Exception:
                            print("%s topic was not registered!" % ID)

                        info = {"gardenID": g["gardenID"],
                                "plantID": p["plantID"],
                                "thingspeakID": p["thingspeakID"],
                                "devID": ID, "resources": d["resources"],
                                "name": d["name"], "topic": topic}
                        return info
        return -1

    def get_token(self, filename):
        """Read api.json and returns Telegram token for Telegram bot."""
        with open(filename, "r") as f:
            api = json.loads(f.read())

        t = {"token": api["telegramtoken"]}
        return t

    def get_ts_api(self, filename, id):
        """Read api.json and returns ThingSpeak channel ID."""
        with open(filename, "r") as f:
            api = json.loads(f.read())

        for c in api["TSchannels"]:
            if c["ID"] == id:
                return c

    def edit_hour(self, plantID, hour, duration, delay):
        """Edit irrigation parameters on dynamic part."""
        self.load_file()

        for g in self.dynamic["gardens"]:
            for p in g["plants"]:
                if p["plantID"] == plantID:
                    for h in p["hours"]:
                        if h["time"] == hour:
                            h["delay"] += delay
                            h["duration"] += duration
        self.write_dynamic()

    def reset_hour(self, plantID, hour):
        """Reset irrigation parameters to default.

        After every irrigation this function is called and irrigation
        parameters for the given plantID/hour are resetted for the new day.
        """
        self.load_file()
        for g in self.dynamic["gardens"]:
            for p in g["plants"]:
                if p["plantID"] == plantID:
                    for h in p["hours"]:
                        if h["time"] == hour["time"]:
                            h["duration"] = 0  # Reset value
                            h["delay"] = 0

        self.write_dynamic()

    def edit_hour_delay(self, plantID, hour, new_hour):
        """Edit irrigation hour in static and dynamic catalog.

        Change irrigation hour to new hour e.g. 19:00->18:20 in static and
        dynamic parts of catalog. It is used when an irrigation has to be
        anticipated and so the next day it will be sheduled to a different
        hour.
        """
        self.load_file()
        for g in self.static["gardens"]:
            for p in g["plants"]:
                if p["plantID"] == plantID:
                    for h in p["hours"]:
                        if h["time"] == hour:
                            h["time"] = new_hour

        self.write_static()

        for g in self.dynamic["gardens"]:
            for p in g["plants"]:
                if p["plantID"] == plantID:
                    for h in p["hours"]:
                        if h["time"] == hour:
                            h["time"] = new_hour

        self.write_dynamic()

    def change_hour(self, plantID, vector):
        """Edit irrigation hour in static and dynamic catalog.

        Change irrigation hour to new hour e.g. 19:00->18:45 in static and
        dynamic parts of catalog. It is used by a strategy which analyze
        data of recent days and find if the irrigation times are always
        postponed or anticipated comparing to the one on the catalog.
        """
        self.load_file()

        # Static part.
        for g in self.static["gardens"]:
            for p in g["plants"]:
                if p["plantID"] == plantID:
                    p["hours"] = vector
        self.write_static()

        # Dynamic part.
        for g in self.dynamic["gardens"]:
            for p in g["plants"]:
                if p["plantID"] == plantID:
                    c = 0
                    for h in p["hours"]:
                        h["time"] = vector[c]["time"]
                        c = c + 1
        self.write_dynamic()


class Webserver(object):
    """CherryPy webserver."""

    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        """Define GET HTTP method for RESTful webserver."""
        cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
        cat.load_file()

        # Get broker info (url, port).
        if uri[0] == 'broker':
            return cat.static["broker"]

        if uri[0] == 'ts':
            return cat.static["thingspeak"]

        # Get dynamic catalog json.
        if uri[0] == 'dynamic':
            return cat.dynamic

        # Get static catalog json.
        if uri[0] == 'static':
            return cat.static

        # Get all information about a garden/plant/device.
        if uri[0] == 'info':
            ID = uri[1]
            return cat.info(ID)

        # Get reserved information (telegram token or ThingSpeak channel APIs).
        if uri[0] == 'api':
            if uri[1] == 'telegramtoken':
                return cat.get_token(APIFILE)

            if uri[1] == 'tschannel':
                return cat.get_ts_api(APIFILE, uri[2])

    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        """Define POST HTTP method for RESTful webserver."""
        # Add new garden.
        if uri[0] == 'addg':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            print(json.dumps(body))
            cat.add_garden(body)
            return 200

        # Add new plant.
        if uri[0] == 'addp':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            print(json.dumps(body))
            cat.add_plant(body)
            return 200

        # Add new device.
        if uri[0] == 'addd':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            print(json.dumps(body))
            cat.add_device(body)
            return 200

        # Change irrigation parameters (duration and hours) on dynamic part.
        if uri[0] == 'edit_hour':  # post_mod
            body = json.loads(cherrypy.request.body.read())
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            cat.edit_hour(body["plantID"], body["hour"],
                          body["duration"], body["delay"])
            return 200

        if uri[0] == 'reset_hour':  # reset_mod
            body = json.loads(cherrypy.request.body.read())
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            cat.reset_hour(body["plantID"], body["hour"])
            return 200

        if uri[0] == 'edit_hour_delay':  # reset_mod
            body = json.loads(cherrypy.request.body.read())
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            cat.edit_hour_delay(body["plantID"], body["hour"],
                                body["new_hour"])
            return 200
        # # Change irrigation parameters (duration and hours) on dynamic part.
        # # If static == 0 change duration and delay of irrigation on dynamic.
        # # if static == 1 change old to new hour in static and dynamic parts.
        # if uri[0] == 'edit_hour':
        #     body = json.loads(cherrypy.request.body.read())
        #     cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
        #
        #     # Change duration and delay on dynamic part.
        #     if body["static"] == 0:
        #         cat.edit_hour(body["plantID"], body["hour"], body["mod"],
        #                       body["modh"], body["reset"])
        #
        #         print(json.dumps(body))
        #         return 200
        #
        #     elif body["static"] == 1:  # Change on static and dynamic.
        #         cat.edit_static_hour(body["plantID"], body["hour"],
        #                              body["new_hour"])
        #         return 200

        # Change irrigation times (hours) e.g. 19:00 -> 18:20.
        if uri[0] == 'update':
            if uri[1] == 'time':
                body = json.loads(cherrypy.request.body.read())  # Read body
                cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
                print(body)
                cat.change_hour(body["plantID"], body["hours"])


class MySubscriber:
    """MQTT subscriber.

    It subscribes to all topics in order to receive alive messages from sensors
    and update their timestams in the dynamic part of the catalog.
    """

    def __init__(self, clientID, topic, serverIP):
        """Initialise MQTT client."""
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received
        (self.url, self.port, self.smart_topic) = read_config(CONFIG)

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
        print("Connected to %s - Result code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        """Define custom on_message function.

        Receives json messages from other devices and get info to update
        old timestamps or insert expired devices.
        """
        msg.payload = msg.payload.decode("utf-8")
        message = json.loads(msg.payload)
        catalog = Catalog(JSON_STATIC, JSON_DYNAMIC)
        devID = message['bn']
        try:
            for e in message['e']:
                if e['n'] == 'alive' and e['v'] == 1:
                    topic = e['topic']
                    string = ('http://' + self.url + ':' + self.port +
                              '/info/' + devID)
                    info = json.loads(requests.get(string).text)
                    gardenID = info["gardenID"]
                    plantID = info["plantID"]
                    catalog.update_device(gardenID, plantID, devID, topic)
        except Exception:
            pass


# Threads
class First(threading.Thread):
    """Thread to run CherryPy webserver."""

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):
        """Run thread."""
        try:
            cherrypy.tree.mount(Webserver(), '/', config=CHERRY_CONF)
            cherrypy.config.update(CHERRY_CONF)
            cherrypy.engine.start()
            cherrypy.engine.block()

        except KeyboardInterrupt:
            print("Stopping the engine")
            return


class Second(threading.Thread):
    """MQTT Thread.

    Subscribe to MQTT in order to update timestamps of sensors in the dynamic
    part of the catalog.
    """

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):
        """Run thread."""
        cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
        cat.load_file()
        broker_ip = cat.broker_ip
        u, p, topic = read_config(CONFIG)
        sub = MySubscriber("Sub1", topic, broker_ip)
        sub.loop_flag = 1
        sub.start()

        while sub.loop_flag:
            print("Waiting for connection...")
            time.sleep(1)

        while True:
            time.sleep(1)

        sub.stop()


class Third(threading.Thread):
    """Old device remover thread.

    Remove old devices which do not send alive messages anymore.
    Devices are removed every five minutes.
    """

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):
        """Run thread."""
        time.sleep(REMOVE_AFTER)
        while True:
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            cat.remove_old_device()
            time.sleep(REMOVE_AFTER)


# Main
def main():
    """Start all threads."""
    thread1 = First(1, "CherryPy")
    thread2 = Second(2, "Updater")
    thread3 = Third(3, "Remover")

    print("> Starting CherryPy...")
    thread1.start()

    time.sleep(1)
    print("\n> Starting MQTT device updater...")
    thread2.start()

    time.sleep(1)
    print("\n> Starting remover...\nDelete old devices every %d seconds."
          % REMOVE_AFTER)
    thread3.start()


if __name__ == '__main__':
    main()
