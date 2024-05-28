#!/usr/bin/env python3

import os
import time
import requests
from dotenv import load_dotenv
import ev3dev2
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.display import Display
from ev3dev2.button import Button
from ev3dev2.sound import Sound

# Load environment variables
load_dotenv()

# Constants
INTERFACES = os.environ.get("INTERFACES", "").split(",")
POST_URL = os.environ.get("POST_URL", "")
FONT = ev3dev2.fonts.load("courB24")

# Initialize devices
touch_sensor = TouchSensor()
delay_motor = LargeMotor(address=OUTPUT_A)
loss_motor = LargeMotor(address=OUTPUT_B)
btn = Button()
sound = Sound()
display = Display()

# Reset motor positions
delay_motor.position = 0
loss_motor.position = 0

def display_metrics(delay_time, loss_rate):
    """Update the EV3 screen with delay and loss metrics."""
    display.clear()
    display.text_pixels("Delay="+delay_time+"ms\nLoss="+loss_rate+"%", x=0, y=0, font=FONT)
    display.update()

def post_metrics(interface, delay_time, loss_rate):
    """Post delay and loss metrics to the server."""
    data = {
        'Rate': '', 'rate_unit': 'mbit', 'Delay': delay_time,
        'DelayVariance': '', 'Loss': loss_rate, 'LossCorrelation': '',
        'Duplicate': '', 'Reorder': '', 'ReorderCorrelation': '',
        'Corrupt': '', 'Limit': '10240'
    }
    response = requests.post(POST_URL+interface, data=data)
    return response.status_code, response.reason

def main_loop():
    """Main loop to handle touch sensor and update metrics."""
    while True:
        while not touch_sensor.is_pressed:
            delay_time = str(-int(round(delay_motor.position / 10)))
            loss_rate = str(int(round(loss_motor.position / 10)))
            display_metrics(delay_time, loss_rate)
            if btn.any():
                delay_motor.position = 0
                loss_motor.position = 0
            time.sleep(0.1)

        display.text_pixels("Ship it", x=0, y=0, font=FONT)
        display.update()

        sound.beep()

        for interface in INTERFACES:
            status_code, reason = post_metrics(interface, delay_time, loss_rate)
            display.clear()
            display.text_pixels(interface+"\n"+str(status_code)+", "+reason, x=0, y=0, font=FONT)
            display.update()
            time.sleep(0.5)

        time.sleep(2)

if __name__ == "__main__":
    main_loop()
