from pattern import Pattern
import copy
import numpy as np
import random
import collections
from scipy.signal import convolve2d

#This is/was the start of a generalisation of the leaking patterns. Unfinished currently.
class GridPattern(Pattern):
    def __init__(self):
        self.register_param("blue", 0, 255, 100)
        self.register_param("grid_m", 0, 1, 0)
        #Leaks controls flow of color
        self.r_filter = np.array([[0.1, 0.1, 0.1], [0.1, 0.5, 0.1], [0.1, 0.1, 0.1]])
        self.g_filter = np.array([[0.1, 0.1, 0.1], [0.1, 0.5, 0.1], [0.1, 0.1, 0.1]])
        self.b_filter = np.array([[0.1, 0.1, 0.1], [0.1, 0.5, 0.1], [0.1, 0.1, 0.1]])

        self.grid_m = True

    def get_grids(self, r, g, b, pixel_count, leg_count):
        #Reshape pixel array to a numpy array

        if self.grid_m is True:
            #Array is (pixels_per_leg, n_legs)
            return (np.array(r).reshape((pixel_count/leg_count, leg_count)), 
            np.array(g).reshape((pixel_count/leg_count, leg_count)), 
            np.array(b).reshape((pixel_count/leg_count, leg_count)))
        else:
            #Array is (pixels_per_strip, n_strips)
            return np.array(pixels.reshape(pixel_count/(2*leg_count), 2*leg_count))

    def next_frame(self, octopus, data):

        pixels = [p.color for p in octopus.pixels()]
        r, g, b = zip(*pixels)
        pixel_count = len(pixels)
        leg_count = len(octopus.legs)

        (r, g, b) = self.get_grids(r, g, b, pixel_count, leg_count)

        #(ri, gi, bi) = self.apply_input(data)
        #(rp, gp, bp) = self.propagate(r, g, b)


    def apply_input(self, data):
        #This function takes the current pixel grid and updates it based on eq/level data
        return np.zeros((128, 8))

    def propagate(self, r, g, b):
        #This function creates a new grid based on propagating the old grid
        return (np.zeros(128, 8), np.zeros(128, 8), np.zeros(128, 8))
        #Create a dummy array to hold the new data - may be a better way to do this
        

#This was where I did my initial playing. Colors leak down legs(r, g, b leaks) and across legs (lleak)
#Leaks control speed of pattern -- close to 1 is pretty quick, around 0.1 is slow. 
#Dont set any leak much greater than 1 or you'll get exponential growth
#Majority should be <1
#Input is just scaled eq data
class SolidColorPattern(Pattern):
    def __init__(self):
        self.register_param("g_leak", 0, 1, 0.1)
        self.register_param("b_leak", 0, 1, 0.3)
        self.register_param("r_leak", 0, 1, 0.7)
        self.register_param("leg_leak", 0, 2, 1.01)
        self.register_param("p_reverse", 0, 0.1, 0.01)
        self.register_param("r_scale", 0, 5, 3)
        self.register_param("g_scale", 0, 5, 2)
        self.register_param("b_scale", 0, 5, 3)
        self.step = 1


    def next_frame(self, octopus, data):
        level = data["level"]
        eq = data["eq"]
        
        g_leak = self.g_leak
        r_leak = self.r_leak
        b_leak = self.b_leak
        ll = self.leg_leak
        leaks = (r_leak, g_leak, b_leak)

        for (i, l) in enumerate(octopus.legs):
            if random.random() > (1-self.p_reverse):
                self.step *= -1
            for (j, pixel) in enumerate(l.pixels()[::self.step]):
                if (j==0):
                    pixel.color = (self.r_scale*(eq[0]*255.), self.g_scale*((eq[1]+eq[2]+eq[3])*255), self.b_scale*((eq[4]+eq[5]+eq[6])*255))
                    prev_pixel = pixel.color
                else:
                    temp = copy.deepcopy(pixel.color)
                    pixel.color = [((v*l*(ll**i)) + (1-(l*ll**i))*p) for (p, v, l) in zip(pixel.color, prev_pixel, leaks)]
                    prev_pixel = copy.deepcopy(temp)


def threshold(inp, threshold):
    if inp>(threshold):
        return 255
    else:
        return inp

