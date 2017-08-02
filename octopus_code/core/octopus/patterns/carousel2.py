from pattern import Pattern
import time
from core.octopus.layouts.octopusLayout import OctopusLayout
import numpy as np
import colorsys
import time

class Carousel2(Pattern):
    # Speed is in degress per second
    def __init__(self, speed=180):
        self.register_param("hue_offset", 0, 1, 0.5)
        self.register_param("hue_sweep", 0, 1, 0.2)

        self.register_param("saturation", 0, 1, 1)
        self.register_param("value", 0, 1, 0.8)

        # Deg per second
        self.register_param("ang_velocity", 0, 300, 150)

        self.register_param("speed_gradient", -300, 300, 120)
        self.register_param("speed_offset", -100, 100, -5)

        self.t = time.time()

    # Reset tings
    def on_pattern_select(self, octopus):
        self.octopus = octopus.clone()
        self.dt()

    # Time elapsed since last call to dt
    def dt(self):
        # Rotational
        current_time = time.time()
        dt = current_time - self.t
        self.t = current_time

        return dt


    # TODO: Phase shift on eq data
    def next_frame(self, octopus, data):
        pixels = self.octopus.pixels()
        dt = self.dt()

        #Get polar coordinates
        polar = np.array([pixel.polar_location() for pixel in pixels])

        r = polar[:,0]
        phi = polar[:,1]

        #Go rotational
        for i in range(len(pixels)):
            angular_velocity = self.speed_gradient*r[i] + self.speed_offset
            d_phi = dt * angular_velocity
            pixels[i].rotate(d_phi)

        #Set HSV
        h = self.hue_offset + 0.5*self.hue_sweep*np.sin(phi)

        s = self.saturation*np.ones(len(pixels))
        v = self.value*np.ones(len(pixels))
        
        octopus_pixels = octopus.pixels()
        for i in range(len(pixels)):
            rgb = colorsys.hsv_to_rgb(h[i], s[i], v[i])

            rgb_255 = [int(255*x) for x in rgb]
            octopus_pixels[i].color = tuple(rgb_255)


if __name__ == '__main__':
    carousel = Carousel()

    octopus_layout = OctopusLayout()

    x = [pixel.location[0] for pixel in octopus_layout.pixels()]

    print "min x", np.min(x)
    print "max x", np.max(x)

    carousel.next_frame(octopus_layout, data=None)