### main.Cheerlight_BLE_HUB.nRF52840express_AirLift.py

"""
Cheerlight BLE HUB for nRF52840 Express Feather + AirLift FeatherWing

Learn more about Cheerlight: https://cheerlights.com/

This connect to the Cheerlight json API, get the color, advertise it in BLE.
The NeoPixel on the nRF52840 Express Feather display the advertised color.

To display the color, one can use a Circuit Playground Bluetooth and code from this project
https://learn.adafruit.com/hide-n-seek-bluefruit-ornament/overview

Original AirLift cheerlight source from ladyada and friends:
https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI/blob/master/examples/esp32spi_cheerlights.py

Modification for nRF52840 + Airlift by David Glaude
Use the airlift feather RGB LED for status_light
Use the build in NEOPIXEL to cheerlight color

This requires at least the following library structure in /lib:
* adafruit_bus_device
* adafruit_esp32spi
* adafruit_ble
adafruit_requests.mpy
adafruit_rgbled.mpy
neopixel.mpy
simpleio.mpy

You also need a file secrets.py that contain your SSID and Wifi password:
 secrets = {
    'ssid' : 'My_SSID',
    'password' : 'My_Password'
    }

Repeat forever
  Connect to Cheerlight API
  Get the current color hex code from JSON
  If the color changed
    Display the new color on the HUB
    Advertise the new color as BLE beacon
  Wait 1 minute

"""

import time
import board
import busio
from digitalio import DigitalInOut

from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager

import neopixel

from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor

ble = BLERadio()
advertisement = AdafruitColor()

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

DATA_SOURCE = "https://api.thingspeak.com/channels/1417/feeds.json?results=1"
DATA_LOCATION = ["feeds", 0, "field2"]

### AirLift FeatherWing attachement and configuration:
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

### This code for controling the LED on the airlift is borrowed from:
### https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI/blob/master/examples/esp32spi_aio_post.py
### And it was added by https://github.com/brentru
import adafruit_rgbled
from adafruit_esp32spi import PWMOut
RED_LED = PWMOut.PWMOut(esp, 26)
GREEN_LED = PWMOut.PWMOut(esp, 27)
BLUE_LED = PWMOut.PWMOut(esp, 25)
status_light = adafruit_rgbled.RGBLED(RED_LED, BLUE_LED, GREEN_LED)

# Now start a wifi manager with that status_light as indicator of wifi activity
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

### This is the NeoPixel of the nRF52840express
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3)
pixels.fill(0)

# we'll save the value in question
last_value = value = None

while True:
    try:
        print("Fetching json from", DATA_SOURCE)
        response = wifi.get(DATA_SOURCE)
        print(response.json())
        value = response.json()
        for key in DATA_LOCATION:
            value = value[key]
            print(value)
        response.close()
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue

    if not value:
        continue
    if last_value != value:
        color = int(value[1:], 16)
        pixels.fill(color)
        print("Beaconing the new color {:06x}".format(color))
        advertisement.color = color
        ble.stop_advertising()
        ble.start_advertising(advertisement)
        last_value = value

    response = None
    time.sleep(60)

### We should never reach this point because of the infinit loop.
ble.stop_advertising()