#Same as above but input is thresholded.
class PulseOut(Pattern):

    def __init__(self):
        self.register_param("r", 0, 0.5, 0.1)
        self.register_param("b", 0, 0.5, 0.05)
        self.register_param("g", 0, 0.5, 0.02)
        self.step = 1
        self.g_leak = 0.75
        self.r_leak = 0.90
        self.b_leak = 0.45


    def next_frame(self, octopus, data):
        level = data["level"]
        eq = data["eq"]
        

        ll = 1.001
        r_threshold = 0.8
        g_threshold = 0.3
        b_threshold = 0.2

        if random.random() > 0.99:
            self.step *= -1

        if random.random() > 0.98:
            self.r_leak += 0.01

        if random.random() > 0.98:
            self.g_leak += 0.01

        if random.random() > 0.98:
            self.b_leak += 0.01

        if random.random() > 0.98:
            self.r_leak -= 0.01

        if random.random() > 0.98:
            self.g_leak -= 0.01

        if random.random() > 0.98:
            self.b_leak -= 0.01
            
        leaks = (self.r_leak, self.g_leak, self.b_leak)


        for (i, l) in enumerate(octopus.legs):
            for (j, pixel) in enumerate(l.pixels()[::self.step]):
                if (j==0):
                    pixel.color = (threshold(eq[0]+eq[1], self.r), threshold(eq[2]+eq[3], self.g), threshold(eq[4]+eq[5]+eq[6], self.b))
                    prev_pixel = pixel.color
                else:
                    temp = copy.deepcopy(pixel.color)
                    pixel.color = [((v*l*(ll**i)) + (1-(l*ll**1))*p) for (p, v, l) in zip(pixel.color, prev_pixel, leaks)]
                    prev_pixel = copy.deepcopy(temp)

#Same as above but instead of leaking down the leg, the red channel spirals out. 
class SpiralOut(Pattern):
    def __init__(self):
        self.register_param("r_scale", 0, 5, 0)
        self.register_param("g_scale", 0, 5, 0)
        self.register_param("b_scale", 0, 20, 10)
        self.step = 1
        self.multiplier = 1
        self.spiral_step = 1

    def next_frame(self, octopus, data):
        level = data["level"]
        eq = data["eq"]

        g_leak = 0.95
        r_leak = 0.9
        b_leak = 0.8
        leaks = (r_leak, g_leak, b_leak)

        pixels = octopus.pixels()
        if random.random() > 0.99:
            self.spiral_step *= 1
        pixel_array = np.array(pixels)[::self.spiral_step].reshape(16, len(pixels)/16)

        for (r, c) in np.ndindex(len(pixels)/16, 16):
            pixel = pixel_array[(c, r)]
            if (r, c) == (0, 0):
                #pixel.color = ((eq[0]+eq[1]), scale*(eq[2]+eq[3]), scale*(eq[4]+eq[5]+eq[6]))
                pixel.color = (self.r_scale*(255.*(eq[0])), pixel.color[1], pixel.color[2])
                prev_pixel = pixel.color
            else:
                temp = copy.deepcopy(pixel.color)
                pixel.color = [((prev_pixel[0]*leaks[0]) + (1-leaks[0])*pixel.color[0]), pixel.color[1], pixel.color[2]]
                prev_pixel = copy.deepcopy(temp)

        for (i, l) in enumerate(octopus.legs):
            if random.random() > 0.999:
                self.step *= -1
            for (j, pixel) in enumerate(l.pixels()[::self.step]):
                if (j==0):
                    pixel.color = (pixel.color[0], self.g_scale*(255.*(eq[2]+eq[1])), pixel.color[2])
                    prev_pixel = pixel.color
                else:
                    temp = copy.deepcopy(pixel.color)
                    pixel.color = [pixel.color[0], ((prev_pixel[1]*leaks[1]) + (1-leaks[1])*pixel.color[1]), pixel.color[2]]
                    prev_pixel = copy.deepcopy(temp)

        for (i, l) in enumerate(octopus.legs):
            if random.random() > 0.999:
                self.multiplier*= -1
            for (j, pixel) in enumerate(l.pixels()[::self.step*self.multiplier]):
                if (j==0):
                    pixel.color = (pixel.color[0], pixel.color[1], self.b_scale*(255.*(eq[3]+eq[4]+eq[5]+eq[6])))
                    prev_pixel = pixel.color
                else:
                    temp = copy.deepcopy(pixel.color)
                    pixel.color = [pixel.color[0], pixel.color[1], ((prev_pixel[2]*leaks[2]) + (1-leaks[2])*pixel.color[2])]
                    prev_pixel = copy.deepcopy(temp)

