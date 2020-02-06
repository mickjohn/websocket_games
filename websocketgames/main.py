import logging
import websockets
import asyncio
import coloredlogs
import argparse

from websocketgames.server import WebsocketServer


async def start_server(address, port):
    logger.info(f'Starting server on  {address}:{port}')
    server = WebsocketServer()
    return websockets.serve(server.handle_message, "0.0.0.0", args.port)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=8080)
    parser.add_argument('--listen', default="0.0.0.0")
    args = parser.parse_args()

    # Configure Logger
    handler = logging.StreamHandler()
    logger = logging.getLogger('websocketgames')
    logger.addHandler(handler)
    fmt = '%(asctime)s %(name)s:%(module)s %(message)s'
    coloredlogs.install(logger=logger, level='DEBUG', fmt=fmt)

    try:
        asyncio.get_event_loop().run_until_complete(start_server(args.listen, args.port))
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server")
