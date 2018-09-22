## Designed for GoPro HERO5

import subprocess
import requests
import time
import argparse
import signal
import logging
import socket
import sys

parser = argparse.ArgumentParser(description="UDP video streaming options.")
parser.add_argument("--ip", help="The IP address of the GoPro", default="10.5.5.9")
parser.add_argument("--port", help="The UDP port of the GoPro stream", default=8554)
parser.add_argument("--stream-ip", help="The IP address of the GoPro stream", default="10.5.5.100")
parser.add_argument("--record", help="Record the stream to the GoPro.", action="store_true")

args = parser.parse_args()
print(args)


# Keep alive message
MESSAGE = bytes("_GPHD_:0:0:2:0.000000\n", "utf-8")
KEEP_ALIVE_PERIOD = 2.5

GOPRO_IP = args.ip
PORT = args.port
UDP_STREAM_IP = args.stream_ip
RECORD = args.record


def init_streaming():
    """
    Initiates streaming on the GoPro camera at the given URL
    """
    did_connect = False
    while not did_connect:
        try: # Attempt to get the status of the GoPro to determine whether we're connected
            response_raw = requests.get(f"http://{GOPRO_IP}/gp/gpControl")
            response_raw.raise_for_status()
            did_connect = True
        except:
            logging.error("Failed to connect to GoPro, retrying...")
            time.sleep(60)

    # GET the URL to init GoPro streaming
    payload={"p1": "gpStream", "a1": "proto_v2", "c1": "restart"}
    requests.get(f"http://{GOPRO_IP}/gp/gpControl/execute", params=payload)
    if RECORD:
        requests.get(f"http://{GOPRO_IP}/gp/gpControl/command/shutter", params={"p": "1"})
        logging.info(f"Began recording at {GOPRO_IP}")
    logging.info(f"Began streaming at {GOPRO_IP}")

def pull_stream():
    """
    Pulls in the UDP stream from the GoPro.
    """
    proc1 = subprocess.Popen(f"ffplay -loglevel panic -fflags nobuffer -fs -f:v mpegts -probesize 8192 udp://{GOPRO_IP}:{PORT}", shell=True)
    logging.info("Began streaming.")
    # proc1 = subprocess.Popen(f"ffplay -fflags nobuffer -f:v mpegts -probesize 8192 udp://{GOPRO_IP}:{PORT}", shell=True)
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (GOPRO_IP, PORT))
        time.sleep(KEEP_ALIVE_PERIOD)

def quit_gopro(signal, frame):
    print("Quitting stream.")
    if RECORD:
        requests.get(f"http://{GOPRO_IP}/gp/gpControl/command/shutter", params={"p": "0"})
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gopro)
    init_streaming()
    pull_stream()