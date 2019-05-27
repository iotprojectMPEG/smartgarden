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

    print("Changing files:")
    update_json("./thingspeak/conf.json", "catalogURL", ip)
    update_json("./telegram-bot/conf.json", "catalogURL", ip)
    update_json("./sensors/conf.json", "catalogURL", ip)
    update_json("./sensors/dht11/conf.json", "catalogURL", ip)
    update_json("./sensors/irrigator/conf.json", "catalogURL", ip)
    update_json("./sensors/light/conf.json", "catalogURL", ip)
    update_json("./sensors/rain/conf.json", "catalogURL", ip)
    update_json("./sensors/wind/conf.json", "catalogURL", ip)
    update_json("./catalog/conf.json", "catalogURL", ip)
    update_cherrypy("./catalog/cherrypyconf", "server.socket_host", ip)


    update_broker("./catalog/static.json", "IP", ip2)

    print("Success!")


if __name__ == '__main__':
    main()