#This was an idea that didnt really work out. Could remove.
class SpiralOutFast(Pattern):
    def __init__(self):
        self.register_param("dummy", 0, 1, 0)

    def next_frame(self, octopus, data):
        level = data["level"]
        eq = data["eq"]

        g_leak = 0.95
        r_leak = 0.90
        b_leak = 0.95
        leaks = (r_leak, g_leak, b_leak)

        pixels = octopus.pixels()
        pixel_array = np.array(pixels).reshape(8, len(pixels)/8)
        temps = collections.deque()
        for (r, c) in np.ndindex(len(pixels)/8, 8):
            pixel = pixel_array[(c, r)]
            if r == 0 and c < 4:
                pixel.color = (int(255.*(eq[0]+eq[1])), int(255.*(eq[2]+eq[3])), int(255.*(eq[4]+eq[5]+eq[6])))
                temps.appendleft(copy.deepcopy(pixel.color))
            else:
                temps.appendleft(copy.deepcopy(pixel.color))
                pixel.color = [((v*l) + (1-l)*p) for (p, v, l) in zip(pixel.color, temps.pop(), leaks)]

#same as above
class IntegrateF(Pattern):
    def __init__(self):
        self.register_param('r', 0, 10, 2)
        self.register_param('g', 0, 10, 3)
        self.register_param('b', 0, 10, 4)

        self.r_int = 0
        self.g_int = 0
        self.b_int = 0

    def next_frame(self, octopus, data):
        level = data["level"]
        eq = data["eq"]

        self.r_int += eq[0] + eq[1]
        self.b_int += eq[2]+eq[3]
        self.g_int += np.sum(eq[4:])

        g_leak = 0.35
        r_leak = 0.30
        b_leak = 0.35

        leaks = (r_leak, g_leak, b_leak)
        zero_color = self.fire()

        for l in octopus.legs:
            for (i, pixel) in enumerate(l.pixels()[::-1]):
                if (i==0):
                    pixel.color = zero_color
                    prev_pixel = pixel.color
                else:
                    temp = copy.deepcopy(pixel.color)
                    pixel.color = [(v*l) + ((1-l)*p) for (p, v, l) in zip(pixel.color, prev_pixel, leaks)]
                    prev_pixel = copy.deepcopy(temp)

    def fire(self):
        r_val = 0
        g_val = 0
        b_val = 0
        if self.r_int > self.r:
            r_val = 255
            self.r_int = 0
        if self.g_int > self.g:
            g_val = 255
            self.g_int = 0
        if self.b_int > self.b:
            b_val = 255
            self.b_int = 0

        return (r_val, g_val, b_val)

#This makes the first leg an EQ and then helicopters the EQ around. 
class HelicopterEq(Pattern):

    def __init__(self, meter_color=(255,255,255), background_color=(0,0,0)):
        self.register_param("meter_r", 0, 255, meter_color[0])
        self.register_param("meter_g", 0, 255, meter_color[1])
        self.register_param("meter_b", 0, 255, meter_color[2])

        self.register_param("bg_r", 0, 255, background_color[0])
        self.register_param("bg_g", 0, 255, background_color[1])
        self.register_param("bg_b", 0, 255, background_color[2])

        self.ws = [0.5, 0.3, 0.1]

    def meter_color(self):
        return (self.meter_r, self.meter_g, self.meter_b)

    def background_color(self):
        return (self.bg_r, self.bg_g, self.bg_b)


    def pixel_add(self, old_c, new_c):
        return [(o*(1.-w))+(n*w) for (o, n, w) in zip(old_c, new_c, self.ws)]

    def next_frame(self, octopus, data):

        leg = octopus.legs[0]
        pixel_colors = []

        for i in range(len(data["eq"])):
            #This is a quick hacky scaling that works fairly well
            level = (i+1)**2*data["eq"][i]

            for led_strip in leg.led_strips:

                n_meter_pixels = int(len(led_strip.pixels)*(float(level)) * (1./len(data["eq"])))
                pixel_colors.extend([self.meter_color() for x in range(n_meter_pixels)])

                n_background_pixels = int((1./len(data["eq"])) * len(led_strip.pixels)) - n_meter_pixels
                pixel_colors.extend([self.background_color() for x in range(n_background_pixels)])

                led_strip.put_pixels(pixel_colors)

        old_leg = copy.deepcopy(leg)

        for leg in octopus.legs[1:]:
            temp = copy.deepcopy(leg)
            for (i, led_strip) in enumerate(leg.led_strips):
                led_strip.put_pixels([self.pixel_add(o.color, p.color) for (o,p) in zip(led_strip.pixels, old_leg.led_strips[i].pixels)])
            old_leg = copy.deepcopy(temp)


class ConwayPattern(Pattern):
    def __init__(self):
        self.register_param("alive", 0, 9, 3)
        self.register_param("dead", 0, 9, 3)

    def next_frame(self, octopus, data):
        level = data["level"]
        eq = data["eq"]

        old_grid = np.array(octopus.pixels()).reshape(16, 64)
        new_grid = np.zeros((16, 64))

        for pos in np.ndindex(16, 64):
            new_grid[pos] = is_alive(old_grid[pos])