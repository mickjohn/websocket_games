import logging
import websockets
import asyncio
import coloredlogs
import argparse

from websocketgames.server import WebsocketServer

parser = argparse.ArgumentParser()
parser.add_argument('--port')
args = parser.parse_args()

# Configure Logger
handler = logging.StreamHandler()
logger = logging.getLogger('websocketgames')
logger.addHandler(handler)
fmt = '%(asctime)s %(name)s:%(module)s %(message)s'
coloredlogs.install(logger=logger, level='DEBUG', fmt=fmt)

if args.port:
    port = args.port
else:
    port = 8080

logger.info(f'Starting server on port {port}')
server = WebsocketServer()
start_server = websockets.serve(server.handle_message, "0.0.0.0", port)

try:
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    logger.info("Shutting down server")
