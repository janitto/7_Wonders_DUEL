import socket
from _thread import *
import pickle
import json

#   vytvor TCP server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = '127.0.0.1'
port = 5555
server_ip = socket.gethostbyname(server)
try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))
s.listen()
print("Cakam na hracov.")

hraci = []

#   ziskaj prvotne metadata
with open("meta/default_metadata.json") as metadata:
    metadata = json.load(metadata)


def threaded_client(conn, addr):
    global hraci, metadata
    data = conn.recv(2048)
    meno = data.decode("utf-8").split(":")[1]
    hra_id = data.decode("utf-8").split(":")[0]
    hraci.append(meno)
    welcome_message = f"Ahoj {meno}, vitaj v hre {hra_id}"
    print("Hrac", meno, "sa pripojil k hre z adresy", addr)
    conn.send(str.encode(welcome_message))
    while True:
        try:
            data = conn.recv(2048)
            data = pickle.loads(data)
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                if data != "get":
                    print("Updatujem metadata na:", data)
                    metadata = data
                    reply = pickle.dumps(metadata)
                else:
                    print("Ziskavam metadata", metadata)
                    reply = pickle.dumps(metadata)
            conn.sendall(reply)
        except:
            break


while True:
    conn, addr = s.accept()
    start_new_thread(threaded_client, (conn, addr))