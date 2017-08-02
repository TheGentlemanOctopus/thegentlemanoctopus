import numpy as np
from pixel import Pixel

class Mantle:
    """Mantle is orientated near the x-z plane
    pixels are ordered in a zig-zag
    TODO: Is this aligned with the convention for tentacles? 
    TODO: radial led objects
    """
    def __init__(self, radius, pixels_per_strip):
        self.radius = radius
        self.pixels_per_strip = pixels_per_strip

        # Form Pixels
        self.pixels = []
        theta = np.linspace(0, np.pi, pixels_per_strip)

        # Get coordinates
        x = np.cos(theta)
        y = np.zeros(len(theta))
        z = np.sin(theta)

        # How much to rotate the led strips by (about z axis)
        dtheta = np.pi/16.0
        
        # First strip of leds, anticlockwise rotation
        cos_anti = np.cos(dtheta)
        sin_anti = np.sin(dtheta)

        x_anti = cos_anti*x - sin_anti*y
        y_anti = sin_anti*x + cos_anti*y

        for i in range(len(x)):
            self.pixels.append(Pixel(np.array([x_anti[i], y_anti[i], z[i]])))

        # Second strip of leds, clockwise rotation
        cos_clock = np.cos(np.pi-dtheta)
        sin_clock = np.sin(np.pi-dtheta)

        x_clock = cos_clock*x - sin_clock*y
        y_clock = sin_clock*x + cos_clock*y

        for i in range(len(x)):
            self.pixels.append(Pixel(np.array([x_clock[i], y_clock[i], z[i]])))

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    mantle = Mantle(1, 32)

    x = [pixel.location[0] for pixel in mantle.pixels]
    y = [pixel.location[1] for pixel in mantle.pixels]
    z = [pixel.location[2] for pixel in mantle.pixels]

    plt.scatter(x,y,z)
    plt.show()