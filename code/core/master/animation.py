import numpy as np
import datetime

from core.cube.layout.panel import Panel

def map_range(value, OldMin, OldMax, NewMin,NewMax):
    OldRange = (OldMax - OldMin)  
    NewRange = (NewMax - NewMin)  
    NewValue = (((value - OldMin) * NewRange) / OldRange) + NewMin
    return max(min(255,NewValue),0)

class Animation():
    ''' Represents a chromatophore in octopusLayout space'''
    def __init__(self, frame_period=100, name='Animation'):
        ''' location is the coordinate of the pixel'''
        self.frame_period = frame_period
        self.name = name

    def next_frame(self):
        print 'Hello world!'


class Cube_animation(Animation):

    def __init__(self, cube_panels, frame_period=10, name='Cube Animation'):
        Animation.__init__(self,frame_period=frame_period, name=name)
        self.Panels = cube_panels


