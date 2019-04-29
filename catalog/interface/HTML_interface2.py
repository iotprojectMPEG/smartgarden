#!/usr/bin/env python3
import random
import string
import cherrypy
import requests
import json

CONF_FILE = 'conf.json'

class Adder(object):

    @cherrypy.expose
    def addgard(self):
        return """<html>
          <head></head>
          <body>
            <h2>ADD GARDEN</h2>
            <form method="get" action="posting" target="_blank">
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
    def posting(self, name=None, location=None):
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
            <form method="get" action="posting" target="_blank">
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
    def posting(self, name=None, location=None):
        new_garden = {"name": name, "location": location}
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        cat_url = config["URL"] + ":" + config["port"] + "/addg"
        return requests.post(cat_url, json.dumps(new_garden))


    @cherrypy.expose
    def adddev(self):
        return """<html>
          <head></head>
          <body>
            <h2>ADD DEVICE</h2>
            <form method="get" action="posting" target="_blank">
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
    def posting(self, name=None, location=None):
        new_garden = {"name": name, "location": location}
        file = open(CONF_FILE, 'r')
        config = json.load(file)
        file.close()
        cat_url = config["URL"] + ":" + config["port"] + "/addg"
        return requests.post(cat_url, json.dumps(new_garden))


    # @cherrypy.expose
    # def index2(self):
    #     return """<html>
    #       <head></head>
    #       <body>
    #         <form method="get" action="generate">
    #           <input type="text" value="8" name="length" />
    #           <button type="submit">Give it now!</button>
    #         </form>
    #       </body>
    #     </html>"""
    #
    #
    # @cherrypy.expose
    # def generate(self, length=8):
    #     return ''.join(random.sample(string.hexdigits, int(length)))


if __name__ == '__main__':
    cherrypy.quickstart(Adder())
