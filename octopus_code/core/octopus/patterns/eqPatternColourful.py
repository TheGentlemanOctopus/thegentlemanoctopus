from pattern import Pattern
import numpy as np
import itertools
import time
from random import randint

class EqPatternColourful(Pattern):
    def __init__(self, meter_color=(255,100,50), background_color=(0,50,255), decay_time = 0.1):

        self.register_param("eq_r", 0, 10, 2)
        self.register_param("eq_g", 0, 10, 1)
        self.register_param("eq_b", 0, 10, 1.5)

        self.register_param("bg_r", 0, 10, 1)
        self.register_param("bg_g", 0, 10, 1.5)
        self.register_param("bg_b", 0, 10, 2)

        self.register_param("decay_time", 0, 1, decay_time)

        self.prev_time = time.time()

    def dynamic_meter_color(self,level):
        # Sine Time
        r = 255*0.5*(1+np.sin(2*np.pi*level*self.eq_r))
        g = 255*0.5*(1+np.sin(2*np.pi*level*self.eq_g))
        b = 255*0.5*(1+np.sin(2*np.pi*level*self.eq_b))
        return (r, g, b)


    def dynamic_background_color(self,level):
        # Sine Time
        r = 255*0.5*(1+np.cos(2*np.pi*level*self.eq_r))
        g = 255*0.5*(1+np.cos(2*np.pi*level*self.eq_g))
        b = 255*0.5*(1+np.cos(2*np.pi*level*self.eq_b))
        return (r, g, b)

    def on_pattern_select(self, octopus):
        self.decay_direction = [1 for x in range(len(octopus.tentacles))]
        self.decay_number = [0 for x in range(len(octopus.tentacles))]

    def next_frame(self, octopus, data):
        #meter_color = self.meter_color()

        eq = itertools.cycle(data.eq[3:6])



        for tent_ind, tentacle in enumerate(octopus.tentacles):
            level = next(eq)


            for led_strip in tentacle.led_strips:
                
                time_difference = time.time() - self.prev_time
                meter_color = self.dynamic_meter_color(level)
                background_color = self.dynamic_background_color(level)
                pixel_colors = []

                n_meter_pixels = int(len(led_strip.pixels)*float(level))

                #print "level", level
                
                #print "td", time_difference
                if time_difference > (1-level)+self.decay_time:
                    if ((self.decay_number[tent_ind] < len(led_strip.pixels))):
                        self.decay_number[tent_ind] += 1
                    else:
                        self.decay_number[tent_ind] = 0 

#                    if ((self.decay_number[tent_ind] < len(led_strip.pixels)) and (self.decay_direction[tent_ind])):
#                        self.decay_number[tent_ind] += 1
#                    elif ((self.decay_number[tent_ind] > 0) and (self.decay_direction[tent_ind] == 0)):
#                        self.decay_number[tent_ind] -= 1
#                    elif ((self.decay_number[tent_ind] == 0) or (self.decay_number[tent_ind] == len(led_strip.pixels)-1)):
#                        self.decay_direction[tent_ind] = self.decay_direction[tent_ind]^1

                    self.prev_time = time.time()
                start_pixel = int(len(led_strip.pixels)-self.decay_number[tent_ind])
                pixel_colors.extend([background_color for x in range(0,start_pixel)])
                pixel_colors.extend([meter_color for x in range(start_pixel,n_meter_pixels)])

                n_background_pixels = len(led_strip.pixels) - n_meter_pixels
                pixel_colors.extend([background_color for x in range(n_background_pixels)])

                led_strip.put_pixels(pixel_colors)

