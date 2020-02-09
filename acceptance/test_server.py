from websocketgames import main
from websocketgames.server import WebsocketServer
from pytest_asyncio.plugin import asyncio
import pytest
import websockets
import logging
import coloredlogs
import json

handler = logging.NullHandler()
logger = logging.getLogger('websocketgames')
logger.addHandler(handler)
fmt = '%(asctime)s %(name)s:%(module)s %(message)s'
coloredlogs.install(logger=logger, level='DEBUG', fmt=fmt)

@pytest.mark.asyncio
async def test_invalid_json_message_returned(unused_tcp_port):
    wsg_server = WebsocketServer()
    ws_server = await main.start_server(wsg_server, "localhost", unused_tcp_port)

    request = "gibberish JSON"
    expected = str({"type": "Error", "message": "Invalid JSON"})

    uri = f"ws://localhost:{unused_tcp_port}"
    async with websockets.connect(uri, close_timeout=2) as wbskt_conn:
        await wbskt_conn.send(request)
        response = await wbskt_conn.recv()

    ws_server.close()
    await ws_server.wait_closed()
    assert response == expected


@pytest.mark.asyncio
async def test_can_create_game(unused_tcp_port):
    wsg_server = WebsocketServer()
    ws_server = await main.start_server(wsg_server, "localhost", unused_tcp_port)
    assert len(wsg_server.games) == 0

    request = '{"type": "CreateGame"}'

    # Take the first game type from the websocketserver game list
    game_type = list(wsg_server.game_constructors.keys())[0]

    uri = f"ws://localhost:{unused_tcp_port}/{game_type}"
    async with websockets.connect(uri, close_timeout=2) as wbskt_conn:
        await wbskt_conn.send(request)
        response = await wbskt_conn.recv()
        print(response)

    ws_server.close()
    await ws_server.wait_closed()
    assert len(wsg_server.games) == 1
    game_code = list(wsg_server.games.keys())[0]

    expected = {"type": "GameCreated", "game_code": game_code}
    assert json.loads(response) == expected
