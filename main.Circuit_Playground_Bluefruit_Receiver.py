"""
Simplified Circuit Playground Bluefruit Ornament

This demo uses advertising to set the color of scanning devices depending on the strongest broadcast
signal received.
"""
### Original code https://learn.adafruit.com/hide-n-seek-bluefruit-ornament/code-with-circuitpython
import time
from adafruit_circuitplayground.bluefruit import cpb

from adafruit_ble import BLERadio

from adafruit_ble.advertising.adafruit import AdafruitColor

ble = BLERadio()

color_options = 0x110011

cpb.pixels.auto_write = False
cpb.pixels.brightness = 0.1
cpb.pixels.fill(color_options)

while True:
    # Listens for color broadcasts and shows the color of the strongest signal.
    closest = None
    closest_rssi = -80
    closest_last_time = 0
    print("Scanning for colors")
    while not cpb.switch:
        for entry in ble.start_scan(AdafruitColor, minimum_rssi=-100, timeout=1):
            now = time.monotonic()
            new = False
            if entry.address == closest:
                pass
            elif entry.rssi > closest_rssi or now - closest_last_time > 0.4:
                closest = entry.address
            else:
                continue
            closest_rssi = entry.rssi
            closest_last_time = now
            discrete_strength = min((100 + entry.rssi) // 5, 10)
            color_options = entry.color
            cpb.pixels.fill(color_options)
            cpb.pixels.show()
        # Clear the pixels if we haven't heard from anything recently.
        now = time.monotonic()
        if now - closest_last_time > 1:
            cpb.pixels.fill(0x000000)
            cpb.pixels.show()
    ble.stop_scan()