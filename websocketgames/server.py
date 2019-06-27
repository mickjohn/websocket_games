import random

class CodeGenerator():

    MAX_CODE = 456975  # i.e 456975 == zzzz
    MIN_CODE = 17576  # i.e baaa
    MODULUS = 97  # Games will be identified by their modulus. Modulus of 97 allows 97 differnt game types
    BASE = 26
    DIGITS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    GAME_MODULUS_TABLE = {
        'RedOrBlack': 1,
    }

    def generate_code(self, mod):
        lower = self.MIN_CODE + self.MODULUS
        higher = self.MAX_CODE - self.MODULUS + 1
        code = random.randint(lower, higher)
        code = code - (code % self.MODULUS)
        code += mod
        # return code
        return self._convert_to_code(code)

    def _convert_to_code(self, code):
        temp_code = code
        converted_code = []
        index = 1
        while(True):
            index += 1
            mod = temp_code % self.BASE
            converted_code.append(self.DIGITS[mod])
            temp_code = temp_code // self.BASE
            if temp_code == 0:
                break
        converted_code.reverse()
        return ''.join(converted_code)


if __name__ == '__main__':
    gen = CodeGenerator()
    # print(gen._convert_to_code(25))
    # print(gen._convert_to_code(26))
    # print(gen._convert_to_code(456976))
    # print(gen._convert_to_code(456975))
    # print(gen._convert_to_code(17576))

    for x in range(0,10):
        print(gen.generate_code(1))
