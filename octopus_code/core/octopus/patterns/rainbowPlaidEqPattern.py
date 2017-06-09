#!/usr/bin/env python

"""Adaoted from the "wall" demo client for Open Pixel Control
http://github.com/zestyping/openpixelcontrol

Creates a shifting rainbow plaid pattern by overlaying different sine waves
in the red, green, and blue channels.

To run:
First start the gl simulator using the included "wall" layout

    make
    bin/gl_server layouts/octopus.json

Then run this script in another shell to send colors to the simulator

    python_clients/raver_plaid.py

"""

from __future__ import division
import time
import math
import sys
import color_utils
import numpy as np
from pattern import Pattern


# I like these trippy settings:
# freq_r: 0
# freq_g: 60
# freq_b: 24
# speed_r 3.6
# speed_g: -0.6
# speed_b: 8

two_pi = np.float(color_utils.pi_16*2)

# how many seconds the color sine waves take to shift through a complete cycle
class RainbowPlaidEqPattern(Pattern):
    def __init__(self, freq_r=24, freq_g=24, freq_b=24, speed_r=2, speed_g=-3, speed_b=4):
        self.register_param("freq_r", 0, freq_r*2, freq_r)
        self.register_param("freq_g", 0, freq_g*2, freq_g)
        self.register_param("freq_b", 0, freq_b*2, freq_b)

        self.register_param("speed_r", 0.1, speed_r*2, speed_r)
        self.register_param("speed_g", 0.1, speed_g*2, speed_g)
        self.register_param("speed_b", 0.1, speed_b*2, speed_b)

        self.register_param("time_warp_speed", 0, 5, 5)

        self.pattern_time = 0
        self.real_time = 0

        self.start_time = time.time()

    def on_pattern_select(self, octopus):
        self.pixels = octopus.pixels()

        self.pct = color_utils.linspace_16(0, 1, len(self.pixels))


        #0,1,2,...,37,0,1,2,...,37
        self.pct_jittered = np.mod(color_utils.linspace_16(0, 77, len(self.pixels)), 37)


    def next_frame(self, octopus, data):
        current_time = np.float16((time.time() - self.start_time) % 1000)

        speed = data['eq'][data["rhythm_channel"]]

        self.pattern_time = self.pattern_time + (self.time_warp_speed*speed+1)*(self.real_time - current_time)
        self.real_time = current_time

        t = self.pattern_time

        blackstripes = color_utils.cos_lookup(self.pct_jittered, offset=t*0.05, period=1, minn=-1.5, maxx=1.5)
        blackstripes_offset = color_utils.cos_lookup(t, offset=0.9, period=60, minn=-0.5, maxx=3)
        clamp = color_utils.clamp(blackstripes + blackstripes_offset, 0, 1)

        r = clamp*np.float16(127)*(np.float16(1)+color_utils.cos_lookup(two_pi*(t/self.speed_r + self.pct*self.freq_r)))
        g = clamp*np.float16(127)*(np.float16(1)+color_utils.cos_lookup(two_pi*(t/self.speed_g + self.pct*self.freq_g)))
        b = clamp*np.float16(127)*(np.float16(1)+color_utils.cos_lookup(two_pi*(t/self.speed_b + self.pct*self.freq_b)))

        for i in range(len(self.pixels)):
            self.pixels[i].color = (r[i], g[i], b[i])
