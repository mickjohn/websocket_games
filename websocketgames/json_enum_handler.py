import jsonpickle
from enum import Enum

class JsonEnumHandler(jsonpickle.handlers.BaseHandler):

    def restore(self, obj):
        pass

    def flatten(self, obj: Enum, data):
        return obj.name
