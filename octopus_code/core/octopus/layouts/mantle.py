import numpy as np
from pixel import Pixel

class Mantle:
    """Mantle always orientated in x-z plane"""
    def __init__(self, radius, pixels_per_strip):
        self.radius = radius
        self.pixels_per_strip = pixels_per_strip

        self.pixels = []
        theta = np.linspace(0, np.pi, pixels_per_strip)
        x = np.cos(theta)
        y = np.zeros(len(theta))
        z = np.sin(theta)

        dtheta = np.pi/16.0
        cos_anti = np.cos(dtheta)
        sin_anti = np.sin(dtheta)

        x_anti = cos_anti*x - sin_anti*y
        y_anti = sin_anti*x + cos_anti*y

        for i in range(len(x)):
            self.pixels.append(Pixel(np.array([x_anti[i], y_anti[i], z[i]])))

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