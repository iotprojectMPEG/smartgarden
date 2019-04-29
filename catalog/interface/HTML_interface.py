#!/usr/bin/env python3.7
import random
import string
import cherrypy


class StringGenerator(object):

    @cherrypy.expose
    def index1(self):
        return """<html>
          <head></head>
          <body>

            <h2>ADD GARDEN</h2>

            <form action="generate">
              Name:<br>
              <input type="text" name="Name" value="">
              <br>
              Location:<br>
              <input type="text" name="Location" value="">
              <br><br>
              <input type="submit" value="Submit">
            </form>


           </body>
        </html>"""



    @cherrypy.expose
    def index2(self):
        return """<html>
          <head></head>
          <body>
            <form method="get" action="generate">
              <input type="text" value="8" name="length" />
              <button type="submit">Give it now!</button>
            </form>
          </body>
        </html>"""


    @cherrypy.expose
    def generate(self, length=8):
        return ''.join(random.sample(string.hexdigits, int(length)))


if __name__ == '__main__':
    cherrypy.quickstart(StringGenerator())
