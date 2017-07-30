
from pattern import Pattern
import time
import numpy as np
class LavaLampPattern2(Pattern):
    def __init__(self):
        pass

    def next_frame(self, octopus, data):
        t = time.time()

        pixels = octopus.pixels()
        x = np.array([pixel.location[0] for pixel in pixels])
        y = np.array([pixel.location[1] for pixel in pixels])
        z = np.array([pixel.location[2] for pixel in pixels])

        freq = 0.5
        speed = 1
        r = 255*(1+np.sin(2*np.pi*freq*x + t*speed))
        g = 255*(1+np.sin(2*np.pi*freq*y + t*speed))
        b = 255*(1+np.sin(2*np.pi*freq*z + t*speed))

        for i in range(len(pixels)):
            pixels[i].color = (int(r[i]), int(b[i]), int(g[i]))