#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script lets you change all IPs in json files.
"""
import json
import sys, os


def update_cherrypy(filename, key, value):
    """Update cherrypy config file with new value
    """
    print(filename)

    with open(filename, 'r') as fr:
        data = fr.readlines()

    string = str(key) + ": '" + str(value) + "'\n"

    for cnt, line in enumerate(data):
        if line.find(key) != -1:
            break

    data[cnt] = string

    with open(filename, 'w') as fw:
         fw.writelines(data)


def update_json(filename, key, value):
    """Update json files with new value
    """
    print(filename)

    with open(filename, 'r') as fr:
        data = json.loads(fr.read())

    data[key] = value

    with open(filename, 'w') as fw:
        json.dump(data, fw, indent=2)

def update_broker(filename, key, value):
    print(filename)

    with open(filename, 'r') as fr:
        data = json.loads(fr.read())

    data["broker"][key] = value

    with open(filename, 'w') as fw:
        json.dump(data, fw, indent=2)

def main():
    ip = input("Type catalog IP followed by [Enter]:\n")
    ip2 = input("Type MQTT broker IP followed by [Enter]:\n")
    ip3 = input("Type the Telegram token followed by [Enter]:\n")

    print("Changing files:")
    # Base files.
    update_json("./catalog/conf.json", "catalogURL", ip)
    update_json("./thingspeak/conf.json", "catalogURL", ip)
    update_json("./telegram-bot/conf.json", "catalogURL", ip)
    update_json("./catalog/api.json", "telegramtoken", ip3)

    # Sensors.
    update_json("./sensors/conf.json", "catalogURL", ip)
    update_json("./sensors/dht11/conf.json", "catalogURL", ip)
    update_json("./sensors/dht11-sim/conf.json", "catalogURL", ip)
    update_json("./sensors/dht11-sim2/conf.json", "catalogURL", ip)
    update_json("./sensors/irrigator-sim/conf.json", "catalogURL", ip)
    update_json("./sensors/light-sim/conf.json", "catalogURL", ip)
    update_json("./sensors/rain-sim/conf.json", "catalogURL", ip)
    update_json("./sensors/wind-sim/conf.json", "catalogURL", ip)

    # Control strategies.
    update_json("./control/plant1/hum.json", "catalogURL", ip)
    update_json("./control/plant1/temp.json", "catalogURL", ip)
    update_json("./control/plant1/wind.json", "catalogURL", ip)
    update_json("./control/plant2/hum.json", "catalogURL", ip)
    update_json("./control/plant2/temp.json", "catalogURL", ip)
    update_json("./control/plant2/light.json", "catalogURL", ip)

    # CherryPi
    update_cherrypy("./catalog/cherrypyconf", "server.socket_host", ip)
    update_cherrypy("./freeboard/conf", "server.socket_host", ip)



    update_broker("./catalog/static.json", "IP", ip2)

    print("Success!")


if __name__ == '__main__':
    main()
