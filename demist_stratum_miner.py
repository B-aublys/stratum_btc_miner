from stratum_helper import Stratum_chatter
from miner import Miner
from config import *

if __name__ == "__main__":
    stratum_chatter = Stratum_chatter(POOL_ADDR, POOL_PORT, WORKER_NAME, WORKER_PASS)
    sending_queue, data_queue = stratum_chatter.start()

    miner = Miner(sending_queue, data_queue)
    miner.start()


    while True:
        try:
            input("-------------- [CTR + C] to quit ---------------\n")
        except KeyboardInterrupt:
            stratum_chatter.kill()
            miner.kill()
            break
