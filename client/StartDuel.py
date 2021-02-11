import seven_wonders_utils
import random
import logging
from time import sleep
from DUEL_Network import Network
import argparse

def generate_game_id():
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    randomstring = ''
    # generates 6-character random string. change 6 to whatever you want
    for i in range(0, 6):
        randomstring += random.choice(characters)
    return randomstring

parser = argparse.ArgumentParser(description='Potrebne data k hre.')
parser.add_argument('meno', help='Meno hraca', type=str)
parser.add_argument('--hra_id', help='Hra ID', type=str)
args = parser.parse_args()

if args.hra_id is None:
    hra_id = generate_game_id()
else:
    hra_id = args.hra_id
ja_som = args.meno

logging.basicConfig(filename=f'logs/gamelog_{hra_id}_{ja_som}.log',
                    filemode='a',
                    format='%(levelname)s: %(funcName)s() at line %(lineno)d: %(message)s',
                    level=logging.DEBUG)

net = Network(hrac=ja_som, hra_id=hra_id)

while True:
    metadata = net.get()
    print("Cakam na oponenta. Hra ID:", hra_id)
    if "?" not in metadata["hraci_mena"]:
        print("Oponent najdeny. Hra zacina.")
        break
    sleep(5)

vek = metadata["vek"]

if vek == 1:
    prvy_vek = seven_wonders_utils.SevenWondersPrvyVek(net, hra_id, ja_som)
    druhy_vek = seven_wonders_utils.SevenWondersDruhyVek(net, hra_id, ja_som)
    treti_vek = seven_wonders_utils.SevenWondersTretiVek(net, hra_id, ja_som)
elif vek == 2:
    druhy_vek = seven_wonders_utils.SevenWondersDruhyVek(net, hra_id, ja_som)
    treti_vek = seven_wonders_utils.SevenWondersTretiVek(net, hra_id, ja_som)
elif vek == 3:
    treti_vek = seven_wonders_utils.SevenWondersTretiVek(net, hra_id, ja_som)
else:
    logging.error(f"Vek {vek} nie je spravny.")



