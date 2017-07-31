from pattern import Pattern
import time
from core.octopus.layouts.octopusLayout import OctopusLayout
import numpy as np

class Carousel(Pattern):
    # Speed is in degress per second
    def __init__(self, speed=180):
        self.register_param("speed", 0, 1080, 30)

        self.t = time.time()

    # Reset Time
    def on_pattern_select(self, octopus):
        self.t = time.time()

    # TODO: Phase shift on eq data
    def next_frame(self, octopus, data):
        pixels = octopus.pixels()

        dt = time.time() - self.t

        self.t = time.time()

        for pixel in octopus.pixels():
            #TODO: Something nicer


            r = int(np.abs((1.0/3)*255*pixel.location[0]))
            g = int(np.abs((1.0/3)*255*pixel.location[1]))
            b = 20


            pixel.rotate(dt*self.speed*np.sin(pixel.radius()))

            pixel.color = (r,g,b)

        



if __name__ == '__main__':
    carousel = Carousel()

    octopus_layout = OctopusLayout()

    x = [pixel.location[0] for pixel in octopus_layout.pixels()]

    print "min x", np.min(x)
    print "max x", np.max(x)

    carousel.next_frame(octopus_layout, data=None)