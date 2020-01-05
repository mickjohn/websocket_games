import jsonpickle
from enum import auto, Enum
from websocketgames.json_enum_handler import JsonEnumHandler


class GameStates(Enum):
    LOBBY = auto()
    PLAYING = auto()
    FINISHED = auto()

    def __str__(self):
        if self == self.LOBBY:
            return 'LOBBY'
        elif self == self.PLAYING:
            return 'PLAYING'
        elif self.FINISHED:
            return 'FINISHED'
        return ''

    def __repr__(self):
        return str(self)


# Use custom JSON handler for GameStates
jsonpickle.handlers.registry.register(GameStates, JsonEnumHandler)
