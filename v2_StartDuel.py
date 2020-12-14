import seven_wonders_utils
import random
import logging

def generate_game_id():
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    randomstring = ''
    # generates 6-character random string. change 6 to whatever you want
    for i in range(0, 6):
        randomstring += random.choice(characters)
    return randomstring

hra_id = generate_game_id()
hra_id = "8xiFJE"

logging.basicConfig(filename=f'logs/gamelog_{hra_id}.log',
                    filemode='a',
                    format='%(levelname)s: %(funcName)s() at line %(lineno)d: %(message)s',
                    level=logging.INFO)


prvy_vek = seven_wonders_utils.SevenWondersPrvyVek(hra_id)



