from pattern import Pattern
import itertools

class EqPattern(Pattern):
    def __init__(self, meter_color=(255,100,50), background_color=(0,50,255)):
        self.register_param("meter_r", 0, 255, meter_color[0])
        self.register_param("meter_g", 0, 255, meter_color[1])
        self.register_param("meter_b", 0, 255, meter_color[2])

        self.register_param("bg_r", 0, 255, background_color[0])
        self.register_param("bg_g", 0, 255, background_color[1])
        self.register_param("bg_b", 0, 255, background_color[2])

    def meter_color(self):
        return (self.meter_r, self.meter_g, self.meter_b)

    def background_color(self):
        return (self.bg_r, self.bg_g, self.bg_b)

    def next_frame(self, octopus, data):
        meter_color = self.meter_color()
        background_color = self.background_color()

        eq = itertools.cycle(data["eq"])

        for leg in octopus.legs:
            level = next(eq)

            for led_strip in leg.led_strips:
                pixel_colors = []

                n_meter_pixels = int(len(led_strip.pixels)*float(level))
                pixel_colors.extend([meter_color for x in range(n_meter_pixels)])

                n_background_pixels = len(led_strip.pixels) - n_meter_pixels
                pixel_colors.extend([background_color for x in range(n_background_pixels)])

                led_strip.put_pixels(pixel_colors)
