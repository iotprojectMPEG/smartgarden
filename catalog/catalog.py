#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import json
import cherrypy
import time
import datetime
import requests
import threading
import paho.mqtt.client as PahoMQTT

JSON_STATIC = 'static.json'
JSON_DYNAMIC = 'dynamic.json'
APIFILE = 'api.json'
CHERRY_CONF = 'cherrypyconf'
CONFIG = 'conf.json'
TOPIC = 'smartgarden/+/+/+'

OLD_MAX = 300
REMOVE_AFTER = 600

class Catalog(object):
    def __init__(self, filename_static, filename_dynamic):
        self.filename_s = filename_static
        self.filename_d = filename_dynamic

    def load_file(self):
        with open(self.filename_s, "r") as fs:
            self.static = json.loads(fs.read())

        with open(self.filename_d, "r") as fd:
            self.dynamic = json.loads(fd.read())

        self.broker_ip = self.static["broker"]["IP"]
        self.mqtt_port = self.static["broker"]["mqtt_port"]


    def write_static(self):
        with open(self.filename_s, "w") as fs:
            json.dump(self.static, fs, ensure_ascii=False, indent=2)

    def write_dynamic(self):
        with open(self.filename_d, "w") as fd:
            json.dump(self.dynamic, fd, ensure_ascii=False, indent=2)

    def add_garden(self, garden_json):
        """Adds a new garden in the static catalog.
           Auto-generate a new gardenID.
        """
        self.load_file()
        list_id = []

        for g in self.static["gardens"]:
            list_id.append(g["gardenID"])

        # Generate a new gardenID.
        numID = 1000
        new_id = 'g_' + str(numID)

        while new_id in list_id:
            numID += 1
            new_id = 'g_' + str(numID)

        garden_json["plants"] = []
        garden_json["gardenID"] = new_id
        print(garden_json)

        self.static["gardens"].append(garden_json)
        self.write_static()

    def add_plant(self, plant_json):
        """Adds a new plant in the static catalog.
           Auto-generate a new plantID.
        """
        self.load_file()
        list_id = []

        for g in self.static["gardens"]:
            if g["gardenID"] == plant_json["gardenID"]:
                break
            for p in g["plants"]:
                list_id.append(p["plantID"])

        # Generate a new plantID.
        numID = 1000
        new_id = 'p_' + str(numID)

        while new_id in list_id:
            numID += 1
            new_id = 'p_' + str(numID)

        del plant_json["gardenID"]
        plant_json["plantID"] = new_id
        plant_json["devices"] = []

        g["plants"].append(plant_json)
        self.write_static()

    def add_device(self, dev_json):
        """Add a new device in the static catalog.
        """
        self.load_file()
        list_id = []
        for g in self.static["gardens"]:
            if g["gardenID"] == dev_json["gardenID"]:
                break
        for p in g["plants"]:
            if p["plantID"] == dev_json["plantID"]:
                break
            for d in p["devices"]:
                list_id.append(d["devID"])

        # Generate a new devID.
        numID = 1000
        new_id = 'd_' + str(numID)

        while new_id in list_id:
            numID += 1
            new_id = 'd_' + str(numID)

        del dev_json["gardenID"]
        del dev_json["plantID"]
        dev_json["devID"] = new_id

        p["devices"].append(dev_json)
        self.write_static()

    def add_new(self, gardenID, plantID, devID, endpoints, resources):
        """Insert new device in the static catalog
        """
        data = {'gardenID': gardenID, 'plantID': plantID, 'devID': devID}
        found = 0
        for g in self.dynamic["gardens"]:
            if g['gardenID'] == gardenID:
                break

        for p in g['plants']:
            if p['plantID'] == plantID:
                break

        for d in p['devices']:
            if d['devID'] == devID:
                return -1  # Device already registered

    def update_device(self, gardenID, plantID, devID):
        """Update timestamp of a device or insert it again in the dynamic
        catalog if it has expired.
        """
        data = {'devID': devID, 'timestamp': time.time()}
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
                d['timestamp'] = time.time()

        # Insert again the device
        if not found:
            # TO DO: Check if device is allowed from the static catalog.
            p['devices'].append(data)

        print("Updating", devID)
        self.write_dynamic()

    def remove_old_device(self):
        """Check all the devices whose timestamp is old and remove them from
        the dynamic catalog.
        """
        self.load_file()

        for g in self.dynamic["gardens"]:
            for p in g['plants']:
                removable = []
                for counter, d in enumerate(p['devices']):
                    print(counter, d)
                    if time.time() - d['timestamp'] > OLD_MAX:
                        print("Removing... %s" %(d['devID']))
                        removable.append(counter)
                for index in sorted(removable, reverse=True):
                    del p['devices'][index]

        print(self.dynamic)
        self.write_dynamic()

    def info(self, ID):
        self.load_file()
        for g in self.static["gardens"]:
            if g["gardenID"] == ID:
                info = {"gardenID": ID, "plants": g["plants"], "name": g["name"]}
                return info

            for p in g["plants"]:
                if p["plantID"] == ID:
                    info = {"gardenID": g["gardenID"], "plantID": ID,
                            "name": p["name"],
                            "thingspeakID": p["thingspeakID"],
                            "devices": p["devices"]}
                    return info

                for d in p["devices"]:
                    if d["devID"] == ID:
                        info = {"gardenID": g["gardenID"],
                                "plantID": p["plantID"],
                                "thingspeakID": p["thingspeakID"],
                                "devID": ID, "resources": d["resources"],
                                "name": d["name"]}
                        return info
        return -1


    def get_token(self, filename):
        with open(filename, "r") as f:
            api = json.loads(f.read())

        t = {"token": api["telegramtoken"]}
        return t

    def get_ts_api(self, filename, id):
        with open(filename, "r") as f:
            api = json.loads(f.read())

        for c in api["TSchannels"]:
            if c["ID"] == id:
                return c

