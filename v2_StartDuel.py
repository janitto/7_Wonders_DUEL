import seven_wonders_utils
import random
import logging
import json
import os
from DUEL_Network import Network


def generate_game_id():
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    randomstring = ''
    # generates 6-character random string. change 6 to whatever you want
    for i in range(0, 6):
        randomstring += random.choice(characters)
    return randomstring

hra_id = generate_game_id()
#hra_id = "YRX7DP"

logging.basicConfig(filename=f'logs/gamelog_{hra_id}.log',
                    filemode='a',
                    format='%(levelname)s: %(funcName)s() at line %(lineno)d: %(message)s',
                    level=logging.DEBUG)

net = Network(hrac="Jan", hra_id=hra_id)
seven_wonders_utils.net = net


metadata = net.get()
vek = metadata["vek"]

if vek == 1:
    prvy_vek = seven_wonders_utils.SevenWondersPrvyVek(hra_id)
    druhy_vek = seven_wonders_utils.SevenWondersDruhyVek(hra_id)
    treti_vek = seven_wonders_utils.SevenWondersTretiVek(hra_id)
elif vek == 2:
    druhy_vek = seven_wonders_utils.SevenWondersDruhyVek(hra_id)
    treti_vek = seven_wonders_utils.SevenWondersTretiVek(hra_id)
elif vek == 3:
    treti_vek = seven_wonders_utils.SevenWondersTretiVek(hra_id)
else:
    logging.error(f"Vek {vek} nie je spravny.")



