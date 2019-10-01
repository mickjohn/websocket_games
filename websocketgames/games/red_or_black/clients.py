import logging

logger = logging.getLogger('websocketgames')


class Client:

    def __init__(self, websocket, player=None):
        self.websocket = websocket
        self.player = player

    def __eq__(self, other):
        if isinstance(other, Client):
            return self.__dict__ == other.__dict__
        return False


class ClientRegistery:
    '''
    Each client can control exactly one player. Clients are identified by
    their websocket connection.
    '''

    def __init__(self):
        self.clients = {}

    def connect(self, websocket, player):
        client = Client(websocket, player)
        self.clients[websocket] = client

    def remove(self, websocket):
        if websocket in self.clients:
            del(self.clients[websocket])

    def websockets(self):
        if len(self.clients):
            return list(self.clients.keys())
        else:
            return []
