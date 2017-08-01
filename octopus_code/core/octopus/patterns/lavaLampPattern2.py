
from pattern import Pattern
import time
import numpy as np


class LavaLampPattern2(Pattern):
    def __init__(self):
        self.register_param("freq", 0, 1, 0.2)
        self.register_param("speed_r", 0, 10, 2)
        self.register_param("speed_g", 0, 10, 1)
        self.register_param("speed_b", 0, 10, 1.5)
        self.register_param("blob_speed", 0, 10, 1)

        self.register_param("time_warp", 0, 10, 1)

        self.t = time.time()

    def next_frame(self, octopus, data):
        # The level gives a little speed boost
        self.t += (time.time()-self.t) + self.time_warp*data.level

        # Pull out x,y,z
        pixels = octopus.pixels()
        x = np.array([pixel.location[0] for pixel in pixels])
        y = np.array([pixel.location[1] for pixel in pixels])
        z = np.array([pixel.location[2] for pixel in pixels])

        # Sine Time
        r = 255*0.5*(1+np.sin(2*np.pi*self.freq*x + self.t*self.speed_r))
        g = 255*0.5*(1+np.sin(2*np.pi*self.freq*y + self.t*self.speed_g))
        b = 255*0.5*(1+np.sin(2*np.pi*self.freq*z + self.t*self.speed_b))

        g = g * 0.6 + (r+b) * 0.2

        # TODO: black out regions?
        clamp_freq = 1/3.0
        r_clamp = np.cos(x*2*np.pi*clamp_freq + self.t*self.blob_speed + 12)
        g_clamp = np.cos(y*2*np.pi*clamp_freq + self.t*self.blob_speed + 24)
        b_clamp = np.cos(z*2*np.pi*clamp_freq + self.t*self.blob_speed + 34)

        for i in range(len(pixels)):
            pixels[i].color = (int(r[i]), int(b[i]), int(g[i]))
