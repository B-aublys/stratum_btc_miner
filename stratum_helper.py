import socket
import json
import logging
import sys
import time

from utils import *

from multiprocessing import Process, Queue
# TODO: maybe add support for extra_nonce?
# TODO: lol remove the sys.exit and actually make error handling
# NOTE: the usage of the sending queue for the inicialization sequence is... I don't like it?

class Stratum_chatter():
    def __init__(self, pool_address: str, pool_port: int, worker_name:str, worker_pass:str):
        self.pool_address = pool_address
        self.pool_port = pool_port
        self.worker_name = worker_name
        self.worker_pass = worker_pass
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.count = 0
        self.mining_data = Mining_data()
        self.sending_queue = Queue()

    def connect_to_pool(self):
        try:
            self.sock.connect((self.pool_address, self.pool_port))
        except socket.error as e:
            logging.error(f"Connecting to the pool <{self.pool_address}:{self.pool_port}>: {e}")
            sys.exit()

    def send_messages(self):
        while True:
            message = self.sending_queue.get(True)
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
        self.sending_queue.put({'id':request.get("id"), "result":"tratum_btc_miner/1.0", "error": None })

    def send_show_message(self, request):
        print(f'Incomming message from the server:\n{request.get("params")[0]}')
        self.sending_queue.put({'id': request.get('id'), 'result': None, 'error': None})

    def receive_mining_notif(self, request):
        params = request.get('params')
        self.mining_data = Mining_data(*params, self.mining_data.difficulty)
        self.sending_queue.put({'id': request.get('id'), 'result': None, 'error': None})

    def receive_mining_diff(self, request):
        self.mining_data.difficulty = request.get('params')[0]
        self.sending_queue.put({"id": request.get('id'), 'result': None, 'error': None})

    # NOTE: this only needs to be supported if we tell the server we support it
    def receive_set_extranonce(self, request):
        print("received set_extrannonce!")
        self.sending_queue.put({"id": request.get('id'), 'result': None, 'error': None})


    # TODO: Complete this method ---------------------------------------------------
    def receive_client_reconnect(self, request):
        print("server asked for the client reconnect")
        self.sending_queue.put({"id": request.get('id'), 'result': None, 'error': None})
    # ------------------------------------------------------------------------------

    def subscribe_to_pool(self):
        subscribe_message = {
        "id": 1,
        "method": "mining.subscribe",
        "params": []
        }

        self.sending_queue.put(subscribe_message)
        return self.receive_message()

    def authorize_worker(self):
        authorize_message = {
        "id": 2,
        "method": "mining.authorize",
        "params": [self.worker_name, self.worker_pass]
        }

        self.sending_queue.put(authorize_message)
        return self.receive_message()

    def receive_message_loop(self):
        while True:
            self.receive_message()

    # Returns sending queue
    def start_process(self):
        self.connect_to_pool()
        p_send = Process(target=self.send_messages)
        p_send.start()

        self.subscribe_to_pool()
        time.sleep(2)
        self.authorize_worker()

        p_receive = Process(target=self.receive_message_loop)
        p_receive.start()
        return p_send, p_receive, self.sending_queue

if __name__ == "__main__":
    chatter = Stratum_chatter("solo.ckpool.org", 3333, "1PKN98VN2z5gwSGZvGKS2bj8aADZBkyhkZ", "x")
    chatter.inicialise_pool()