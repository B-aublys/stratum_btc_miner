from stratum_helper import Stratum_chatter



if __name__ == "__main__":
    stratum_chatter = Stratum_chatter("solo.ckpool.org", 3333, "1PKN98VN2z5gwSGZvGKS2bj8aADZBkyhkZ", "x")
    p_send, p_receive, sending_queue = stratum_chatter.start_process()

    while True:
        try:
            input("-------------- [CTR + C] to quit ---------------\n")
        except KeyboardInterrupt:
            sending_queue.close()
            p_send.kill()
            p_receive.kill()
            break
