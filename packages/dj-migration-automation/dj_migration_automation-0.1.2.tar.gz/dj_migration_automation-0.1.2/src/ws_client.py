# -*- coding: utf-8 -*-
"""
    src.ws_client
    ~~~~~~~~~~~~~~~~

    Python client for connecting to the web socket.

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""

import asyncio
import websockets


async def hello():
    async with websockets.connect('ws://localhost:5678' + '/robot') as websocket:
        greeting = await websocket.recv()
        print("< {}".format(greeting))

asyncio.get_event_loop().run_until_complete(hello())