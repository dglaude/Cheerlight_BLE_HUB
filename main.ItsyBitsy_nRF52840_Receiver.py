"""
Simplified "Circuit Playground Bluefruit Ornament" but for ItsyBitsy nRF52840

This demo uses advertising to set the color of scanning devices depending on the strongest broadcast
signal received.
"""
### Original code https://learn.adafruit.com/hide-n-seek-bluefruit-ornament/code-with-circuitpython
import time
import board

from adafruit_ble import BLERadio

from adafruit_ble.advertising.adafruit import AdafruitColor

ble = BLERadio()

color_options = 0x110011

### Configure the DotStar available on the ItsyBitsy nRF52840
import adafruit_dotstar as dotstar

# On-board DotStar for boards including Gemma, Trinket, and ItsyBitsy
rgb = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
rgb.brightness = 0.3
rgb.fill(0)

while True:
    # Listens for color broadcasts and shows the color of the strongest signal.
    closest = None
    closest_rssi = -80
    closest_last_time = 0
    print("Scanning for colors")
    while True:
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
            color_options = entry.color
            rgb.fill(color_options)
        # Clear the pixels if we haven't heard from anything recently.
        now = time.monotonic()
        if now - closest_last_time > 1:
            rgb.fill(0)
    ble.stop_scan()