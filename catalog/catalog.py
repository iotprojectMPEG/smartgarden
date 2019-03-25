#!/usr/bin/env python3

import json
import cherrypy
import time
import datetime
import requests
import threading

JSON_FILE = 'static.json'
CONF_FILE = 'conf'

class Catalog(object):
    def __init__(self, filename):
        self.filename = filename

    def load_file(self):
        with open(self.filename, "r") as f:
            self.data = json.loads(f.read())

class Webserver(object):
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        catalog = Catalog(JSON_FILE)
        catalog.load_file()
        return catalog.data


def main():
    cherrypy.tree.mount(Webserver(), '/catalog', config=CONF_FILE)
    cherrypy.config.update('conf')
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    main()
