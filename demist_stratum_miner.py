from stratum_helper import Stratum_chatter
from miner import Miner


if __name__ == "__main__":
    stratum_chatter = Stratum_chatter("solo.ckpool.org", 3333, "1PKN98VN2z5gwSGZvGKS2bj8aADZBkyhkZ", "x")
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
