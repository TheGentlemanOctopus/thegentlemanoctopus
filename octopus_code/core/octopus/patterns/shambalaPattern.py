from pattern import Pattern

import numpy as np

#from patterns.solidColorPattern import SolidColorPattern, SpiralOut, PulseOut, SpiralOutFast, IntegrateF, GridPattern, HelicopterEq
from core.octopus.patterns.rainbowPlaidEqPattern import RainbowPlaidEqPattern
from core.octopus.patterns.lavaLampPattern import LavaLampPattern
from core.octopus.patterns.eqPattern import EqPattern
from core.octopus.patterns.spiralOutFast import SpiralOutFast
from core.octopus.patterns.spiralInFast import SpiralInFast


import time

import itertools
import random

class ShambalaPattern(Pattern):
    def __init__(self):
        self.patterns = [
            #RainbowPlaidEqPattern(),
            SpiralOutFast(),
            #SpiralInFast(),
            #LavaLampPattern(),
            EqPattern()
        ]

        self.last_transition = 0
        self.register_param("min_switch_time", 1, 200, 30)
        self.register_param("max_switch_time", 1, 200, 90)

        self.switch_time = self.next_switch_time()

        #Set thte first pattern, because it should switch on first iteration
        self.pattern_iterable = itertools.cycle(self.patterns)
        self.previous_pattern = next(self.pattern_iterable)
        self.current_pattern = next(self.pattern_iterable)

        self.pattern_dict = {}

    def next_switch_time(self):
        self.switch_time = self.min_switch_time + (self.max_switch_time - self.min_switch_time)*random.random()

    #Clone Army of Octopuses!
    def on_pattern_select(self, octopus):    
        for pattern in self.patterns:
            self.pattern_dict[pattern] = octopus.clone()

        self.previous_pattern.on_pattern_select(octopus)
        self.current_pattern.on_pattern_select(octopus)

    def next_frame(self, octopus, data):
        t = time.time()
        time_since_switch = t - self.last_transition

        colors = self.pixel_colors(self.current_pattern, data)
        pixels = octopus.pixels()
        for i in range(len(pixels)):
            pixels[i].color = colors[i]


        # The old switch-er-oo
        if time_since_switch > self.switch_time:
            self.last_transition = t
            self.previous_pattern = self.current_pattern

            self.current_pattern = next(self.pattern_iterable)
            current_octopus = self.pattern_dict[self.current_pattern]
            self.current_pattern.on_pattern_select(current_octopus)

            self.next_switch_time()

    def pixel_colors(self, pattern, data):
        octopus = self.pattern_dict[pattern]
        pattern.next_frame(octopus, data)

        return octopus.pixel_colors()

    def status(self):
        return self.current_pattern.__class__.__name__
        

