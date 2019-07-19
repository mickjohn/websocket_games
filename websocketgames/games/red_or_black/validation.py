from websocketgames.games.red_or_black import handler
import logging

ALLOWED_MESSAGES = handler.MESSAGE_TYPES

logger = logging.getLogger(__name__)

# {
#     'game_id': 'aaaa',
#     'data': {...}
# }

# def validate_message(msg):
    # if 'data'

def _validate_basic_fields(msg):
    missing = []
    if 'game_id' not in msg:
        missing.append('game_id')
    if 'data' not in msg:
        missing.append('data')
    if len(missing):
        raise Exception(f'Message is missing {" ".join(missing)}')
    
    if not isinstance(msg['data'], dict):
        raise Exception('data should be an object')

    data = msg['data']
    if 'type' not in msg['data']:
        raise Exception("data['type'] is missing")
    
    msg_type = data['type']
    if msg_type not in ALLOWED_MESSAGES:
        raise Exception(f"Unknown message type '{msg_type}''")
    