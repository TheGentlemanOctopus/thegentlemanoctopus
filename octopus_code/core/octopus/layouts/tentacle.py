import numpy as np
from ledStrip import LedStrip

class Tentacle:
    def __init__(self, r, theta, length, nPixels):
        self.led_strips = []

        dTheta = np.pi/32
        for angle in [theta + dTheta, theta - dTheta]:
            base = [r*np.cos(angle), r*np.sin(angle), 0]
            direction = [np.cos(angle), np.sin(angle), 0]
            self.led_strips.append(LedStrip(base, length, direction, nPixels))

    def pixels(self):
        pixels = []
        for led_strip in self.led_strips:
            pixels.extend(led_strip.pixels)

        return pixels

    # Base --> Tip; Tip --> Base, Base --> Tip ....
    def pixels_zig_zag(self):
        pixels = []
        flip = False
        for led_strip in self.led_strips:
            pixels.extend(led_strip.pixels[::-1] if flip else led_strip.pixels)
            flip = not flip

        return pixels