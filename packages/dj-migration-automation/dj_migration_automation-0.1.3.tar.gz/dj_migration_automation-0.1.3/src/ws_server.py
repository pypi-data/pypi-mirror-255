# -*- coding: utf-8 -*-
"""
    src.ws_server
    ~~~~~~~~~~~~~~~~

    Websocket server and handlers associated with the websoscket.

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""

import asyncio
import datetime
import random
import websockets


async def time(websocket, path):
    if path == '/robot':
        while True:
            now = datetime.datetime.now().isoformat() + 'Z'
            await websocket.send(now)
            await asyncio.sleep(random.random() * 3)


start_server = websockets.serve(time, '127.0.0.1', 5678)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
