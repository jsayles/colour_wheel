import time

import board
import neopixel
from digitalio import DigitalInOut, Direction, Pull


red_button = DigitalInOut(board.A2)
red_button.direction = Direction.INPUT
red_button.pull = Pull.UP

red_led = DigitalInOut(board.A3)
red_led.direction = Direction.OUTPUT

green_button = DigitalInOut(board.A4)
green_button.direction = Direction.INPUT
green_button.pull = Pull.UP

green_led = DigitalInOut(board.A5)
green_led.direction = Direction.OUTPUT

blue_button = DigitalInOut(board.A6)
blue_button.direction = Direction.INPUT
blue_button.pull = Pull.UP

blue_led = DigitalInOut(board.A7)
blue_led.direction = Direction.OUTPUT

board_led = DigitalInOut(board.D13)
board_led.direction = Direction.OUTPUT


while True:
    if red_button.value or green_button.value or blue_button.value:
        print(".")
        board_led.value = False
    else:
        print("X")
        board_led.value = True

    if blue_led.value:
        red_led.value = False
        green_led.value = False
        blue_led.value = False
    else:
        red_led.value = True
        green_led.value = True
        blue_led.value = True

    time.sleep(0.2)