def read_config(filename):
    with open(filename, "r") as file:
        f = json.loads(file.read())
        url = f["catalogURL"]
        port = f["port"]
    return (url, port)

class Webserver(object):
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):

        catalog = Catalog(JSON_STATIC, JSON_DYNAMIC)
        catalog.load_file()


        if uri[0] == 'broker':
            return catalog.static["broker"]

        # if uri[0] == 'devices':
        #     """Get all devices from a specific plant in the garden.
        #     If the plant is present it returns a json with the list of devices.
        #     If the plant is not found it returns -1.
        #     """
        #     gardenID = uri[1]
        #     plantID = uri[2]
        #     g_found = 0
        #     p_found = 0
        #
        #     for g in catalog.dynamic["gardens"]:
        #         if g["gardenID"] == gardenID:
        #             g_found = 1
        #             break
        #
        #     for p in g["plants"]:
        #         if p["plantID"] == plantID:
        #             p_found = 1
        #             break
        #
        #     if g_found and p_found:
        #         devices = p["devices"]
        #         return devices
        #
        #     else:
        #         return -1

        #catalog.add_device("garden1", "plant1", "dht11")
        #catalog.load_file()

        if uri[0] == 'dynamic':
            return catalog.dynamic

        if uri[0] == 'static':
            return catalog.static


        if uri[0] == 'info':
            ID = uri[1]
            return catalog.info(ID)

        if uri[0] == 'api':
            if uri[1] == 'telegramtoken':
                return catalog.get_token(APIFILE)

            if uri[1] == 'tschannel':
                return catalog.get_ts_api(APIFILE, uri[2])

    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        if uri[0] == 'addg':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            print(json.dumps(body))
            cat.add_garden(body)
            return 200

        if uri[0] == 'addp':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            print(json.dumps(body))
            cat.add_plant(body)
            return 200

        if uri[0] == 'addd':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            print(json.dumps(body))
            cat.add_device(body)
            return 200

class MySubscriber:
    def __init__(self, clientID, topic, serverIP):
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        print ("Connected to %s - Result code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        """Receives json messages in the topic '/device/updater' from other
        devices and get info to update old timestamps or insert expired devices.

        json format:
        {"gardenID": "garden1", "plantID": "plant1", "devID": "dht11"}
        """
        msg.payload = msg.payload.decode("utf-8")
        message = json.loads(msg.payload)
        catalog = Catalog(JSON_STATIC, JSON_DYNAMIC)
        devID = message['bn']
        try:
            for e in message['e']:
                if e['n'] == 'alive' and e['v'] == 1:
                    (url, port) = read_config(CONFIG)
                    string = 'http://' + url + ':' + port + '/info/' + devID
                    info = json.loads(requests.get(string).text)
                    gardenID = info["gardenID"]
                    plantID = info["plantID"]
                    catalog.update_device(gardenID, plantID, devID)
        except:
            pass


class First(threading.Thread):
    def __init__(self,ThreadID,name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name
    def run(self):
        try:
            cherrypy.tree.mount(Webserver(), '/', config=CHERRY_CONF)
            cherrypy.config.update(CHERRY_CONF)
            cherrypy.engine.start()
            cherrypy.engine.block()
        except KeyboardInterrupt:
            print ("Stopping the engine")
            return


class Second(threading.Thread):
    """Subscribe to MQTT in order to update timestamps of sensors
    """
    def __init__(self,ThreadID,name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):
        cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
        cat.load_file()
        broker_ip = cat.broker_ip #json.loads(broker.text)["IP"]
        sub = MySubscriber("Sub1", TOPIC, broker_ip)
        sub.loop_flag = 1
        sub.start()


        while sub.loop_flag:
            print("Waiting for connection...")
            time.sleep(1)

        while True:
            time.sleep(1)

        sub.stop()


class Third(threading.Thread):
    def __init__(self,ThreadID,name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):
        time.sleep(REMOVE_AFTER)
        while True:
            cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
            cat.remove_old_device()
            time.sleep(REMOVE_AFTER)

def main():
    thread1 = First(1,"CherryPy")
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
