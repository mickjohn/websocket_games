from websocketgames import code_generator
# import code_generator


class RedOrBlack():

    def __init__(self):
        self.codes = set()
        name = type(self).__name__
        if name not in code_generator.GAME_MODULUS_TABLE:
            raise Exception(f"{name} not registered in GAME_MODULUS_TABLE")
