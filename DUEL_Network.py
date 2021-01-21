import socket
import pickle
import logging

class Network:

    def __init__(self, hrac, hra_id):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "192.168.0.105"
        self.port = 5555
        self.addr = (self.host, self.port)
        self.hrac = hrac
        self.hra_id = hra_id
        welcome_message = self.connect()
        self.poradove_cislo = welcome_message.split(":")[1]
        logging.info(welcome_message)


    def connect(self):
        self.client.connect(self.addr)
        self.client.send(str.encode(f"{self.hra_id}:{self.hrac}"))
        return self.client.recv(2048).decode()

    def send(self, data):
        try:
            self.client.send(pickle.dumps(f"{data}"))
            reply = self.client.recv(2048)
            reply = pickle.loads(reply)
            return reply
        except socket.error as e:
            return str(e)

    def get(self):
        try:
            self.client.send(pickle.dumps("get"))
            reply = self.client.recv(2048)
            reply = pickle.loads(reply)
            return reply
        except socket.error as e:
            return str(e)