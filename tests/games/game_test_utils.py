from websocketgames.games import utils

import jsonpickle
from pytest import fixture


class MockWebsocket():
    def __init__(self):
        self.message_stack = []
        self.broadcast_stack = []
        self.open = True

    async def send(self, s):
        # decode message to check if it's a broadcast message or not
        msg_dict = jsonpickle.decode(s)
        if 'broadcast' in msg_dict and msg_dict['broadcast']:
            self.broadcast_stack.append(s)
        else:
            self.message_stack.append(s)

    async def close(self):
        self.open = False


@fixture
def mock_utils_send(monkeypatch):
    class MockUtils():
        def __init__(self):
            self.msgs = []
            self.broadcast = []

        async def send_message(self, ws, msg_type, **kwargs):
            msg = jsonpickle.encode(
                {'type': msg_type, **kwargs},
                unpicklable=False
            )
            self.msgs.append(jsonpickle.decode(msg))

        async def broadcast_message(self, ws, msg_type, skip=[], **kwargs):
            json_msg = jsonpickle.encode(
                {'type': msg_type, **kwargs},
                unpicklable=False
            )
            msg = jsonpickle.decode(json_msg)
            utils.remove_sensitive_info_from_message(msg)
            self.broadcast.append(msg)

        def __repr__(self):
            return (
                f"msgs = {self.msgs}\n"
                f"broadcast = {self.broadcast}\n"
            )

    mock_utils = MockUtils()
    monkeypatch.setattr(
        'websocketgames.games.utils.send_message',
        mock_utils.send_message,
    )
    monkeypatch.setattr(
        'websocketgames.games.utils.broadcast_message',
        mock_utils.broadcast_message,
    )
    return mock_utils
