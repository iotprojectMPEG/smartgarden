#!/usr/bin/env python3
import random
import string
import cherrypy
import requests
import json

CONF_FILE = 'conf.json'


class Data(object):
    #this gets the list
    def get_list_gardens(self):
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        string = config["URL"] + ":" + config["port"] + "/static" # Genera URL per GET
        data = json.loads(requests.get(string).text)  # GET per ottenere il catalog
        list = [g["name"] for g in data["gardens"]]  # Genera lista di giardini


class HTML(object):
    #this is the index page
    @cherrypy.expose
    def index(self):
        return """<html>
          <head></head>
          <body>
            <h2>WELCOME TO THE SMART GARDEN</h2>
            <p>Choose one of the following options:</p>
              <form method="get" action="addgard" target="_self">
                <button type="submit">Add Garden</button>
              </form>
              <form method="get" action="addplant" target="_self">
                <button type="submit">Add Plant</button>
              </form>
              <form method="get" action="adddev" target="_self">
                <button type="submit">Add Device</button>
              </form>
          </body>
        </html>"""



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
                <option value=""></option>
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
    def posting_plant(self, name=None, location=None):
        new_garden = {"name": name, "location": location}
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        cat_url = config["URL"] + ":" + config["port"] + "/addp"
        return requests.post(cat_url, json.dumps(new_garden))

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

    #Data().get_list_gardens()
    cherrypy.quickstart(HTML())
