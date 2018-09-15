## Designed for GoPro HERO5

import requests
import time
import argparse

import logging

GOPRO_IP = "10.5.5.9"
UDP_STREAM_IP = "10.5.5.100"
RECORD = False


def init_streaming():
    """
    Initiates streaming on the GoPro camera at the given URL
    """
    did_connect = False
    while not did_connect:
        try:
            response_raw = requests.get(f"http://{GOPRO_IP}/gp/gpControl")
            response_raw.raise_for_status()
            did_connect = True
        except:
            logging.error("Failed to connect to GoPro, retrying...")
            time.sleep(60)
    payload={"p1": "gpStream", "a1": "proto_v2", "c1": "restart"}
    requests.get(f"http://{GOPRO_IP}/gp/gpControl/execute", params=payload)
    if RECORD:
        requests.get(f"http://{GOPRO_IP}/gp/gpControl/command/shutter", params={"p": "1"})
        logging.info(f"Began recording at {GOPRO_IP}")
    logging.info(f"Began streaming at {GOPRO_IP}")

    



if __name__ == "__main__":
    init_streaming()