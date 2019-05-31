#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import json
import paho.mqtt.client as PahoMQTT
import time
import datetime

TOPIC = 'smartgarden/+/+/+'

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
        global loop_flag
        print ("Connected to %s - Result code: %d" % (self.messageBroker, rc))
        loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        msg.payload = msg.payload.decode("utf-8")
        message = json.loads(msg.payload)
        # Funzione che ritorna thingspeakID
        #Funzione che associa thingspeakID con writeAPI
        #Funzione che pubblica su Thingspeak (Gennaro)
        

class SubData(threading.Thread):
    """Publish sensor data with MQTT every minute.
    """
    def __init__(self, ThreadID, name):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.url, self.port, self.topic) = updater.read_file("conf.json")
        (self.broker_ip, mqtt_port) = updater.broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)


    def run(self):

        sub = MySubscriber("Thingspeak", self.topic, self.broker_ip,
                          int(self.mqtt_port))
        loop_flag = 1
        sub.start()

        while loop_flag:
            print("Waiting for connection...")
            time.sleep(.01)

        while True:
            time.sleep(5)

        sub.stop()
        # sub.start()
        # # pub2 = MyPublisher(self.devID + '_2', self.topic[1], self.broker_ip,
        #                   # int(self.mqtt_port))
        # # pub2.start()
        #
        # while pub.loop_flag:
        #     print("Waiting for connection...")
        #     time.sleep(1)
        #
        # while True:
        #     data = get_data(self.devID, self.resources)
        #     pub.my_publish(json.dumps(data))
        #     # pub2.my_publish(json.dumps(temp))
        #     time.sleep(60)
        #
        # sub.stop()


if __name__ == "__main__":
