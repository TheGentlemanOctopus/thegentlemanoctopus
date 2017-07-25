import xmlrpclib
import numpy as np
from pattern import Pattern

#Change the brightness of the octopus
class RpcTestPattern(Pattern):
    def __init__(self):
        self.register_param("red", 0, 255, 255)
        self.register_param("green", 0, 255, 255)
        self.register_param("blue", 0, 255, 255)
    
    def next_frame(self, octopus, data):
        r = int(self.red*data.eq[0])
        g = int(self.green*data.eq[1])
        b = int(self.blue*data.eq[2])

        for pixel in octopus.pixels():
            pixel.color = (r,g,b)

if __name__ == '__main__':
    s = xmlrpclib.ServerProxy('http://localhost:8000')
    
    print "Enter a brightness level between 0-255"
    while True:
        s.put({"level": raw_input("Brightness: ")})