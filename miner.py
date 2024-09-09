from utils import Mining_data
from multiprocessing import Process, Queue, Pool
import random
import hashlib
import binascii
import time


# TODO: create an actual multiprocess management for ending them

class Miner:
    def __init__(self, send_queue: Queue, receive_queue: Queue):
        self.send_queue = send_queue
        self.receive_queue = receive_queue
        self.mining_processes = []
        self.reading_process = None
        self.mine_data = None
        self.number_of_processes = 4

    def start_mining(self):
        while True:
            self.mine_data: Mining_data = self.receive_queue.get(True)
            print("New data")

            if not self.mine_data.job_ID:
                continue

            for process in self.mining_processes:
                process.kill()
                process.join()

            self.mining_processes = []

            new_miners = []
            for i in range(self.number_of_processes):
                new_miner = Process(target=self.mine_coin, args=[self.mine_data])
                new_miner.start()
                new_miners.append(new_miner)

            for m in new_miners:
                self.mining_processes.append(m)


    def mine_coin(self, mine_data: Mining_data):
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

        while True:
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
                print("found it")
                print(hashy)



    def start(self):
        reading_p = Process(target=self.start_mining)
        reading_p.start()
        self.reading_process = reading_p

    def kill(self):
        for process in self.mining_processes:
                process.kill()
                process.join()

        if self.reading_process:
            self.reading_process.kill()
            self.reading_process.join()


