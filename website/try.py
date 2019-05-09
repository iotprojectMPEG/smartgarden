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
    def GET(self):
        return open('index.html')

    #function to add the garden
    @cherrypy.expose
    def addgard(self):
        return """<html>
          <head></head>
          <body>
            <h2>ADD GARDEN</h2>
            <form method="get" action="posting_gard" target="_self">
              Name:<br>
              <input type="text" name="name" value="">
              <br>
              Location:<br>
              <input type="text" name="location" value="">
              <br><br>
              <input type="submit" value="Submit">
            </form>
          </body>
        </html>"""
    @cherrypy.expose
    def posting_gard(self, name=None, location=None):
        new_garden = {"name": name, "location": location}
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        cat_url = config["URL"] + ":" + config["port"] + "/addg"
        return requests.post(cat_url, json.dumps(new_garden))

    #function to add the plant
    @cherrypy.expose
    def addplant(self):
        return """<html>
          <head></head>
          <body>
            <h2>ADD PLANT</h2>
            <form method="get" action="posting_plant" target="_self">
            Select Garden:<br>
              <select name="garden">
                <option value="fiat">fiat</option>
                <option value=""></option>
                <option value=""></option>
                <option value=""></option>
              </select>
              <br>
              Name:<br>
              <input type="text" name="name" value="">
              <br>
              <br><br>
              <input type="submit">
            </form>
          </body>
        </html>"""
    @cherrypy.expose
    def posting_plant(self, garden=None, name=None):
        new_plant = {"garden": garden, "plant": name}
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        cat_url = config["URL"] + ":" + config["port"] + "/addp"
        return requests.post(cat_url, json.dumps(new_plant))

    #function to add a device
    @cherrypy.expose
    def adddev(self):
        return """<html>
          <head></head>
          <body>
            <h2>ADD DEVICE</h2>
            <form method="get" action="posting_dev" target="_self">
              Select Garden:<br>
                <select name="garden">
                    <option value=""></option>
                    <option value=""></option>
                    <option value=""></option>
                    <option value=""></option>
                </select>
                <br>
              Select Plant:<br>
                <select name="garden">
                    <option value=""></option>
                    <option value=""></option>
                    <option value=""></option>
                    <option value=""></option>
              </select>
              <br>
              Name:<br>
              <input type="text" name="name" value="">
              <br>
              Resources:<br>
              <input type="text" name="location" value="">
              <br>
              Endpoints:<br>
              <input type="text" name="name" value="">
              <br>
              <input type="submit" value="Submit">
            </form>
          </body>
        </html>"""
    @cherrypy.expose
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

    cherrypy.tree.mount(HTML(), '/', config=conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
