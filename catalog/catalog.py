#!/usr/bin/env python3

import numpy as np
import json
import cherrypy
import time
import datetime
import requests
import threading
import paho.mqtt.client as PahoMQTT

JSON_FILE = 'static.json'
JSON_FILE2 = 'dynamic.json'
CONF_FILE = 'cherrypyconf'
TOPIC = 'smartgarden/+/+/+'

OLD_MAX = 300
#URL = "http://192.168.1.70:8080/broker"

class Catalog(object):
    def __init__(self, filename, filename2):
        self.filename = filename
        self.filename2 = filename2

    def load_file(self):
        with open(self.filename, "r") as fs:
            self.static = json.loads(fs.read())
            print("Static loaded")
        with open(self.filename2, "r") as fd:
            self.dynamic = json.loads(fd.read())
            print("Dynamic loaded")

        self.broker_ip = self.static["broker"]["IP"]
        self.rest_port = self.static["broker"]["rest_port"]
        self.mqtt_port = self.static["broker"]["mqtt_port"]

    def write_file(self):
        with open(self.filename, "w") as fs:
            json.dump(self.static, fs, ensure_ascii=False)
        with open(self.filename2, "w") as fd:
            json.dump(self.dynamic, fd, ensure_ascii=False)

    # def add_device(self, gardenID, plantID, devID):
    #     data = {'devID': devID, 'timestamp': time.time()}
    #     self.load_file()
    #     for g in self.dynamic["gardens"]:
    #         if g['gardenID'] == gardenID:
    #             break
    #
    #     for p in g['plants']:
    #         if p['plantID'] == plantID:
    #             break
    #
    #     for d in p['devices']:
    #         if d['devID'] == devID:
    #             d['timestamp'] = time.time()
    #
    #     self.write_file()

    def add_garden(self, garden_json):
        """Adds a new garden in the static catalog.
           Needs a garden_json formatted as:

           {
           "name": "MyGarden"
           "location": "Turin"
           }

        """
        self.load_file()
        list_id = []
        for g in self.static["gardens"]:
            list_id.append(g["gardenID"])

        new_id = 'g_' + str(np.random.randint(1000, 9999))

        while new_id in list_id:
            new_id = 'g_' + str(np.random.randint(1000, 9999))

        garden_json["plants"] = []
        garden_json["gardenID"] = new_id
        print(garden_json)

        self.static["gardens"].append(garden_json)
        self.write_file()



    def add_plant(self, plant_json):
        """Adds a new plant in the static catalog.
           Needs a plant_json formatted as:

           {
           "gardenID": "g_9999"
           "name": "Dionea"
           }

        """
        self.load_file()
        list_id = []
        for g in self.static["gardens"]:
            if g["gardenID"] == plant_json["gardenID"]:
                break
            for p in g["plants"]:
                list_id.append(p["plantID"])

        new_id = 'p_' + str(np.random.randint(1000, 9999))

        while new_id in list_id:
            new_id = 'p_' + str(np.random.randint(1000, 9999))

        del plant_json["gardenID"]
        plant_json["plantID"] = new_id
        plant_json["devices"] = []

        g["plants"].append(plant_json)
        self.write_file()

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

        new_id = 'd_' + str(np.random.randint(1000, 9999))

        while new_id in list_id:
            new_id = 'd_' + str(np.random.randint(1000, 9999))

        del dev_json["gardenID"]
        del dev_json["plantID"]
        dev_json["devID"] = new_id

        p["devices"].append(dev_json)
        self.write_file()

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
        self.write_file()

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
        self.write_file()

    def info(self, ID):
        self.load_file()
        for g in self.static["gardens"]:
            if g["gardenID"] == ID:
                info = {"gardenID": ID, "plants": g["plants"], "name": g["name"]}
                return info

            for p in g["plants"]:
                if p["plantID"] == ID:
                    info = {"gardenID": g["gardenID"], "plantID": ID,
                            "devices": p["devices"], "name": p["name"]}
                    return info

                for d in p["devices"]:
                    if d["devID"] == ID:
                        info = {"gardenID": g["gardenID"],
                                "plantID": p["plantID"],
                                "devID": ID, "resources": d["resources"],
                                "name": d["name"]}
                        return info
        return -1


class Webserver(object):
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):

        catalog = Catalog(JSON_FILE, JSON_FILE2)
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

        if uri[0] == 'status':
            # if uri[1] == 'p':
            #     return catalog.get_sensors()
            # else:
            #     return catalog.static
            return catalog.dynamic

        if uri[0] == 'static':
            return catalog.static


        if uri[0] == 'info':
            ID = uri[1]
            return catalog.info(ID)


        # if uri[0] == 'device':
        #     devID = uri[1]
        #     for g in catalog.static["gardens"]:
        #         for p in g["plants"]:
        #             for d in p["devices"]:
        #                 if d["devID"] == devID:
        #                     info = {"gardenID": g["gardenID"],
        #                             "plantID": p["plantID"],
        #                             "devID": d["devID"]}
        #                     return info
        #     return -1
        #
        # if uri[0] == 'plant':
        #     plantID = uri[1]
        #     for g in catalog.static["gardens"]:
        #         for p in g["plants"]:
        #             if p["plantID"] == plantID:
        #                 info = {"gardenID": g["gardenID"],
        #                         "plantID": p["plantID"],
        #                         "devices": p["devices"]}
        #                 return info
        #     return -1
        #
        # if uri[0] == 'garden':
        #     gardenID = uri[1]
        #     for g in catalog.static["gardens"]:
        #         for p in g["plants"]:
        #             if p["plantID"] == plantID:
        #                 info = {"gardenID": g["gardenID"],
        #                         "plantID": p["plantID"],
        #                         "devices": p["devices"]}
        #                 return info
        #     return -1

            # print(g["gardenID"])
            # print(p["plantID"])
            # print(d["devID"])
            # print("\n\n\n")

    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        if uri[0] == 'addg':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog(JSON_FILE, JSON_FILE2)
            print(json.dumps(body))
            cat.add_garden(body)
            return 200

        if uri[0] == 'addp':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog(JSON_FILE, JSON_FILE2)
            print(json.dumps(body))
            cat.add_plant(body)
            return 200

        if uri[0] == 'addd':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog(JSON_FILE, JSON_FILE2)
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
        catalog = Catalog(JSON_FILE, JSON_FILE2)
        #gardenID = message["gardenID"]
        #plantID = message["plantID"]
        devID = message["devID"]
        string = 'http://192.168.1.70:8080/info/'+devID
        print("\n\n\n")
        print(string)
        print("\n\n\n")
        info = json.loads(requests.get(string).text)
        gardenID = info["gardenID"]
        plantID = info["plantID"]
        catalog.update_device(gardenID, plantID, devID)

class First(threading.Thread):
    def __init__(self,ThreadID,name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name
    def run(self):
        try:
            cherrypy.tree.mount(Webserver(), '/', config=CONF_FILE)
            cherrypy.config.update(CONF_FILE)
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
        cat = Catalog(JSON_FILE, JSON_FILE2)
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
        time.sleep(50000)
        while True:
            cat = Catalog(JSON_FILE, JSON_FILE2)
            cat.remove_old_device()
            time.sleep(300)

def main():
    thread1 = First(1,"CherryPy")
    thread2 = Second(2,"Updater")
    thread3 = Third(3, "Remover")

    print("Starting CherryPy...")
    thread1.start()

    time.sleep(1)
    print("\nStarting MQTT device updater...")
    thread2.start()

    time.sleep(1)
    print("\nStarting remover...")
    thread3.start()






if __name__ == '__main__':
    main()
