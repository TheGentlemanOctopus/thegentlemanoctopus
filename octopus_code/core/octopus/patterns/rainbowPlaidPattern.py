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
from pattern import Pattern

# I like these trippy settings:
# freq_r: 0
# freq_g: 60
# freq_b: 24
# speed_r 3.6
# speed_g: -0.6
# speed_b: 8

# how many seconds the color sine waves take to shift through a complete cycle
class RainbowPlaidPattern(Pattern):
    def __init__(self, freq_r=12, freq_g=30, freq_b=24, speed_r=2, speed_g=-3, speed_b=4):
        self.register_param("freq_r", 0, freq_r*2, freq_r)
        self.register_param("freq_g", 0, freq_g*2, freq_g)
        self.register_param("freq_b", 0, freq_b*2, freq_b)

        self.register_param("speed_r", 0.1, speed_r*2, speed_r)
        self.register_param("speed_g", 0.1, speed_g*2, speed_g)
        self.register_param("speed_b", 0.1, speed_b*2, speed_b)

        self.start_time = time.time()

    def next_frame(self, octopus, data):
        t = time.time() - self.start_time

        pixels = octopus.pixels()
        num_pixels = len(pixels)
        for ii in range(num_pixels):
            pct = ii / num_pixels

            # diagonal black stripes
            pct_jittered = (pct * 77) % 37
            blackstripes = color_utils.cos(pct_jittered, offset=t*0.05, period=1, minn=-1.5, maxx=1.5)
            blackstripes_offset = color_utils.cos(t, offset=0.9, period=60, minn=-0.5, maxx=3)
            blackstripes = color_utils.clamp(blackstripes + blackstripes_offset, 0, 1)

            # 3 sine waves for r, g, b which are out of sync with each other
            r = blackstripes * color_utils.remap(math.cos((t/self.speed_r + pct*self.freq_r)*math.pi*2), -1, 1, 0, 256)
            g = blackstripes * color_utils.remap(math.cos((t/self.speed_g + pct*self.freq_g)*math.pi*2), -1, 1, 0, 256)
            b = blackstripes * color_utils.remap(math.cos((t/self.speed_b + pct*self.freq_b)*math.pi*2), -1, 1, 0, 256)
            
            pixels[ii].color = (r, g, b)      