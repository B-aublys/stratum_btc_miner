import socket
import json
import logging
import sys

from utils import *

# TODO: maybe add support for extra_nonce?


class stratum_chatter():
    def __init__(self, pool_address: str, pool_port: int, worker_name:str, worker_pass:str):
        self.pool_address = pool_address
        self.pool_port = pool_port
        self.worker_name = worker_name
        self.worker_pass = worker_pass
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.count = 0
        self.mining_data = Mining_data()

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
            response = json.loads(response)

            if response.get("method") == "client.get_version":
                self.send_version(response)
            elif response.get("method") == "client.reconnect":
                self.receive_client_reconnect(response)
                pass
            elif response.get("method") == "client.show_message":
                self.send_show_message(response)
                pass
            elif response.get("method") == "mining.notify":
                self.receive_mining_notif(response)
                pass
            elif response.get("method") == "mining.set_difficulty":
                self.receive_mining_diff(response)
                pass
            elif response.get("method") == "mining.set_extranonce":
                self.receive_set_extranonce(response)
                pass

            print(response)

    def send_version(self, request):
        self.send_message({'id':request.get("id"), "result":"tratum_btc_miner/1.0", "error": None })

    def send_show_message(self, request):
        print(f'Incomming message from the server:\n{request.get("params")[0]}')
        self.send_message({'id': request.get('id'), 'result': None, 'error': None})

    def receive_mining_notif(self, request):
        params = request.get('params')
        self.mining_data = Mining_data(*params, self.mining_data.difficulty)
        print("-------------- mining params set ----------------")
        print(self.mining_data)
        print("-------------------------------------------------")
        self.send_message({'id': request.get('id'), 'result': None, 'error': None})

    def receive_mining_diff(self, request):
        self.mining_data.difficulty = request.get('params')[0]
        self.send_message({"id": request.get('id'), 'result': None, 'error': None})

    def receive_set_extranonce(self, request):

        self.send_message({"id": request.get('id'), 'result': None, 'error': None})


    # TODO: Complete this method ---------------------------------------------------
    def receive_client_reconnect(self, request):
        print("server asked for the client reconnect")
        self.send_message({"id": request.get('id'), 'result': None, 'error': None})
    # ------------------------------------------------------------------------------

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