
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

        self.register_param("time_warp", 0, 3, 0.1)

        self.t = time.time()


    def next_frame(self, octopus, data):
        level = data.eq[3]

        # The level gives a little speed boost
        self.t += (time.time()-self.t) + self.time_warp*level

        # Pull out x,y,z
        pixels = octopus.pixels()
        x = np.array([pixel.location[0] for pixel in pixels])
        y = np.array([pixel.location[1] for pixel in pixels])
        z = np.array([pixel.location[2] for pixel in pixels])

        # Sine Time
        r = 255*0.5*(1+np.sin(2*np.pi*self.freq*x*(1) + self.t*self.speed_r))
        g = 0.5*255*0.5*(1+np.sin(2*np.pi*self.freq*y + self.t*self.speed_g))

        ones = np.ones(len(z))
        b = level*255*ones

        #g = g * 0.6 + (r+b) * 0.2

        for i in range(len(pixels)):
            pixels[i].color = (int(r[i]), int(g[i]), int(b[i]))
