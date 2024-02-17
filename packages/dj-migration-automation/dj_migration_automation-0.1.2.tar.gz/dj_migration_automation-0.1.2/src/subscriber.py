from ws4py.client.threadedclient import WebSocketClient


class Subscriber(WebSocketClient):
    def handshake_ok(self):
        self._th.start()
        self._th.join()

    def received_message(self, m):
        print(m)

if __name__ == '__main__':
    ws = Subscriber('ws://127.0.0.1:10008/pubsub/ws?username=admin&channel=canister')
    ws.connect()

