from pattern import Pattern

import time
import math

class SimplePattern(Pattern):
    def next_frame(self, octopus, data):
        intensity = 127 + 127*math.cos(time.time())
        color = (intensity, intensity, intensity)

        for pixel in octopus.pixels():
            pixel.color = color