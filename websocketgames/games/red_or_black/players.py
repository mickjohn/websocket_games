from collections import OrderedDict


class Player():

    def __init__(self, username, user_id, active=True):
        self.username = username
        self.user_id = user_id
        self.active = active

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.__dict__ == other.__dict__
        return False


class PlayerRegistery():

    def __init__(self):
        self.id_map = OrderedDict()
        self.uname_map = OrderedDict()

    def __str__(self):
        return str(self.__dict__)

    def add_player(self, player):
        self.id_map[player.user_id] = player
        self.uname_map[player.username] = player

    def remove(self, player):
        del(self.id_map[player.user_id])
        del(self.uname_map[player.username])

    def deactivate(self, player):
        player.active = False
        self.id_map.move_to_end(player.user_id)
        self.uname_map.move_to_end(player.username)

    def uname_exists(self, uname):
        for p in list(self.id_map.values()):
            if p.username == uname:
                return True
        return False

    def get_order(self):
        return [p for p in list(self.id_map.values()) if p.active]

    def all_inactive(self):
        for (__id, player) in self.id_map.items():
            if player.active == True:
                return False
        return True
