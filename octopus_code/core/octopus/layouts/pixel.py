import numpy as np

class Pixel:
    ''' Represents a chromatophore in octopusLayout space'''
    def __init__(self, location, color=(0,0,0)):
        ''' location is the coordinate of the pixel'''
        self.location = location
        self.color = color

    def set_color(self, color):
        self.color = color

    # Rotate your location around the origin
    def rotate(self, degrees):
        theta = np.radians(degrees)

        # Rotation Matrix
        c = np.cos(theta)
        s = np.sin(theta)

        R = np.array([[c, -s, 0], [s, c, 0], [0,0,1]])

        self.location = R.dot(self.location)

    def radius(self):
        return np.linalg.norm(self.location)

    def set_radius(self, r):
        _, theta = self.polar_location()
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        self.location = np.array([x, y, self.location[2]])

    def polar_location(self):
        r = np.linalg.norm(self.location)
        theta = np.arctan2(self.location[1], self.location[0])

        return (r, theta)

if __name__ == '__main__':
    pixel = Pixel(np.array([1,0,0]))

    print "Pixel Location", pixel.location

    pixel.rotate(90)
    print "location after 90 degree rotation", pixel.location
