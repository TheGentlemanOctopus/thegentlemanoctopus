from pattern import Pattern
import itertools
import random
import colorsys
import time

class EqPattern(Pattern):
    def __init__(self, meter_color=(255,100,50), background_color=(0,50,255)):
        self.meter_r = meter_color[0]
        self.meter_g = meter_color[1]
        self.meter_b = meter_color[2]

        self.bg_r = background_color[0]
        self.bg_g = background_color[1]
        self.bg_b = background_color[2]

        # TODO: delete?
        # self.register_param("meter_r", 0, 255, meter_color[0])
        # self.register_param("meter_g", 0, 255, meter_color[1])
        # self.register_param("meter_b", 0, 255, meter_color[2])

        # self.register_param("bg_r", 0, 255, background_color[0])
        # self.register_param("bg_g", 0, 255, background_color[1])
        # self.register_param("bg_b", 0, 255, background_color[2])

        self.register_param("max_hue_shift", 0, 0.5, 0.2)
        self.register_param("beat_channel", 0, 6, 2)

        self.register_param("max_bpm", 0, 200, 100)

        self.register_param("prob_shift", 0, 1, 100)

        self.next_shift = time.time()


    def meter_color(self):
        return (self.meter_r, self.meter_g, self.meter_b)

    def background_color(self):
        return (self.bg_r, self.bg_g, self.bg_b)

    # TODO: put this into utils or something
    def hue_shift(self, color, hue_shift):
        color_scaled = [x/255.0 for x in color]
        hsv = list(colorsys.rgb_to_hsv(color_scaled[0], color_scaled[1], color_scaled[2]))
        hsv[0] += hue_shift % 1

        return tuple([int(x*255) for x in colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])])


    def next_frame(self, octopus, data):
        beat_channel = int(round(self.beat_channel))

        t = time.time()
        if data.beats[beat_channel] and t > self.next_shift:
            self.next_shift = t + 60.0/self.max_bpm

            shift = self.max_hue_shift*(2*random.random() - 1)

            if int(round(random.random())):
                self.meter_r, self.meter_g, self.meter_b = self.hue_shift(self.meter_color(), shift)
            else:
                self.bg_r, self.bg_g, self.bg_b = self.hue_shift(self.background_color(), shift)

        meter_color = self.meter_color()
        background_color = self.background_color()


        eq = itertools.cycle(data.eq)

        for tentacle in octopus.tentacles:
            level = next(eq)

            for led_strip in tentacle.led_strips:
                pixel_colors = []

                n_meter_pixels = int(len(led_strip.pixels)*float(level))
                pixel_colors.extend([meter_color for x in range(n_meter_pixels)])

                n_background_pixels = len(led_strip.pixels) - n_meter_pixels
                pixel_colors.extend([background_color for x in range(n_background_pixels)])

                led_strip.put_pixels(pixel_colors)
