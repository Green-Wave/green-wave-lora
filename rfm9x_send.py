#!/usr/bin/env python3

import time
import requests
import sys

import board
import busio
import digitalio

import adafruit_rfm9x

# Define radio parameters.
RADIO_FREQ_MHZ = 868.0  # Frequency of the radio in Mhz. Must match your
                        # module! Can be a value like 915.0, 433.0, etc.

CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

url = "http://172.16.2.107/seconds_phase_left"

while True:

    try:
        response = requests.get(url=url, timeout=3)
    except KeyboardInterrupt:
        raise
    except (ConnectionError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
        print(f"Connection error: {e}. Retrying.")
        continue
    except:
        print("Unexpected error:", sys.exc_info()[0])
        continue
    green_string = None

    if response.json()["is_green"]:
        green_string = "1"
    else:
        green_string = "0"

    lora_packet = ";".join(
        [
            green_string,
            str("{:.2f}".format(response.json()["seconds_phase_left"])),
            str("{:.0f}".format(response.json()["seconds_phase_total"])),
        ]
    )

    rfm9x.send(bytes(lora_packet, "utf-8"))
    print("Sent: ", lora_packet)
    time.sleep(0.65)

