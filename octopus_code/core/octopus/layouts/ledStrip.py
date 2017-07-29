import numpy as np
from pixel import Pixel

class LedStrip:
    def __init__(self, base, length, direction, nPixels):
        self.base = base
        self.length = length
        self.direction = direction/np.linalg.norm(direction)
        
        dP = (self.length/float(nPixels - 1)) * self.direction
        self.pixels = [Pixel(self.base + i*dP) for i in range(nPixels)]

    #Always starting from the base, excess pixels/colored are ignored
    def put_pixels(self, colors):
        for i in range(np.min([len(self.pixels), len(colors)])):
            self.pixels[i].color = colors[i]