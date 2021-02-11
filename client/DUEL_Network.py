import socket
import pickle
import logging
import time

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
        return self.client.recv(4096).decode()

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            reply = self.client.recv(9999)
            #print("from 1st SEND", len(reply))
            try:
                reply = pickle.loads(reply)
            except:
                additional_reply = self.client.recv(9999)
                #print("from 2nd SEND", len(additional_reply))
                reply += additional_reply
                #print("whole SEND", len(reply))
                reply = pickle.loads(reply)
            return reply
        except socket.error as e:
            return str(e)

    def get(self):
        try:
            self.client.send(pickle.dumps("get"))
            reply = self.client.recv(9999)
            # print("from 1st GET", len(reply))
            try:
                reply = pickle.loads(reply)
            except:
                additional_reply = self.client.recv(9999)
                # print("from 2nd GET", len(additional_reply))
                reply += additional_reply
                # print("whole GET", len(reply))
                reply = pickle.loads(reply)
            return reply
        except socket.error as e:
            return str(e)

    def recv_timeout(self, the_socket):
        all_data = []
        while True:
            data = the_socket.recv(9999)
            print(data)
            if not data:
                break
            else:
                all_data.append(data)
        return "".join(data)