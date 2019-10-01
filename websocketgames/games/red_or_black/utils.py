import jsonpickle

SENSITIVE = [
    'user_id'
]


def remove_sensitive_info_from_message(msg):
    '''
    If broadcasting a message to all clients it's a good idea to remove the
    user ID from the message, since it's only needed by the one user
    '''
    keys_to_remove = []
    for k, v in msg.items():
        if k in SENSITIVE:
            keys_to_remove.append(k)
        if isinstance(v, dict):
            remove_sensitive_info_from_message(v)

    for k in keys_to_remove:
        del(msg[k])


async def send_message(websocket, msg_type, **kwargs):
    msg = {
        'type': msg_type,
        **kwargs
    }

    # Convert dict to json
    json_msg = jsonpickle.encode(msg, unpicklable=False)

    # Convert back to dict. This ensures that every object in the dict is made
    # of basic types (aka json types)
    dict_msg = jsonpickle.decode(json_msg)
    if 'broadcast' in dict_msg and dict_msg['broadcast']:
        remove_sensitive_info_from_message(dict_msg)

    # Convert the back to json
    await websocket.send(jsonpickle.encode(dict_msg, unpicklable=False))

async def broadcast_message(websockets, msg_type, skip=[], **kwargs):
    for websocket in websockets:
        if websocket.open and websocket not in skip:
            await send_message(websocket, msg_type, **kwargs, broadcast=True)