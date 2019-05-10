#!/usr/bin/env python3
import random
import string
import cherrypy
import requests
import json
import os

CONF_FILE = 'conf.json'


class Data(object):

    def __init__(self):
        return

    #this gets the list
    def get_lists(self):
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        string = config["URL"] + ":" + config["port"] + "/static" # Genera URL per GET
        data = json.loads(requests.get(string).text)  # GET per ottenere il catalog
        list_gar = [g["name"] for g in data["gardens"]] # Generates list of gardens
        #list_pla = [p["name"] for p in data["plants"]]  # Generates list of plants
        #list_dev = [d["name"] for d in data["devices"]] # Generates list of devices

class HTML(object):

    #this is the index page
    exposed = True
    def GET(self, *uri):
        if uri[0] == 'index':
            return open('index.html')

    #function to add the garden
    #exposed=True
    #def addgard(self):
        if uri[0] == 'AddGarden':
            return open('Add Garden.html')

    exposed=True
    def posting_gard(self, name=None, location=None):
        new_garden = {"name": name, "location": location}
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        cat_url = config["URL"] + ":" + config["port"] + "/addg"
        return requests.post(cat_url, json.dumps(new_garden))

    #function to add the plant
    exposed=True
    def addplant(self):
        return open('Add Plant.html')
    exposed=True
    def posting_plant(self, garden=None, name=None):
        new_plant = {"garden": garden, "plant": name}
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        cat_url = config["URL"] + ":" + config["port"] + "/addp"
        return requests.post(cat_url, json.dumps(new_plant))

    #function to add a device
    exposed=True
    def adddev(self):
        return open('Add Device.html')
    exposed = True
    def posting_dev(self, name=None, location=None):
        new_garden = {"name": name, "location": location}
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        cat_url = config["URL"] + ":" + config["port"] + "/addd"
        return requests.post(cat_url, json.dumps(new_garden))


if __name__ == '__main__':
    conf  = {'/':
         {
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher()
         },
            '/assets':
        {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : os.path.abspath(os.path.join(os.path.dirname(__file__), './assets'))
        }
    }
    #cherrypy.tree.mount(Data(), '/', config=conf)
    cherrypy.tree.mount(HTML(), '/', config=conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
