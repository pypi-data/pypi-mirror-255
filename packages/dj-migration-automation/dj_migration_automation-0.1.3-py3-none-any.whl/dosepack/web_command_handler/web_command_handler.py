"""
    web_command_handler
    ~~~~~~~~~~~~~~~~

    This is web command handler object. Conveyor units which requires to provide webservices to
    the other units would be using this object.

    Example:

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""
import inspect
import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
import os
import traceback
import sys
import urllib
import json
from dosepack.error_handling.error_handler import create_response, error
import urllib2
from dosepack.utilities.utils import print_info
from ws4py.websocket import WebSocket
from urlparse import parse_qs
import settings


def notify(channel, msg):
    for conn in settings.channels[channel]:
        try:
            conn.send(msg)
        except Exception as e:
            print(e)


class Publisher(WebSocket):
    def __init__(self, *args, **kw):
        WebSocket.__init__(self, *args, **kw)
        _params = vars(self)['environ']['QUERY_STRING']
        _params = parse_qs(_params)
        try:
            if _params['username'][0] == 'admin' and _params['channel'][0] in settings.channels:
                settings.channels[_params['channel'][0]].add(self)
                print(settings.channels)
            else:
                print('Unauthorized Access')
        except KeyError:
            pass

    def closed(self, code, reason=None):
        print("Remove subscribers from the list.")

    def received_message(self, message):
        "Take action according to message received"
        print(message)


class WebCommandHandler(object):
    """
    Handles all the /api path requests
    """

    def __init__(self, ip, port, index_file):
        print("starting web command handler")
        self.exposed = True
        self.listening_port = port
        self.listening_ip = ip
        self.cherrypy_conf = {}
        self.logs_path = 'logs'
        self.index_file = index_file
        self.enable_cli_simulation = False
        self.setup_cherrypy()
        
    def start_handler(self):
        pass

    def stop_handler(self):
        pass

    def setup_cherrypy(self):
        self.cherrypy_conf = {
            '/': {
                'tools.sessions.on': True,
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.staticdir.dir': './public'
            },
            '/ws': {'tools.websocket.on': True,
                    'tools.websocket.handler_cls': Publisher,
                    'tools.websocket.protocols': ['dp']
                    },

            '/api': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [('Content-Type', 'text/plain')],
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': './public'
            },
        }
        cherrypy.engine.autoreload.match = r'^(?!settings).+'
        cherrypy.engine.subscribe('start', self.start_handler)
        cherrypy.engine.subscribe('stop', self.stop_handler)

    def CORS(self):
        """Allow AngularJS apps not on the same server to use our API
        """
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

    def start(self):
        try:
            webapp = self
            webapp.api = self

            cherrypy.tools.cors = cherrypy.Tool('before_handler', self.CORS)

            cherrypy.config.update({'server.socket_host': self.listening_ip,
                                    'server.socket_port': self.listening_port,
                                    'engine.autoreload_on': False,
                                    'log.screen': True,
                                    'log.access_file': os.path.join(self.logs_path, 'server_access_logs'),
                                    'log.error_file': os.path.join(self.logs_path, 'server_error_logs'),
                                    })

            WebSocketPlugin(cherrypy.engine).subscribe()
            cherrypy.tools.websocket = WebSocketTool()

            # start the cherrypy and block
            cherrypy.quickstart(webapp, "/", self.cherrypy_conf)

        except Exception as ex:
            # no matter what we have to cancel the background thread and exit gracefully
            print_info("error from cherrypy.quickstart()")
            print(ex)
            traceback.format_exception_only(type(ex), ex)        
            error_string = traceback.format_exc()
            print_info("error:" + error_string)
        print_info("program exited.")

    @cherrypy.expose
    def index(self):
        if os.path.isfile(self.index_file):
            webpage = open(self.index_file).read()
            return webpage
        else:
            return self.index_file

    @cherrypy.expose
    def ws(self, **kwargs):
        print(kwargs)

    @cherrypy.expose
    def GET(self, command=None, callback=None, _=None, **kwargs):
        return self.execute(command, callback, _, **kwargs)

    @cherrypy.expose
    def POST(self, command=None, callback=None, _=None, **kwargs):
        return self.execute(command, callback, _, **kwargs)

    def execute(self, command=None, callback=None, _=None, **kwargs):
        try:
            response = "error:no command received"
            if command is not None:
                if len(command) == 0:
                    response = "error:no command received"
                else:
                    print_info("d:command received: %s" % command)
                    args = kwargs

                    # make sure that api is exists
                    if not self.is_api_exists(command):
                        response = error(1000, "Error:command received doesnt exists")
                    else:
                        # execute the api 
                        # get the function handler for the api
                        print("command received is " + command )
                        if self.enable_cli_simulation:
                            response = raw_input("Enter response for cmd " + command + " :>")
                        else:
                            func = self.get_api_func(command)
                            response = str(func(args))
                            if not self.is_json( response ):
                                response = create_response( response )

            else:
                response = "error:no command"

            # to support jsonp handle the callback
            if callback:
                response = callback  + '({response:"' + urllib.quote(response) + '"})'

            print_info("d:response to be sent: %s" % response)
            cherrypy.response.headers['Access-Control-Allow-Origin'] = "*"

        except Exception as ex:
            print("from:RobotCmdWebService::execute()")
            # print out the error
            print(traceback.format_exc())
            print(sys.exc_info()[0])
            traceback.format_exception_only(type(ex), ex)
            response = error(1000, "From:RobotCmdWebService::execute()\nerror:" + str(ex))
            print_info("response:" + response)

        return response 

    def get_api_func(self, api_name):
        all_functions = inspect.getmembers(self,inspect.ismethod)
        apis = [a[1] for a in all_functions if (a[0].startswith('api_' + api_name))]
        return apis[0]

    def api_get_all_apis(self, *args):
        return self.get_all_apis()

    def get_all_apis(self):
        all_functions = inspect.getmembers(self,inspect.ismethod)
        response = [a[0][4:] for a in all_functions if (a[0].startswith('api_'))]
        return response 

    def is_api_exists(self,api_name):
        # print self.get_all_apis()
        return api_name in self.get_all_apis()

    def is_json(self, jsondata):
        try:
            if jsondata[0] == '{':
                jsonvalue = json.loads(jsondata)
            else:
                return False
        except ValueError, e:
            return False
        return True

    def urlopen(self,  url, callback=None,  _=None):
        response = ''
        try:
            # open the request url
            http_get = urllib2.urlopen(url)
            # read the contents of the request
            response = http_get.read()
            # close the connection
            http_get.close()
        except Exception as ex:
            print_info("error:" + str(ex))
        # if callback is present attach response to it.
        if callback is not None:
            response = callback + "(" + response + ")"
        return response
