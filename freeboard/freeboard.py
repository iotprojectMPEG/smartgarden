#!/usr/bin/env python3
"""
@author = Paolo Grasso

- Set 'freeboard' folder path in the conf file
- Visit '0.0.0.0:8080'
- Edit freeboard configuration
- Save the configuration
- Reload the page
"""
import json
import cherrypy
import os

class Index(object):
    exposed = True

    def GET(self):
        return open("./freeboard/index.html", "r").read()

class SaveDashboard(object):
    exposed = True

    def POST(self, *uri, **params):
        dash_json = json.loads(params["json_string"])  # Load json object
        with open("./freeboard/dashboard/dashboard.json", "w") as f:
            json.dump(dash_json, f)  # Write json to file

if __name__ == '__main__':

    conf  = {'/':
         {
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : os.path.abspath(os.path.join(os.path.dirname(__file__), '/'))
         },
            '/css':
        {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : os.path.abspath(os.path.join(os.path.dirname(__file__), './freeboard/css'))
        },
            '/dashboard':
        {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : os.path.abspath(os.path.join(os.path.dirname(__file__), './freeboard/dashboard'))
        },
            '/img':
        {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : os.path.abspath(os.path.join(os.path.dirname(__file__), './freeboard/img'))
        },
            '/js':
        {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : os.path.abspath(os.path.join(os.path.dirname(__file__), './freeboard/js'))
        },
            '/plugins':
        {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : os.path.abspath(os.path.join(os.path.dirname(__file__), './freeboard/plugins'))
        },
            '/static':
        {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : os.path.abspath(os.path.join(os.path.dirname(__file__), './freeboard'))
        }
    }


    cherrypy.tree.mount (Index(), '/', config=conf)
    cherrypy.tree.mount (SaveDashboard(), '/saveDashboard', config=conf)
    cherrypy.config.update('conf')
    cherrypy.engine.start()
    cherrypy.engine.block()
