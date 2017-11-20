import numpy as np
from ledStrip import LedStrip

class Tentacle:
    '''Tentacle is a key limb of the octopus, who normally have 8 of them
    Our GentlemanOctopus typically has two led strips per limb
    '''
    def __init__(self, r, theta, length, nPixels):
        ''' r is radius of tentacle
            theta is its angle with respect to the origin
            length is its length in units
            nPixels is pixel per led strip, there are 2 strips per tentacle
        '''
        self.led_strips = []

        dTheta = np.pi/32
        for angle in [theta + dTheta, theta - dTheta]:
            base = [r*np.cos(angle), r*np.sin(angle), 0]
            direction = [np.cos(angle), np.sin(angle), 0]
            self.led_strips.append(LedStrip(base, length, direction, nPixels))

    def pixels(self):
        ''' List of all pixels in the tentacle from base-->tip, base-->tip'''
        pixels = []
        for led_strip in self.led_strips:
            pixels.extend(led_strip.pixels)

        return pixels

    def pixels_zig_zag(self):
        ''' List of all pixels in the tentacle by Base --> Tip; Tip --> Base, Base --> Tip .... '''
        pixels = []
        flip = False
        for led_strip in self.led_strips:
            pixels.extend(led_strip.pixels[::-1] if flip else led_strip.pixels)
            flip = not flip

        return pixels