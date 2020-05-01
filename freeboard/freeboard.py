#!/usr/bin/env python3
"""Freeboard on CherryPy.
- Edit freeboard configuration
- Save the configuration
- Reload the page
"""
import json
import cherrypy
from pathlib import Path

P = Path(__file__).parent.absolute()


class Index(object):
    """Index page."""

    exposed = True

    def GET(self):
        """Return index page in HTML."""
        return open(P / "freeboard/index.html", "r").read()


class SaveDashboard(object):
    """Add SaveDashboard page to save dashboard."""

    exposed = True

    def POST(self, *uri, **params):
        """Save dashboard configuration on json."""
        dash_json = json.loads(params["json_string"])  # Load json object
        with open(P / "freeboard/dashboard/dashboard.json", "w") as f:
            json.dump(dash_json, f)  # Write json to file


if __name__ == '__main__':

    conf = {'/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': P / '/'
            },
            '/css': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': P / 'freeboard/css'
            },
            '/dashboard': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': P / 'freeboard/dashboard'
            },
            '/img': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': P / 'freeboard/img'
            },
            '/js': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': P / 'freeboard/js'
            },
            '/plugins': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': P / 'freeboard/plugins'
            },
            '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': P / 'freeboard'
            }
            }

    cherrypy.tree.mount(Index(), '/', config=conf)
    cherrypy.tree.mount(SaveDashboard(), '/saveDashboard', config=conf)
    cherrypy.config.update(str(P / 'conf'))
    cherrypy.engine.start()
    cherrypy.engine.block()
