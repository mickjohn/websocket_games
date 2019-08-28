from jsonschema import validate
import logging

logger = logging.getLogger('websocketgames')

ALLOWED_MESSAGES = [
    'AddPlayer',
    'CreateGame',
    'ReaddPlayer',
    'GameStatus',
    'Register',
    'Activate',
    'StartGame',
]

'''
Json schemas for more complicated data structs
'''
schemas = {
    'CreateGame': {
        "type": "object",
        "required": ["type"],
        "additionalProperties": False,
        "properties": {
            "type": {"type": "string"},
        }
    },

    'AddPlayer': {
        "type": "object",
        "required": ["type", "game_id", "username"],
        "additionalProperties": False,
        "properties": {
            "type": {"type": "string"},
            "game_id": {"type": "string"},
            "username": {"type": "string"},
        }
    },

    'Register': {
        "type": "object",
        "required": ["type", "username", "game_id"],
        "additionalProperties": False,
        "properties": {
            "type": {"type": "string"},
            "username": {"type": "string"},
            "game_id": {"type": "string"},
        }
    },

    'Activate': {
        "type": "object",
        "required": ["type", "user_id", "game_id"],
        "additionalProperties": False,
        "properties": {
            "type": {"type": "string"},
            "user_id": {"type": "string"},
            "game_id": {"type": "string"},
        }
    },

    'StartGame': {
        "type": "object",
        "required": ["type", "user_id", "game_id"],
        "additionalProperties": False,
        "properties": {
            "type": {"type": "string"},
            "user_id": {"type": "string"},
            "game_id": {"type": "string"},
        }
    },    
}


def validate_msg(json_dict):
    if 'type' not in json_dict:
        raise Exception("Field 'type' is missing")

    if json_dict['type'] not in ALLOWED_MESSAGES:
        raise Exception(f"Unknown message type '{json_dict['type']}'")

    validate(json_dict, schemas[json_dict['type']])
    return True
