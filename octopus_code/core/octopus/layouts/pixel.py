import numpy as np

class Pixel:
    ''' Represents a chromatophore in octopusLayout space'''
    def __init__(self, location, color=(0,0,0)):
        ''' location is the coordinate of the pixel'''
        self.location = np.array(location)
        self.color = color

    def set_color(self, color):
        self.color = color

    # Rotate your location around the origin
    def rotate(self, degrees):
        theta = np.radians(degrees)
        print "theta", theta

        # Rotation Matrix
        c = np.cos(theta)
        s = np.sin(theta)

        R = np.array([[c, -s], [s, c]])

        print "Rotation matri", R

        self.location = R.dot(self.location)

if __name__ == '__main__':
    pixel = Pixel((1,0))

    print "Pixel Location", pixel.location

    pixel.rotate(90)
    print "location after 90 degree rotation", pixel.location
