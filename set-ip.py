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

    if isinstance(value, int):
        string = str(key) + ": " + str(value) + "\n"
    else:
        string = str(key) + ": '" + str(value) + "'\n"

    for cnt, line in enumerate(data):
        if line.find(key) != -1:
            break

    data[cnt] = string

    with open(filename, 'w') as fw:
         fw.writelines(data)


def update_json(filename, keys, values):
    """Update json files with new value."""
    print(filename)

    with open(filename, 'r') as fr:
        data = json.loads(fr.read())

    for c, key in enumerate(keys):
        data[key] = values[c]

    with open(filename, 'w') as fw:
        json.dump(data, fw, indent=2)

def update_broker(filename, key, value):
    print(filename)

    with open(filename, 'r') as fr:
        data = json.loads(fr.read())

    data["broker"][key] = value

    with open(filename, 'w') as fw:
        json.dump(data, fw, indent=2)

def update_ts(filename, key, value):
    print(filename)

    with open(filename, 'r') as fr:
        data = json.loads(fr.read())

    data["thingspeak"][key] = value

    with open(filename, 'w') as fw:
        json.dump(data, fw, indent=2)

def main():
    cat_ip = input("Type catalog IP followed by [Enter]:\n")
    cat_port = input("Type catalog port followed by [Enter]:\n")
    mqtt_ip = input("Type MQTT broker IP followed by [Enter]:\n")
    telegram_token = input("Type the Telegram token followed by [Enter]:\n")
    ts_ip = input("Type ThingSpeak adaptor IP followed by [Enter]:\n")
    ts_port = input("Type ThingSpeak adaptor port followed by [Enter]:\n")

    print("Changing files:")
    # Base files.
    update_json("./catalog/conf.json", ["cat_ip", "cat_port"],
                                       [cat_ip, cat_port])
    update_ts("./catalog/static.json", "IP", ts_ip)
    update_ts("./catalog/static.json", "port", ts_port)
    update_broker("./catalog/static.json", "IP", mqtt_ip)
    update_json("./thingspeak/conf.json", ["cat_ip", "cat_port"],
                                          [cat_ip, cat_port])
    update_json("./telegram-bot/conf.json", ["cat_ip", "cat_port"],
                                            [cat_ip, cat_port])
    update_json("./catalog/api.json", ["telegramtoken"], [telegram_token])

    # Sensors.
    update_json("./sensors/conf.json", ["cat_ip", "cat_port"],
                                       [cat_ip, cat_port])
    update_json("./sensors/dht11/conf.json", ["cat_ip", "cat_port"],
                                             [cat_ip, cat_port])
    update_json("./sensors/dht11-sim/conf.json", ["cat_ip", "cat_port"],
                                                 [cat_ip, cat_port])
    update_json("./sensors/dht11-sim2/conf.json", ["cat_ip", "cat_port"],
                                                  [cat_ip, cat_port])
    update_json("./sensors/irrigator-sim/conf.json", ["cat_ip", "cat_port"],
                                                     [cat_ip, cat_port])
    update_json("./sensors/light-sim/conf.json", ["cat_ip", "cat_port"],
                                                 [cat_ip, cat_port])
    update_json("./sensors/rain-sim/conf.json", ["cat_ip", "cat_port"],
                                                [cat_ip, cat_port])
    update_json("./sensors/wind-sim/conf.json", ["cat_ip", "cat_port"],
                                                [cat_ip, cat_port])

    # Control strategies.
    update_json("./control/plant1/hum.json", ["cat_ip", "cat_port"],
                                             [cat_ip, cat_port])
    update_json("./control/plant1/temp.json", ["cat_ip", "cat_port"],
                                              [cat_ip, cat_port])
    update_json("./control/plant1/wind.json", ["cat_ip", "cat_port"],
                                              [cat_ip, cat_port])
    update_json("./control/plant2/hum.json", ["cat_ip", "cat_port"],
                                             [cat_ip, cat_port])
    update_json("./control/plant2/temp.json", ["cat_ip", "cat_port"],
                                              [cat_ip, cat_port])
    update_json("./control/plant2/light.json", ["cat_ip", "cat_port"],
                                               [cat_ip, cat_port])

    # CherryPi
    update_cherrypy("./catalog/cherrypyconf", "server.socket_host", cat_ip)
    update_cherrypy("./freeboard/conf", "server.socket_host", cat_ip)
    update_cherrypy("./thingspeak/cherrypyconf", "server.socket_host", ts_ip)
    update_cherrypy("./catalog/cherrypyconf", "server.socket_port",
                    int(cat_port))
    update_cherrypy("./freeboard/conf", "server.socket_port", int(cat_port))
    update_cherrypy("./thingspeak/cherrypyconf", "server.socket_port",
                    int(ts_port))
    print("Success!")


if __name__ == '__main__':
    main()
