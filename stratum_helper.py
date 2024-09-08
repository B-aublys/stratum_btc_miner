import socket
import json
import logging
import sys

from utils import *

class stratum_chatter():
    def __init__(self, pool_address: str, pool_port: int, worker_name:str, worker_pass:str):
        self.pool_address = pool_address
        self.pool_port = pool_port
        self.worker_name = worker_name
        self.worker_pass = worker_pass
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.count = 0

    def connect_to_pool(self):
        try:
            self.sock.connect((self.pool_address, self.pool_port))
        except socket.error as e:
            logging.error(f"Connecting to the pool <{self.pool_address}:{self.pool_port}>: {e}")
            sys.exit()

    def send_message(self, message:object):
        message_json = json.dumps(message) + '\n'

        try:
            self.sock.sendall(message_json.encode('utf-8'))
        except socket.error as e:
            logging.error(f"Sending message to the pool: {e}")
            sys.exit()

    def receive_message(self):
        try:
            response = self.sock.recv(2056).decode('utf-8')
        except InterruptedError:
            raise InterruptedError
        responses = list(filter(None, response.split('\n')))

        if len(response) == 0:
            logging.error("The pool disconnected while waiting for a message")
            sys.exit()

        for response in responses:
            # TODO: handle all the responsese
            print(json.loads(response))


    def subscribe_to_pool(self):
        subscribe_message = {
        "id": 1,
        "method": "mining.subscribe",
        "params": []
        }

        self.send_message(subscribe_message)
        return self.receive_message()

    def authorize_worker(self):
        authorize_message = {
        "id": 2,
        "method": "mining.authorize",
        "params": [self.worker_name, self.worker_pass]
        }

        self.send_message(authorize_message)
        return self.receive_message()

    def start_operation(self):
        self.connect_to_pool()
        recv = self.subscribe_to_pool()
        recv = self.authorize_worker()

        while True:
            try:
                self.receive_message()
            except InterruptedError:
                self.sock.close()




if __name__ == "__main__":
    chatter = stratum_chatter("solo.ckpool.org", 3333, "1PKN98VN2z5gwSGZvGKS2bj8aADZBkyhkZ", "x")
    chatter.start_operation()