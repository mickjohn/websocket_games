from websocketgames.games.clients import Client, ClientRegistery
from websocketgames.games.players import Player, PlayerRegistery
import asyncio
import logging
import uuid

logger = logging.getLogger('websocketgames')

class TurnBasedGame():

    def __init__(self, game_code, cleanup_handler=None):
        self.game_code = game_code
        self.p_reg = PlayerRegistery()
        self.c_reg = ClientRegistery()
        self.cleanup_handler = cleanup_handler

    async def _cleanup(self):
        await asyncio.sleep(30)
        self.cleanup_handler(self.game_code)

    async def start_cleanup_task(self):
        logger.debug("running cleanup")
        if self.cleanup_handler != None:
            task = asyncio.create_task(self._cleanup())
            self.cleanup_task = task

    # async def handle_message(self, json_dict, websocket):
    #     if json_dict['type'] == 'Debug':
    #         self._debug()
    #         return
    #     validator.validate_msg(json_dict)
    #     message = json_dict
    #     msg_type = json_dict['type']

    #     if msg_type == 'Register':
    #         await self.register_player(websocket, message)
    #     elif msg_type == 'Activate':
    #         await self.activate_player(websocket, message)
    #     elif msg_type == 'StartGame':
    #         await self.start_game(websocket, message)
    #     elif msg_type == 'PlayTurn':
    #         await self.play_turn(websocket, message)

    async def register_player(self, websocket, msg):
        '''
        Create a player, but don't add to the game. 'activate_player' must be
        called afterwards to enable the player. This does not add a new client
        '''
        username = msg['username']
        new_player = Player(username, str(uuid.uuid4()), False)

        if self.p_reg.uname_exists(username):
            err_msg = f"User {username} already registered in {self.game_code}"
            logger.error(err_msg)
            await utils.send_message(
                websocket,
                'Error',
                error_type="UserAlreadyRegistered",
                error=f"User with name {username} already registered in game"
            )
            return None

        logger.info(f"Registering player {username} in game {self.game_code}")
        self.p_reg.add_player(new_player)
        await utils.send_message(websocket, 'Registered', user_id=new_player.user_id)
        return new_player

    async def activate_player(self, websocket, msg):
        '''
        Activate a registered Player
        '''
        user_id = msg['user_id']
        if user_id not in self.p_reg.id_map:
            await utils.send_message(
                websocket,
                'Error',
                error=f"User with id {user_id} does not exist in game {self.game_code}"
            )
            return None

        logger.info(f"Activating player {user_id} in game {self.game_code}")

        if user_id in self.inactive_player_ids:
            self.inactive_player_ids.remove(user_id)

        player = self.p_reg.id_map[user_id]
        player.active = True

        # If game was set to be removed, cancel the task
        if self.cleanup_task != None:
            logger.debug('cancelling cleanup')
            self.cleanup_task.cancel()

        if self.owner == None:
            self.owner = player

        self.c_reg.connect(websocket, player)

        await utils.broadcast_message(
            self.c_reg.websockets(),
            'PlayerAdded',
            player=player,
            skip=[websocket]
        )

        await utils.broadcast_message(
            self.c_reg.websockets(),
            'OrderChanged',
            order=self.p_reg.get_order()
        )

        await utils.send_message(
            websocket,
            'YouJoined',
            player=player,
            game_state=self.get_full_game_state(),
        )

        return player