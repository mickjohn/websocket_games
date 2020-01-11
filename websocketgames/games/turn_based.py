import asyncio
import logging
import uuid

from websocketgames.games.clients import ClientRegistery
from websocketgames.games.players import Player, PlayerRegistery
from websocketgames.games.red_or_black import utils

from collections import defaultdict

logger = logging.getLogger('websocketgames')


class TurnBasedGame():

    def __init__(self, game_code, cleanup_handler=None, timeout_seconds=30):
        self.game_code = game_code
        self.p_reg = PlayerRegistery()
        self.c_reg = ClientRegistery()
        self.timeout_seconds = timeout_seconds
        self.cleanup_handler = cleanup_handler
        self.owner = None
        self.inactive_player_ids = set()
        self.inactive_player_counter = defaultdict(int)

    async def _cleanup(self):
        '''
        Sleep for 30 seconds (in case someone joins), and then call the cleanup
        callback
        '''
        await asyncio.sleep(self.timeout_seconds)
        self.cleanup_handler(self.game_code)

    async def start_cleanup_task(self):
        logger.debug("running cleanup")
        if self.cleanup_handler is not None:
            task = asyncio.create_task(self._cleanup())
            self.cleanup_task = task

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

    async def handle_close(self, websocket):
        '''
        Handle the close of a websocket of an active client, and send out
        messages of the new state. The playing order will change, the owner
        could change.
        '''
        if websocket not in self.c_reg.clients:
            return
        logger.debug("Handling websocket disconnection")
        client = self.c_reg.clients[websocket]
        if client and client.player:
            player = client.player
            self.p_reg.deactivate(player)

            if self.p_reg.all_inactive():
                logger.debug("All players inactive, calling cleanup")
                await self.start_cleanup_task()

            self.c_reg.remove(websocket)
            resp = []

            # Send msg that player has disconnected
            resp.append({
                'type': 'PlayerDisconnected',
                'player': player,
            })

            if self.owner.user_id == player.user_id:
                if len(self.p_reg.get_order()):
                    new_owner = self.p_reg.get_order()[0]
                else:
                    new_owner = None
                self.owner = new_owner
                # Inform players that there is a new owner
                resp.append({
                    'type': 'NewOwner',
                    'owner': new_owner,
                })

            # The game order will have changed
            resp.append({
                'type': 'OrderChanged',
                'order': self.p_reg.get_order()
            })

            for msg in resp:
                await utils.broadcast_message(
                    self.c_reg.websockets(),
                    msg['type'],
                    **msg,
                )
        await websocket.close()

    async def activate_player(self, websocket, msg):
        '''
        Activate a registered Player and broadcast two messages, a
        'PlayerAdded' message, and a 'OrderChanged' message. Returns the player
        that was added.
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
        if self.cleanup_task is not None:
            logger.debug('cancelling cleanup')
            self.cleanup_task.cancel()

        if self.owner is None:
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
        return player
