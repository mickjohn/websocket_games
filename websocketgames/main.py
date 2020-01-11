import logging
import websockets
import asyncio
import coloredlogs

from websocketgames.server import WebsocketServer

# Configure Logger
handler = logging.StreamHandler()
logger = logging.getLogger('websocketgames')
logger.addHandler(handler)
fmt = '%(asctime)s %(name)s:%(module)s %(message)s'
coloredlogs.install(logger=logger, level='DEBUG', fmt=fmt)


logger.info('Starting server')
server = WebsocketServer()
start_server = websockets.serve(server.handle_message, "0.0.0.0", 9000)

try:
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    logger.info("Shutting down server")
