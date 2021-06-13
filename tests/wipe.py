import time

import board
import neopixel
from digitalio import DigitalInOut, Direction, Pull


# Colour Constants
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
AQUA = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)
WHITE = (255, 255, 255)

COLOURS = [BLACK, RED, YELLOW, GREEN, AQUA, BLUE, PURPLE]


class State:
    _debounce = 0.2

    def __init__(self):
        self.ring1 = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.5)
        self.ring2 = neopixel.NeoPixel(board.A2, 12, brightness=0.5)

        self.colour_index = 0

        self.switch = DigitalInOut(board.D7)
        self.switch.direction = Direction.INPUT
        self.switch.pull = Pull.UP
        self.switch_state = self.switch.value

        self.buttonA = DigitalInOut(board.D4)
        self.buttonA_state = self.buttonA.value

        self.buttonB = DigitalInOut(board.D5)
        self.buttonB_state = self.buttonB.value

        self.red_button = DigitalInOut(board.A2)
        self.red_button.direction = Direction.INPUT
        self.red_button.pull = Pull.UP
        self.red_state = self.red_button.value

        self.red_led = DigitalInOut(board.A3)
        self.red_led.direction = Direction.OUTPUT
        self.red_led.value = False

        self.green_button = DigitalInOut(board.A4)
        self.green_button.direction = Direction.INPUT
        self.green_button.pull = Pull.UP
        self.green_state = self.green_button.value

        self.green_led = DigitalInOut(board.A5)
        self.green_led.direction = Direction.OUTPUT
        self.green_led.value = False

        self.blue_button = DigitalInOut(board.A6)
        self.blue_button.direction = Direction.INPUT
        self.blue_button.pull = Pull.UP
        self.blue_state = self.blue_button.value

        self.blue_led = DigitalInOut(board.A7)
        self.blue_led.direction = Direction.OUTPUT
        self.blue_led.value = False

        self.board_led = DigitalInOut(board.D13)
        self.board_led.direction = Direction.OUTPUT

        self.checkin = time.monotonic()

    def update(self):
        if time.monotonic() - self.checkin > self._debounce:
            self.switch_state = self.switch.value
            self.buttonA_state = self.buttonA.value
            self.buttonB_state = self.buttonB.value
            self.red_state = self.red_button.value
            self.green_state = self.green_button.value
            self.blue_state = self.blue_button.value


    def __repr__(self):
        return "<Buttons: {}/{}, Switch: {}, Color: {}>".format(self.buttonA_state, self.buttonB_state, self.switch_state, self.colour_index)


def simpleCircle(wait):
    wipeColour(RED, ring1, wait)
    wipeColour(RED, ring2, wait)
    wipeColour(YELLOW, ring1, wait)
    wipeColour(YELLOW, ring2, wait)
    wipeColour(GREEN, ring1, wait)
    wipeColour(GREEN, ring2, wait)
    wipeColour(AQUA, ring1, wait)
    wipeColour(AQUA, ring2, wait)
    wipeColour(BLUE, ring1, wait)
    wipeColour(BLUE, ring2, wait)
    wipeColour(PURPLE, ring1, wait)
    wipeColour(PURPLE, ring2, wait)


def wipeColour(colour, pixels, wait):
    for i in range(len(pixels)):
        pixels[i] = colour
        time.sleep(wait)
    #time.sleep(1)


def goColour(colour, pixels):
    wipeColour(colour, pixels, 0)

state = State()

# Run continuously
while True:
    state.update()

    updated = False
    if state.buttonA_state:
        state.colour_index = state.colour_index + 1
        if state.colour_index >= len(COLOURS):
            # Skip 0 (black)
            state.colour_index = 1
        updated = True
    elif state.buttonB_state:
        state.colour_index = state.colour_index - 1
        if state.colour_index <= 0:
            state.colour_index = len(COLOURS) - 1
        updated = True

    if state.switch_state:
        if updated:
            wait = 0.1
            colour = COLOURS[state.colour_index]
            wipeColour(colour, state.ring1, wait)
            wipeColour(colour, state.ring2, wait)
    else:
        goColour(BLACK, state.ring1)
        goColour(BLACK, state.ring2)
        time.sleep(1)

    print(state)
