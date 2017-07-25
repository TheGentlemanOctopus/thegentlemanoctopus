from pattern import Pattern
import copy
import numpy as np
import random
import collections
#from scipy.signal import convolve2d
import time
from collections import deque

import color_utils

#This was an idea that didnt really work out. Could remove.
#TODO: params
class SpiralOutFast(Pattern):
    def __init__(self):
        self.register_param("r_leak", 0, 3, 1.2)
        self.register_param("g_leak", 0, 3, 1.7)
        self.register_param("b_leak", 0, 3, 2)

        self.register_param("speed", 0, 1 , 0)

        self.t = np.array([0,0], dtype=np.float16)
        self.r = np.array([0,0], dtype=np.float16)
        self.g = np.array([0,0], dtype=np.float16)
        self.b = np.array([0,0], dtype=np.float16)

        self.buff_len = 1500

        self.start_time = np.float(time.time())

    def on_pattern_select(self, octopus):
        self.pixels = octopus.pixels_spiral()
        self.previous_time = np.float16(time.time())

        #TODO: Param
        self.domain = color_utils.linspace_16(0,1,len(self.pixels))


    def next_frame(self, octopus, data):
        eq = data.eq

        current_time = np.float16((time.time() - self.start_time) % 1000)
        dt = current_time - self.previous_time
        self.previous_time = current_time

        self.t = np.append(self.t, current_time)
        

        scale = np.float16(255)
        self.r = np.append(self.r, scale*np.mean([eq[0], eq[1]], dtype=np.float16))
        self.g = np.append(self.g, scale*np.mean([eq[2],eq[3]], dtype=np.float16))
        self.b = np.append(self.b, scale*np.mean([eq[4], eq[5],eq[6]], dtype=np.float16))

        if len(self.t) > self.buff_len:
            self.t.pop(0)
            self.r.pop(0)
            self.g.pop(0)
            self.b.pop(0)


        domain_r = color_utils.linspace_16(current_time, current_time - self.r_leak, len(self.pixels)) 
        domain_g = color_utils.linspace_16(current_time, current_time - self.g_leak, len(self.pixels)) 
        domain_b = color_utils.linspace_16(current_time, current_time - self.b_leak, len(self.pixels)) 

        r = np.interp(domain_r, self.t, self.r)
        g = np.interp(domain_r, self.t, self.g)
        b = np.interp(domain_r, self.t, self.b)

        for i in range(len(self.pixels)):
            self.pixels[i].color = (r[i], g[i], b[i])
