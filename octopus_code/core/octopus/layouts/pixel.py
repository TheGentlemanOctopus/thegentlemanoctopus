class Pixel:
    ''' Represents a chromatophore in octopusLayout space'''
    def __init__(self, location, color=(0,0,0)):
        ''' location is the coordinate of the pixel'''
        self.location = location
        self.color = color