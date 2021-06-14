import gc
import time

import board
import busio
import digitalio
import adafruit_lis3dh
import neopixel
from digitalio import DigitalInOut, Direction, Pull


class LEDButton:
    _cycles_until_dark = 60

    def __init__(self, button_pin, led_pin):
        self.button = DigitalInOut(button_pin)
        self.button.direction = Direction.INPUT
        self.button.pull = Pull.UP
        self.state = self.button.value

        self.led = DigitalInOut(led_pin)
        self.led.direction = Direction.OUTPUT
        self.led.value = False

        self.cycles_since_update = self._cycles_until_dark

    def led_off(self):
        self.led.value = False

    def led_on(self):
        self.led.value = True

    def update(self):
        updated = False
        new_state = self.button.value
        if new_state == self.state:
            # No change
            if self.cycles_since_update < self._cycles_until_dark:
                self.cycles_since_update += 1
        else:
            # State Change
            self.cycles_since_update = 0
            self.state = new_state
            updated = True
        return updated

    @property
    def pressed(self):
        return self.state == False

    @property
    def inactive(self):
        if not self.pressed:
            if self.cycles_since_update >= self._cycles_until_dark:
                return True
        return False


class LEDRing:

    def __init__(self, ring_pin, pixels, brightness):
        self.ring = neopixel.NeoPixel(ring_pin, pixels, brightness=brightness)

    def wipe_colour(self, colour, wait):
        for i in range(len(self.ring)):
            self.ring[i] = colour
            time.sleep(wait)

    def go_colour(self, colour):
        self.wipe_colour(colour, 0)


class State:
    _debounce = 0.1

    def __init__(self):
        print("Starting...")

        self.inner_ring = LEDRing(board.NEOPIXEL, 10, 0.25)
        self.outer_ring = LEDRing(board.A1, 60, 1.0)

        self.r_button = LEDButton(board.D9, board.D10) #A2 and A3
        self.g_button = LEDButton(board.D3, board.D2)  #A5 and A5
        self.b_button = LEDButton(board.D0, board.D1)  #A6 and A7

        self._i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
        self._int1 = digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT)
        self._lis3dh = adafruit_lis3dh.LIS3DH_I2C(self._i2c, address=0x19, int1=self._int1)
        self._lis3dh.range = adafruit_lis3dh.RANGE_8_G

        # Start with our button LEDs off
        self.button_leds_off()

        self.update_ts = time.monotonic()

    def update(self):
        if time.monotonic() - self.update_ts > self._debounce:
            self.update_ts = time.monotonic()

            self.update_button_state()

            if self.buttons_are_inactive():
                if self.button_leds:
                    print("Turning off button lights...")
                    self.button_leds_off()
            else:
                self.button_leds_on()

            # Debug code -- REOMVE --JLS
            # print("({}, {}, {})".format(self.r_button.cycles_since_update, self.g_button.cycles_since_update, self.b_button.cycles_since_update))
            # gc.collect()
            # print(gc.mem_free())

    def update_button_state(self):
        self.r_button.update()
        self.g_button.update()
        self.b_button.update()

    def reset_button_timers(self):
        self.r_button.cycles_since_update = 0
        self.g_button.cycles_since_update = 0
        self.b_button.cycles_since_update = 0

    def buttons_are_inactive(self):
        if self.r_button.inactive and self.g_button.inactive and self.b_button.inactive:
            return True

    def button_leds_off(self):
        self.button_leds = False
        self.r_button.led_off()
        self.g_button.led_off()
        self.b_button.led_off()

    def button_leds_on(self):
        self.button_leds = True
        self.r_button.led_on()
        self.g_button.led_on()
        self.b_button.led_on()

    def get_colour(self):
        r = 255 if self.r_button.pressed else 0
        g = 255 if self.g_button.pressed else 0
        b = 255 if self.b_button.pressed else 0
        return (r, g, b)

    def shake(self, shake_threshold=30):
        return self._lis3dh.shake(shake_threshold=shake_threshold)

    def __repr__(self):
        return "<Color: {}>".format(self.get_colour())


state = State()

while True:
    state.update()
    colour = state.get_colour()
    state.inner_ring.go_colour(colour)
    state.outer_ring.go_colour(colour)

    if state.shake(shake_threshold=20):
        print("Shake detected!")
        state.reset_button_timers()
