from utils import Mining_data
from queue import Empty as QueueEmpty
from multiprocessing import Process, Queue, Event, Pipe
import random
import hashlib
import binascii
from config import *
import signal

import time
import logging

logging.basicConfig(level=logging.INFO)

class Miner:
    def __init__(self, send_queue: Queue, receive_queue: Queue):
        self.send_queue = send_queue
        self.receive_queue = receive_queue
        self.mining_processes = []
        self.miner_pipes = []
        self.miner_stop_events = []
        self.reading_process = None
        self.mine_data = None
        self.number_of_processes = NUMBER_OF_THREADS
        self.stop_manager_thread = False


    def start_mining(self):
        signal.signal(signal.SIGINT, self.kill)
        new_miners = []

        for i in range(NUMBER_OF_THREADS):
            self.miner_pipes.append(Pipe())
            self.miner_stop_events.append(Event())
            new_miner = Process(target=self.mine_coin, args=[self.miner_pipes[-1], self.miner_stop_events[-1]])
            new_miner.start()
            new_miners.append(new_miner)

        self.mining_processes = new_miners

        old_time = time.time()

        while not self.stop_manager_thread:
            try:
                self.mine_data: Mining_data = self.receive_queue.get(False)
            except QueueEmpty:
                continue

            for pipes in self.miner_pipes:
                pipes[0].send(self.mine_data)

            sumi = 0
            new_time = time.time()

            # NOTE: the poll function with a timeout would block the execution...
            # Sleep doesn't seem to block it...
            time.sleep(1)
            for pipes in self.miner_pipes:
                if pipes[0].poll():
                    sumi += pipes[0].recv() / (new_time + 0.000001 - old_time)

            old_time = new_time
            self.print_hashrate(sumi)



    def mine_coin(self, data_pipes, stop_event):
        signal.signal(signal.SIGINT, lambda a, b: None)

        iteration = 0
        while not stop_event.is_set():

            if data_pipes[1].poll():
                mine_data = data_pipes[1].recv()
                data_pipes[1].send(iteration)
                iteration = 0
            else:
                continue
            
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

                while not stop_event.is_set() and not data_pipes[1].poll():
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

                    iteration += 1


    def print_hashrate(self, hashrate):
        print(f"The \033[38;2;110;5;196mWizard's\033[0m 🧙‍♂️ current power level: [ \033[38;2;18;228;78m{hashrate/1000000:.2f} GH/s\033[0m ]")

    def submit_found(self, nonce, extranonce2):
        self.send_queue.put({"id":666 ,
                            'method':'mining.submit',
                            'params': [WORKER_NAME, self.mine_data.job_ID, extranonce2, self.mine_data.nTime, nonce]})

    def start(self):
        reading_p = Process(target=self.start_mining)
        reading_p.start()
        # TODO: join this process in the main code
        self.reading_process = reading_p

    def kill(self, signal, frame):
        for event in self.miner_stop_events:
            event.set()

        self.stop_manager_thread = True

        for process in self.mining_processes:
                process.join()