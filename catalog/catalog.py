#!/usr/bin/env python3

import json
import cherrypy
import time
import datetime
import requests
import threading
import paho.mqtt.client as PahoMQTT

JSON_FILE = 'static.json'
JSON_FILE2 = 'dynamic.json'
CONF_FILE = 'conf'
TOPIC = '/device/updater'
BROKER_IP = '192.168.1.70'
OLD_MAX = 300

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

    def write_file(self):
        with open(self.filename2, "w") as fd:
            json.dump(self.dynamic, fd, ensure_ascii=False)

    def add_device(self, gardenID, plantID, devID):
        data = {'devID': devID, 'timestamp': time.time()}
        self.load_file()
        for g in self.dynamic["gardens"]:
            if g['gardenID'] == gardenID:
                break

        for p in g['plants']:
            if p['plantID'] == plantID:
                break

        for d in p['devices']:
            if d['devID'] == devID:
                d['timestamp'] = time.time()

        self.write_file()

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


class Webserver(object):
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):

        catalog = Catalog(JSON_FILE, JSON_FILE2)
        catalog.load_file()
        if uri[0] == 'devices':
            """Get all devices from a specific plant in the garden.
            If the plant is present it returns a json with the list of devices.
            If the plant is not found it returns -1.
            """
            gardenID = uri[1]
            plantID = uri[2]
            g_found = 0
            p_found = 0
            
            for g in catalog.dynamic["gardens"]:
                if g["gardenID"] == gardenID:
                    g_found = 1
                    break

            for p in g["plants"]:
                if p["plantID"] == plantID:
                    p_found = 1
                    break

            if g_found and p_found:
                devices = p["devices"]
                return devices

            else:
                return -1

        #catalog.add_device("garden1", "plant1", "dht11")
        #catalog.load_file()

        if uri[0] == 'catalog':
            # if uri[1] == 'p':
            #     return catalog.get_sensors()
            # else:
            #     return catalog.static
            return catalog.dynamic


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
        gardenID = message["gardenID"]
        plantID = message["plantID"]
        devID = message["devID"]
        catalog.update_device(gardenID, plantID, devID)

class First(threading.Thread):
    def __init__(self,ThreadID,name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name
    def run(self):
        try:
            cherrypy.tree.mount(Webserver(), '/', config=CONF_FILE)
            cherrypy.config.update('conf')
            cherrypy.engine.start()
            cherrypy.engine.block()
        except KeyboardInterrupt:
            print ("Stopping the engine")
            return



class Second(threading.Thread):
    def __init__(self,ThreadID,name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):
        sub = MySubscriber("Sub1", TOPIC, BROKER_IP)
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
        while True:
            time.sleep(6000)
            cat = Catalog(JSON_FILE, JSON_FILE2)
            cat.remove_old_device()

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
