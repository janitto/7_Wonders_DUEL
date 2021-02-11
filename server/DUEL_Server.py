import socket
from _thread import *
import pickle
import json
import glob
import random

#   vytvor TCP server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = '0.0.0.0'
port = 5555
server_ip = socket.gethostbyname(server)
try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen()
print("Cakam na hracov.")

pocet_hracov = 0
metadata = {}

def threaded_client(conn, addr):
    global pocet_hracov, metadata
    data = conn.recv(4096)
    pocet_hracov += 1
    meno = data.decode("utf-8").split(":")[1]
    hra_id = data.decode("utf-8").split(":")[0]
    welcome_message = f"Ahoj {meno}, vitaj v hre {hra_id}. Tvoje cislo je:{pocet_hracov}"
    print("Hrac", meno, "sa pripojil k hre", hra_id, "z adresy", addr, "ako hrac", pocet_hracov)
    conn.send(str.encode(welcome_message))

    open_games = []
    for game in glob.glob("archiv_hier/input_metadata_??????.json"):
        open_games.append(game[27:33])

    print("Open games", open_games)
    if hra_id in open_games:
        print(f"Hra {hra_id} exituje. Obnovujem...")
        with open(f"archiv_hier/input_metadata_{hra_id}.json") as m:
            metadata = json.load(m)

            if pocet_hracov == 1:
                metadata["hraci_mena"][0] = meno
                metadata["hraci_mena"][1] = "?"
            else:
                metadata["hraci_mena"][1] = meno

    else:
        print(f"Hra {hra_id} je nova.")
        if pocet_hracov == 1:
            with open("meta/default_metadata.json") as m:
                metadata = json.load(m)
                metadata["hraci_mena"][0] = meno
                metadata["hraci_mena"][1] = "?"
        elif pocet_hracov == 2:
            metadata["hraci_mena"][1] = meno
            #   hru zacina nahodny hrac
            nahodny_hrac = random.randrange(2)
            metadata["naposledy_hral"] = metadata["hraci_mena"][nahodny_hrac]
        else:
            pass

    while True:
        try:
            data = conn.recv(9999)
            data = pickle.loads(data)
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                if data != "get":
                    print("Updatujem metadata na:", data)
                    metadata = json.loads(data)
                    # vytvor metadatovy subor na servri.
                    with open(f"archiv_hier/input_metadata_{hra_id}.json", 'w') as f:
                        json.dump(metadata, f, indent=2)
                    reply = pickle.dumps(metadata)
                else:
                    reply = pickle.dumps(metadata)
            print("Odosielam bajty pre", meno, len(reply))
            conn.sendall(reply)
        except:
            break

# cakam na prveho hraca
while True:
    conn, addr = s.accept()
    if pocet_hracov <= 2:  start_new_thread(threaded_client, (conn, addr))
    else: print("Hru uz hraju 2 hraci.")