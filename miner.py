from utils import Mining_data
from queue import Empty as QueueEmpty
from multiprocessing import Process, Queue, Event
import random
import hashlib
import binascii
from config import *
import signal

import time
import logging

logging.basicConfig(level=logging.INFO)

# TODO: Make the mining threads close when an multirpocess event happens :)

class Miner:
    def __init__(self, send_queue: Queue, receive_queue: Queue):
        self.send_queue = send_queue
        self.receive_queue = receive_queue
        self.mining_processes = []
        self.miner_queues = []
        self.reading_process = None
        self.mine_data = None
        self.number_of_processes = NUMBER_OF_THREADS
        self.exit_event = Event()


    # TODO: handle closing :)
    def start_mining(self):
        signal.signal(signal.SIGINT, self.kill)

        # NOTE: might need to be switched to non-blocking
        new_miners = []

        for i in range(NUMBER_OF_THREADS):
            self.miner_queues.append(Queue())
            new_miner = Process(target=self.mine_coin, args=[self.miner_queues[-1]])
            new_miner.start()
            new_miners.append(new_miner)

        self.mining_processes = new_miners

        while not self.exit_event.is_set():
            try:
                self.mine_data: Mining_data = self.receive_queue.get(False)
            except QueueEmpty:
                continue

            # TODO: when new data is gotten send it to the miners :D
            for queue in self.miner_queues:
                queue.put(self.mine_data)

    # TODO: I know could be optimised by moving some stuff out, but this is python anyways xDDD
    def mine_coin(self, data_queue: Queue):
        signal.signal(signal.SIGINT, lambda a, b: None)

        while not self.exit_event.is_set():
            try:
                mine_data = data_queue.get(False)
            except QueueEmpty:
                pass

            if mine_data.job_ID:
                target = (mine_data.nBits[2 :] + '00' * (int(mine_data.nBits[:2] , 16) - 3)).zfill(64)
                adjusted_target = hex(int(target, 16)*mine_data.difficulty)[2:].zfill(64)
                extranonce2 = hex(random.randint(0 , 2 ** 32 - 1))[2 :].zfill(2 * mine_data.extranonce2_zise)

                coinbase = mine_data.gen_tranx_1 + mine_data.extranonce1 + extranonce2 + mine_data.gen_tranx_2
                coinbase_hash_bin = hashlib.sha256(hashlib.sha256(binascii.unhexlify(coinbase)).digest()).digest()

                merkle_root = coinbase_hash_bin
                for h in mine_data.merkle_branches:
                    merkle_root = hashlib.sha256(hashlib.sha256(merkle_root + binascii.unhexlify(h)).digest()).digest()

                merkle_root = binascii.hexlify(merkle_root).decode()

                # little endian
                merkle_root = ''.join([merkle_root[i] + merkle_root[i + 1] for i in range(0 , len(merkle_root) , 2)][: :-1])

                while not self.exit_event.is_set() and data_queue.empty():
                    nonce = hex(random.randint(0 , 2 ** 32 - 1))[2 :].zfill(8)  # nNonce   #hex(int(nonce,16)+1)[2:]
                    blockheader = mine_data.btc_block_version + \
                                mine_data.prev_HASH + \
                                merkle_root + \
                                mine_data.nTime + \
                                mine_data.nBits + \
                                nonce + \
                                '000000800000000000000000000000000000000000000000000000000000000000000000000000000000000080020000'

                    hashy = hashlib.sha256(hashlib.sha256(binascii.unhexlify(blockheader)).digest()).digest()
                    hashy = binascii.hexlify(hashy).decode()


                    if hashy < adjusted_target:
                        self.submit_found(nonce, extranonce2)

    def submit_found(self, nonce, extranonce2):
        # TODO: make the stratum helper handle IDs
        self.send_queue.put({"id":666 ,
                            'method':'mining.submit',
                            'params': [WORKER_NAME, self.mine_data.job_ID, extranonce2, self.mine_data.nTime, nonce]})

    def start(self):
        reading_p = Process(target=self.start_mining)
        reading_p.start()
        # TODO: join this process in the main code
        self.reading_process = reading_p

    def kill(self, signal, frame):
        self.exit_event.set()
        for process in self.mining_processes:
                process.join()