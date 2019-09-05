#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script...
"""
import json
import sys, os
import threading
import requests
import time
import datetime
import schedule
import paho.mqtt.client as PahoMQTT
from rain_control import rain_control
from light_control import light_control
from wind_control import wind_control
from hum_control import hum_control
from temp_control import temp_control

FILE1 = "conf.json"
URL = None  # Catalog URL
PORT = None  # Catalog port
plant_list = []  # Plant list


def read_file(filename):
    """Read json file to get catalogURL, port and gardenID."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["catalogURL"]
        port = data["port"]
        gardenID = data["gardenID"]

        return (url, port, gardenID)


def update_global(url, port):
    global URL
    URL = url
    global PORT
    PORT = port


def post_mod(plantID, h, mod=0, modh=0, reset=0, static=0, new_hour=None):
    data = {
        "plantID": plantID,
        "hour": h,
        "mod": mod,
        "modh": modh,
        "reset": reset,
        "static": static,
        "new_hour": new_hour
    }

    # POST on catalog.
    string = "http://" + URL + ":" +str(PORT) + "/hours"
    r = requests.post(string, data=json.dumps(data))


def rain(plantID, h, type, env):
    if rain_control.get_result(plantID, env):
        pass


def light(plantID, h, type, env):
    """Type: morning/evening.
    Morning: anticipate irrigation if there is too much light.
    Evening: posticipate irrigation if there is too much light.
    """
    print(plantID, type)
    sec = rain_control.get_result(plantID, env, type)


def wind(plantID, h, type, env):
    sec = wind_control.get_result(plantID, env)
    post_mod(plantID, h, sec)
    pass


def hum(plantID, h, type, env):
    sec = hum_control.get_result(plantID, env)
    pass


def temp(plantID, h, type, env):
    sec = temp_control.get_result(plantID, env)
    pass


