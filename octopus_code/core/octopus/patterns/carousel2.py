from pattern import Pattern
import time
from core.octopus.layouts.octopusLayout import OctopusLayout
import numpy as np
import colorsys

class Carousel2(Pattern):
    # Speed is in degress per second
    def __init__(self, speed=180):
        self.register_param("hue_offset", 0, 1, 0.5)
        self.register_param("hue_sweep", 0, 1, 0.5)

        self.register_param("saturation", 0, 1, 0.5)
        self.register_param("value", 0, 1, 0.8)

    # Reset tings
    def on_pattern_select(self, octopus):
        self.octopus = octopus.clone()

    # TODO: Phase shift on eq data
    def next_frame(self, octopus, data):
        pixels = self.octopus.pixels()

        polar = np.array([pixel.polar_location() for pixel in pixels])

        r = polar[:,0]
        phi = polar[:,1]

        h = self.hue_offset + 0.5*self.hue_sweep*np.sin(phi)

        s = self.saturation*np.ones(len(pixels))
        v = self.value*np.ones(len(pixels))
        
        octopus_pixels = octopus.pixels()
        for i in range(len(pixels)):
            rgb = colorsys.hsv_to_rgb(h[i], s[i], v[i])

            rgb_255 = [int(255*x) for x in rgb]
            octopus_pixels[i].color = tuple(rgb_255)


        # dt = time.time() - self.t
        # self.t = time.time()

        # for pixel in self.octopus.pixels():
        #     #TODO: Something nicer
        #     r = int(np.abs((1.0/3)*255*pixel.location[0]))
        #     g = int(np.abs((1.0/3)*255*pixel.location[1]))
        #     b = 20

        #     dtheta = dt*self.speed*np.sin(pixel.radius() + 2*np.pi*np.sin(time.time()))

        #     pixel.rotate(dtheta)

        #     pixel.color = (r,g,b)

        # # Pull out x,y,z
        # pixels = octopus.pixels()
        # x = np.array([pixel.location[0] for pixel in pixels])
        # y = np.array([pixel.location[1] for pixel in pixels])
        # z = np.array([pixel.location[2] for pixel in pixels])

        # h = 0.5*(1+np.sin(2*np.pi*self.freq*x))
        # s = self.saturation*np.ones(len(x))
        # v = 0.5*(1+np.sin(2*np.pi*self.freq*z))


        # for i in range(len(pixels)):
        #     hsv = colorsys.hsv_to_rgb(h[i], s[i], v[i])
        #     pixels[i].color = tuple([int(255*x) for x in hsv])



        # # Sine Time
        # r = 255*0.5*(1+np.sin(2*np.pi*self.freq*x + self.t*self.speed_r))
        # g = 255*0.5*(1+np.sin(2*np.pi*self.freq*y + self.t*self.speed_g))
        # b = 255*0.5*(1+np.sin(2*np.pi*self.freq*z + self.t*self.speed_b))

        # g = g * 0.6 + (r+b) * 0.2



        # for i in range(len(pixels)):
        #     pixels[i].color = (int(r[i]), int(b[i]), int(g[i]))  



if __name__ == '__main__':
    carousel = Carousel()

    octopus_layout = OctopusLayout()

    x = [pixel.location[0] for pixel in octopus_layout.pixels()]

    print "min x", np.min(x)
    print "max x", np.max(x)

    carousel.next_frame(octopus_layout, data=None)