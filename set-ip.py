#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script lets you change all IPs in json files."""
import json
from pathlib import Path
import os

P = Path(__file__).parent.absolute()


def update_cherrypy(filename, key, value):
    """Update cherrypy config file with new value."""
    print(filename)
    filename = str(filename)
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
    """Update json files with new values."""
    print(filename)

    with open(filename, 'r') as fr:
        data = json.loads(fr.read())

    for c, key in enumerate(keys):
        data[key] = values[c]

    with open(filename, 'w') as fw:
        json.dump(data, fw, indent=2)
        fw.write("\n")


def update_broker(filename, key, value):
    """Update json files with new broker values."""
    print(filename)

    with open(filename, 'r') as fr:
        data = json.loads(fr.read())

    data["broker"][key] = value

    with open(filename, 'w') as fw:
        json.dump(data, fw, indent=2)
        fw.write("\n")


def update_ts(filename, key, value):
    """Update json files with new TS values."""
    print(filename)

    with open(filename, 'r') as fr:
        data = json.loads(fr.read())

    data["thingspeak"][key] = value

    with open(filename, 'w') as fw:
        json.dump(data, fw, indent=2)
        fw.write("\n")


def main():
    """Update all configuration files."""
    cat_ip = input("Type catalog IP followed by [Enter]:\n")
    cat_port = input("Type catalog port followed by [Enter]:\n")
    ts_ip = input("Type ThingSpeak adaptor IP followed by [Enter]:\n")
    ts_port = input("Type ThingSpeak adaptor port followed by [Enter]:\n")
    fre_ip = input("Type freeboard IP followed by [Enter]:\n")
    fre_port = input("Type freeboard port followed by [Enter]:\n")
    mqtt_ip = input("Type MQTT broker IP followed by [Enter]:\n")
    telegram_token = input("Type the Telegram token followed by [Enter]:\n")

    print("Changing files:")
    # Base files.
    update_json(P / "catalog/conf.json", ["cat_ip", "cat_port"],
                                         [cat_ip, cat_port])
    update_ts(P / "catalog/static.json", "IP", ts_ip)
    update_ts(P / "catalog/static.json", "port", ts_port)
    update_broker(P / "catalog/static.json", "IP", mqtt_ip)
    update_json(P / "thingspeak/conf.json", ["cat_ip", "cat_port"],
                                            [cat_ip, cat_port])
    update_json(P / "telegram-bot/conf.json", ["cat_ip", "cat_port"],
                                              [cat_ip, cat_port])
    update_json(P / "catalog/api.json", ["telegramtoken"], [telegram_token])
    update_json(P / "interface/conf.json", ["cat_ip", "cat_port"],
                                           [cat_ip, cat_port])

    # Sensors.
    for sub in os.walk(P / 'sensors'):
        for f in sub[2]:
            if f.endswith('.json'):
                j = Path(sub[0]) / f
                update_json(j, ["cat_ip", "cat_port"], [cat_ip, cat_port])

    # Control strategies.
    for sub in os.walk(P / 'control'):
        for f in sub[2]:
            if f.endswith('.json'):
                j = Path(sub[0]) / f
                update_json(j, ["cat_ip", "cat_port"], [cat_ip, cat_port])

    # CherryPi
    update_cherrypy(P / "catalog/cherrypyconf", "server.socket_host", cat_ip)
    update_cherrypy(P / "freeboard/conf", "server.socket_host", fre_ip)
    update_cherrypy(P / "thingspeak/cherrypyconf", "server.socket_host", ts_ip)
    update_cherrypy(P / "catalog/cherrypyconf", "server.socket_port",
                    int(cat_port))
    update_cherrypy(P / "freeboard/conf", "server.socket_port", int(fre_port))
    update_cherrypy(P / "thingspeak/cherrypyconf", "server.socket_port",
                    int(ts_port))
    print("Success!")


if __name__ == '__main__':
    main()
