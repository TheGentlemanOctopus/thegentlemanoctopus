from pattern import Pattern
import time
from core.octopus.layouts.octopusLayout import OctopusLayout
import numpy as np
import colorsys
import time

class CarouselPattern(Pattern):
    # Speed is in degress per second
    def __init__(self):
        self.register_param("hue_sweep", 0, 1, 0.2)

        self.register_param("saturation", 0, 1, 1)
        self.register_param("value", 0, 1, 0.8)

        self.register_param("speed_gradient", -300, 300, 100)
        self.register_param("speed_offset", -100, 100, 5)

        self.register_param("hue_rate", 0, 1, 0.1)

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
        locations = np.array([pixel.location for pixel in pixels])

        x = locations[:,0]
        y = locations[:,1]
        z = locations[:,2]

        r = np.linalg.norm(locations, axis=1)
        phi = np.arctan2(y, x)

        self.hue_offset = (dt*data.eq[3]*self.hue_rate) % 1

        #Go rotational
        angular_velocity = self.speed_gradient*r + self.speed_offset
        d_phi = dt*angular_velocity
        cos = np.cos(np.radians(d_phi))
        sin = np.sin(np.radians(d_phi))

        # rotation matrix
        new_x = cos*x - sin*y
        new_y = sin*x + cos*y

        for i in range(len(pixels)):
            pixels[i].location = np.array([new_x[i], new_y[i], z[i]])

        #Set HSV
        h = (self.hue_offset + 0.5*self.hue_sweep*np.sin(phi)) % 1 
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