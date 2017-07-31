from pattern import Pattern
import numpy as np
import itertools
import time
from random import randint

class EqPatternColourful(Pattern):
    def __init__(self, meter_color=(255,100,50), background_color=(0,50,255), decay_time = 0.1):
        self.register_param("meter_r", 0, 255, meter_color[0])
        self.register_param("meter_g", 0, 255, meter_color[1])
        self.register_param("meter_b", 0, 255, meter_color[2])

        self.register_param("bg_r", 0, 255, background_color[0])
        self.register_param("bg_g", 0, 255, background_color[1])
        self.register_param("bg_b", 0, 255, background_color[2])

        self.register_param("decay_time", 0, 1, decay_time)

        self.decay_number = 0
        self.decay_direction = 1
        self.prev_time = time.time()
    def meter_color(self):
        return (self.meter_r, self.meter_g, self.meter_b)

    def dynamic_meter_color(self,level):
        return (self.meter_g*np.cos(np.pi/2*level), self.meter_g*np.cos(np.pi/3*level), self.meter_b*np.cos(np.pi/4*level))

    def background_color(self):
        return (self.bg_r, self.bg_g, self.bg_b)

    def dynamic_background_color(self,level):
        return (self.bg_r, self.bg_g, self.bg_b)

    def next_frame(self, octopus, data):
        #meter_color = self.meter_color()

        eq = itertools.cycle(data.eq[3:6])



        for tentacle in octopus.tentacles:
            level = next(eq)



            for led_strip in tentacle.led_strips:

                meter_color = self.dynamic_meter_color(level)
                background_color = self.dynamic_background_color(level)
                pixel_colors = []

                n_meter_pixels = int(len(led_strip.pixels)*float(level))

                if time.time() - self.prev_time > self.decay_time:
                    if self.decay_number < len(led_strip.pixels):
                        self.decay_number += 1
                    elif self.decay_number > 0:
                        self.decay_number -= 1

                    self.prev_time = time.time()
                start_pixel = int(len(led_strip.pixels)-self.decay_number)
                pixel_colors.extend([background_color for x in range(0,start_pixel-1)])
                pixel_colors.extend([meter_color for x in range(start_pixel,n_meter_pixels)])

                n_background_pixels = len(led_strip.pixels) - n_meter_pixels
                pixel_colors.extend([background_color for x in range(n_background_pixels)])

                led_strip.put_pixels(pixel_colors)

