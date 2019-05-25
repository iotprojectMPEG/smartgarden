#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script lets you change all IPs in json files.
"""
import json
import sys, os


def update_json(filename, key, value):

    with open(filename, 'r') as fr:
        data = json.loads(fr.read())

    data[key] = value

    with open(filename, 'w') as fw:
        json.dump(data, fw, indent=2)


def main():
    ip = input("Type catalog IP followed by [Enter]:\n")
    update_json("./thingspeak/conf.json", "catalogURL", ip)
    update_json("./telegram-bot/conf.json", "catalogURL", ip)
    update_json("./sensors/conf.json", "catalogURL", ip)
    update_json("./sensors/dht11/conf.json", "catalogURL", ip)
    update_json("./sensors/irrigator/conf.json", "catalogURL", ip)
    update_json("./sensors/light/conf.json", "catalogURL", ip)
    update_json("./sensors/rain/conf.json", "catalogURL", ip)
    update_json("./sensors/wind/conf.json", "catalogURL", ip)

    print("Success!")


if __name__ == '__main__':
    main()
