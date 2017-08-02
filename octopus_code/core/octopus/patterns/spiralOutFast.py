from pattern import Pattern
import copy
import numpy as np
import random
import collections
#from scipy.signal import convolve2d
import time
from collections import deque


class SpiralOutFast(Pattern):
    def __init__(self):
        self.register_param("r_leak", 0, 3, 1.2)
        self.register_param("g_leak", 0, 3, 1.7)
        self.register_param("b_leak", 0, 3, 2)

        self.register_param("speed", 0, 1 , 0)

        #Initialise time and color history
        self.t = [0,0]
        self.r = [0,0]
        self.g = [0,0]
        self.b = [0,0]

        self.buff_len = 1500

        self.start_time = np.float(time.time())

    def on_pattern_select(self, octopus):
        self.pixels = octopus.pixels_spiral()
        self.previous_time = np.float16(time.time())


    def next_frame(self, octopus, data):
        current_time = time.time() - self.start_time
        self.previous_time = current_time

        scale = float(255)
        self.t.append(current_time)
        self.r.append(scale*np.mean([data.eq[0], data.eq[1]]))
        self.g.append(scale*np.mean([data.eq[2], data.eq[3]]))
        self.b.append(scale*np.mean([data.eq[4], data.eq[5], data.eq[6]]))


        if len(self.t) > self.buff_len:
            del self.t[0]
            del self.r[0]
            del self.g[0]
            del self.b[0]


        domain_r = np.linspace(current_time, current_time - self.r_leak, len(self.pixels)) 
        domain_g = np.linspace(current_time, current_time - self.g_leak, len(self.pixels)) 
        domain_b = np.linspace(current_time, current_time - self.b_leak, len(self.pixels)) 

        r = np.interp(domain_r, self.t, self.r)
        g = np.interp(domain_g, self.t, self.g)
        b = np.interp(domain_b, self.t, self.b)

        for i in range(len(self.pixels)):
            self.pixels[i].color = (r[i], g[i], b[i])
