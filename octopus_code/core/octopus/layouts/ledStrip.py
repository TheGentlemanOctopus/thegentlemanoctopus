import numpy as np
from pixel import Pixel

class LedStrip:
    ''' Represents a strip of addressable leds with nPixels (chromatophores) '''
    def __init__(self, base, length, direction, nPixels):
        ''' base is the coordinate of the base pixel
            length is the length of the strip
            dirrection is a vector of linear strip direction]
        '''
        self.base = base
        self.length = length
        self.direction = direction/np.linalg.norm(direction)
        
        dP = (self.length/float(nPixels - 1)) * self.direction
        self.pixels = [Pixel(self.base + i*dP) for i in range(nPixels)]

    #Always starting from the base, excess pixels/colored are ignored
    def put_pixels(self, colors):
        for i in range(np.min([len(self.pixels), len(colors)])):
            self.pixels[i].color = colors[i]