class MyPublisher(object):
    """MQTT publisher."""
    def __init__(self, clientID, serverIP, port):
        self.clientID = clientID + '_pub'
        self.devID = clientID
        self.port = int(port)
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self.loop_flag = 1

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        print ("P - Connected to %s - Res code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_publish(self, message, topic):
        self._paho_mqtt.publish(topic, message, 2)
        print("Publishing on %s:" % topic)
        print(json.dumps(json.loads(message), indent=2))


class Actuator(object):
    """It reads irrigations information on dynamic catalog and send MQTT
    messages in order to start irrigation.
    If an irrigation has to be postponed, it calls a scheduler which has a
    there that has a countdown.
    """
    def __init__(self, ID, IP, mqtt_port):
        self.pub = MyPublisher(ID, IP, mqtt_port)
        self.pub.start()

    def publish(self, duration, topic):
        message = {
                   "e": [{
                     "n": "irrigate", "d": duration
                        }]
                   }
        self.pub.my_publish(json.dumps(message), topic)

    def irr(self, plantID, devID, h, type, env, url, port):

        # Get dynamic catalog.
        string = "http://" + url + ":" + port + "/dynamic"
        data = json.loads(requests.get(string).text)

        # Get device topic.
        string_dev = "http://" + url + ":" + port + "/info/" + devID
        data_dev = json.loads(requests.get(string_dev).text)
        topic = data_dev["topic"]

        # Find hour modifications.
        # print(plantID)
        for g in data["gardens"]:
            for p in g["plants"]:
                if p["plantID"] == plantID:
                    for ho in p["hours"]:
                        if ho["time"] == h:
                            mod = ho["mod"]
                            modh = ho["modh"]
                            break


        # Reset data about duration and delay on catalog. Next day it will be
        # generated again.
        post_mod(plantID, h, reset=1)

        # If there is no delay: publish via MQTT irrigation and duration.
        if modh == 0:
            if topic != None:
                self.publish(mod, topic)

        # If the irrigation has to be anticipated do the same as before but
        # write on catalog that the next day it has to be anticipated.
        elif modh < 0:
            if topic != None:
                self.publish(mod, topic)

            new_h = delay_h(h, modh)
            print(new_h)
            post_mod(plantID, h, static=1, new_hour=new_h)

        # If there is a delay: start thread with a countdown and then publish.
        elif modh > 0:
            thr = ThreadScheduler(devID.replace('d_', ''), devID + "_sch",
                                  modh, self.pub, mod, topic)
            thr.start()



class ThreadScheduler(threading.Thread):
    """Thread to schedule posticipated irrigations. It has a countdown to do
    that.
    """
    def __init__(self, ThreadID, name, delay, pub, mod, topic):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name
        self.delay = delay
        self.publisher = pub
        self.mod = mod
        self.topic = topic
        self.pub = pub

    def run(self):
        print("Thread status: Waiting %d seconds" % self.delay)
        time.sleep(self.delay)
        self.publish(self.mod, self.topic)

    def publish(self, duration, topic):
        message = {
                   "e": [{
                     "n": "irrigate", "d": duration
                        }]
                   }
        self.pub.my_publish(json.dumps(message), topic)


def delay_h(h, delta):
    """Takes as inputs an hour in format "XX:XX" and a number of seconds which
    has to be added. Returns the delayed hour in format "XX:XX".
    """
    h = datetime.datetime.strptime(h, '%H:%M')
    h = h + datetime.timedelta(seconds=delta)
    h = format(h, '%H:%M')
    return h


class Plant(threading.Thread):
    def __init__(self, ThreadID, name, list, IP, mqtt_port):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        self.list = list
        self.IP = IP
        self.mqtt_port = mqtt_port

    def run(self):
        sch = Actuator('my_ID', self.IP, self.mqtt_port)

        # Create schedules.
        (c_url, c_port, garden_id) = read_file(FILE1)
        for p in self.list:
            pID = p["plantID"]
            env = p["environment"]
            for h in p["hours"]:
                t = delay_h(h["time"], -600)
                ty = h["type"]
                for d in p["devices"]:
                    for r in d["resources"]:
                        res = r["n"]
                        if res == 'rain':
                            print("Schedule: %s - %s - %s" % (t, pID, res))
                            schedule.every().day.at(t).do(rain, pID, t, ty, env)
                        if res == 'light':
                            print("Schedule: %s - %s - %s" % (t, pID, res))
                            schedule.every().day.at(t).do(light, pID, t, ty, env)
                        if res == 'wind':
                            print("Schedule: %s - %s - %s" % (t, pID, res))
                            schedule.every().day.at(t).do(wind, pID, t, ty, env)
                        if res == 'humidity':
                            print("Schedule: %s - %s - %s" % (t, pID, res))
                            schedule.every().day.at(t).do(hum, pID, t, ty, env)
                        if res == 'temperature':
                            print("Schedule: %s - %s - %s" % (t, pID, res))
                            schedule.every().day.at(t).do(temp, pID, t, ty, env)
                        if res == 'irrigation':
                            devID = d["devID"]
                            # print("Schedule: %s - %s - %s" % (h["time"], pID, res))
                            # schedule.every().day.at(t).do(sch.irr, pID, devID, h["time"], ty, env)

                            TIME = '16:00'
                            print("Schedule: %s - %s - %s" % (TIME, pID, res))
                            schedule.every().day.at(TIME).do(sch.irr, pID, devID, h["time"], ty, env, c_url, c_port)


        # Check schedules every 30 seconds.
        while True:
            schedule.run_pending()
            # time.sleep(30)
            time.sleep(3)


        # To do later:
        # if 'light' in self.resources:
        #     sec = light_control.get_result()
        #     h = datetime.datetime.strptime(self.hours, '%H:%M')
        #     h = h + datetime.timedelta(seconds=sec)
        #     h = format(h, '%H:%M')
        #     print(h)


class UpdateList(threading.Thread):
    """Updates global list of plants every day. If the list is the same as
    before, it does not update it.
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name

    def run(self):
        global plant_list
        while True:
            new_list = []
            url, port, gardenID = read_file(FILE1)
            string = "http://" + url + ":" + port + "/static"
            data = json.loads(requests.get(string).text)

            string2 = "http://" + url + ":" + port + "/broker"
            broker_info = json.loads(requests.get(string2).text)
            broker_ip = broker_info["IP"]
            mqtt_port = broker_info["mqtt_port"]

            for g in data["gardens"]:
                if g["gardenID"] == gardenID:
                    for p in g["plants"]:
                        new_list.append(p)

            if plant_list != new_list:
                plant_list = new_list
                print("Thread status: updated plant list!")

                # Stop thread.
                try:
                    planter.stop()
                except:
                    pass

                # (Re)start thread.
                planter = Plant(101, "Planter", new_list, broker_ip, mqtt_port)
                planter.start()

            else:
                print("Thread status: list is up to date.")
                planter.stop()
                planter.start()

            time.sleep(86400)


def main():
    upd = UpdateList(1, "UpdateList")
    upd.start()


if __name__ == '__main__':
    (gardenID, url, port) = read_file(FILE1)
    update_global(url, port)
    main()
