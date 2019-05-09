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
        #return open('index.html')
        risposta = requests.get(".....").text()

        test = "Ciao"
        return """<html>

        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>The Smart Garden</title>
            <link rel="stylesheet" href="assets/bootstrap/css/bootstrap.min.css">
            <link rel="stylesheet" href="assets/fonts/font-awesome.min.css">
            <link rel="stylesheet" href="assets/fonts/ionicons.min.css">
            <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Abel">
            <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Dosis">
            <link rel="stylesheet" href="assets/css/Footer-Clean.css">
            <link rel="stylesheet" href="assets/css/Footer-Dark.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/3.5.2/animate.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/aos/2.1.1/aos.css">
            <link rel="stylesheet" href="assets/css/styles.css">
        </head>

        <body>
            <div data-bs-parallax-bg="true" style="height:583px;background-image:url(&quot;assets/img/3840x2160-5238361-plant-pot-minimal-minimalist-white-green-windowsill-window-vibrant-succulent-space-nature-minimalistic-house-home-gardening-garden-flower-decoration-copy-free-stock-photos.jpg&quot;);background-position:center;background-size:cover;margin:0;margin-right:-258px;">
                <nav class="navbar navbar-light navbar-expand-md" data-bs-hover-animate="bounce" style="width:280px;">
                    <div class="container-fluid"><a class="navbar-brand" href="index.html" data-aos="fade" data-aos-duration="950" data-aos-delay="500" style="font-size:29px;letter-spacing:-1px;font-family:Dosis, sans-serif;width:903px;height:86px;margin:-4px;padding:5px;"><img src="assets/img/cactus.svg" id="cac">Smart Gardening</a>
                        <button
                            class="navbar-toggler" data-toggle="collapse" data-target="#navcol-1"></button>
                            <div class="collapse navbar-collapse" id="navcol-1"></div>
                    </div>
                </nav>
                <h1 class="text-left" data-aos="fade" data-aos-duration="3000" data-aos-delay="700" style="height:53px;margin:41px;">Your <strong>Green</strong> thumb, <strong>everywhere</strong></h1>
                <div class="col-md-12" style="width:675px;height:268px;padding:93px;margin:-41px;padding-top:36px;">
                    <div class="btn-group" role="group"><a class="btn btn-light btn-lg" role="button" href="Add Garden.html" data-aos="fade" data-aos-duration="1000" data-aos-delay="700" style="background-color:#F1B34D;width:458px;margin-top:18px;margin-bottom:36px;margin-left:36px;"><i class="fa fa-home"></i>&nbsp;Add a new garden</a></div>
                    <a
                        class="btn btn-light btn-lg" role="button" href="Add Plant.html" data-aos="fade" data-aos-duration="1000" data-aos-delay="850" id="bt2" style="background-color:#F1B34D;width:458px;margin-top:-8px;margin-bottom:36px;margin-left:36px;"><i class="fa fa-leaf"></i>&nbsp;""" + test +"""</a><a class="btn btn-light btn-lg" role="button" href="Add Device.html" data-aos="fade" data-aos-duration="800" data-aos-delay="1100" id="bt2" style="background-color:#F1B34D;width:458px;margin-top:-8px;margin-bottom:36px;margin-left:36px;"><i class="fa fa-wrench"></i>&nbsp;Add a new device</a></div>
            </div>
            <div class="footer-dark" style="height:292px;margin:0px;">
                <footer>
                    <div class="container">
                        <div class="row">
                            <div class="col-sm-6 col-md-3 item">
                                <h3>Services</h3>
                                <ul>
                                    <li><a href="#">Web design</a></li>
                                    <li><a href="#">Development</a></li>
                                    <li><a href="#">Hosting</a></li>
                                </ul>
                            </div>
                            <div class="col-sm-6 col-md-3 item">
                                <h3>About</h3>
                                <ul>
                                    <li><a href="#">Company</a></li>
                                    <li><a href="#">Team</a></li>
                                    <li><a href="#">Careers</a></li>
                                </ul>
                            </div>
                            <div class="col-md-6 item text">
                                <h3>The Smart Garden - ICT for Smart Societies</h3>
                                <p>We certainly know that nobody will read these lines, so we can say all the fuck we want. Politecnico di Torino is a nice university, but shit you won't find a place to study even paying some bitch around the hallways.</p>
                            </div>
                            <div class="col item social"><a href="#"><i class="icon ion-social-facebook"></i></a><a href="#"><i class="icon ion-social-twitter"></i></a><a href="#"><i class="icon ion-social-snapchat"></i></a><a href="#"><i class="icon ion-social-instagram"></i></a></div>
                        </div>
                        <p class="copyright">Smart Garden © 2019</p>
                    </div>
                </footer>
            </div>
            <script src="assets/js/jquery.min.js"></script>
            <script src="assets/bootstrap/js/bootstrap.min.js"></script>
            <script src="assets/js/bs-animation.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/aos/2.1.1/aos.js"></script>
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
