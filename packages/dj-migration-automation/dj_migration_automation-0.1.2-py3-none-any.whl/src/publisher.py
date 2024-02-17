import settings
import requests
from ws4py.websocket import WebSocket
from urllib.parse import parse_qs
# from dosepack.utilities.utils import call_webservice


def notify(channel, msg):
    for conn in settings.channels[channel]:
        try:
            conn.send(msg)
        except Exception as e:
            pass

def publish(base_url, pub_url, channel, msg):
    pub_url = pub_url + '?channel=' + channel
    requests.post("http://" + base_url + pub_url, data=msg)


class Publisher(WebSocket):
    def __init__(self, *args, **kw):
        WebSocket.__init__(self, *args, **kw)
        _params = vars(self)['environ']['QUERY_STRING']
        _params = parse_qs(_params)
        if _params['username'][0] == 'admin' and _params['channel'][0] in settings.channels:
            settings.channels[_params['channel'][0]].add(self)
            print(settings.channels)
        else:
            print('Unauthorized Access')

    def closed(self, code, reason=None):
        print("Remove subscribers from the list.")

    def received_message(self, message):
        "Take action according to message received"
        print(message)
