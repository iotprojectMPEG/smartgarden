#!/usr/bin/env python3
import random
import string
import cherrypy
import requests
import json

CONF_FILE = 'conf.json'

class Adder(object):

    @cherrypy.expose
    def index(self):
        return """<html>
          <head></head>
          <body>
            <h2>WELCOME TO THE SMART GARDEN</h2>
            <p>Choose one of the following options:</p>
            <form method="get" action="posting" target="_blank">
              <button type="button" onclick="alert('Hello World!')">Click Me!</button>
            </form>
          </body>
        </html>"""


    @cherrypy.expose
    def addgard(self):
        return """<html>
          <head></head>
          <body>
            <h2>ADD GARDEN</h2>
            <form method="get" action="posting_gard" target="_blank">
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


    @cherrypy.expose
    #look here to understand: https://www.w3schools.com/html/tryit.asp?filename=tryhtml_elem_select
    def addplant(self):
        return """<html>
          <head></head>
          <body>
            <h2>ADD PLANT</h2>
            <form method="get" action="posting_plant" target="_blank">
            Select Garden:<br>
              <select name="garden">
                <option value=""></option>
                <option value=""></option>
                <option value=""></option>
                <option value=""></option>
              </select>
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


    @cherrypy.expose
    def adddev(self):
        return """<html>
          <head></head>
          <body>
            <h2>ADD DEVICE</h2>
            <form method="get" action="posting_dev" target="_blank">
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
    def posting_dev(self, name=None, location=None):
        new_garden = {"name": name, "location": location}
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        cat_url = config["URL"] + ":" + config["port"] + "/addd"
        return requests.post(cat_url, json.dumps(new_garden))



if __name__ == '__main__':
    cherrypy.quickstart(Adder())
