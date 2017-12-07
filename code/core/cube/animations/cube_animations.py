import numpy as np
import datetime

from core.cube.layout.panel import Panel
from core.master.animation import Cube_animation

def map_range(value, OldMin, OldMax, NewMin,NewMax):
    OldRange = (OldMax - OldMin)  
    NewRange = (NewMax - NewMin)  
    NewValue = (((value - OldMin) * NewRange) / OldRange) + NewMin
    return max(min(255,NewValue),0)

class Vu_to_rows(Cube_animation):

    def __init__(self, cube_panels, frame_period=10, name='vu_to_rows'):
        Cube_animation.__init__(self, cube_panels, frame_period=frame_period, name=name)
        self.hue_start = 0.0

    def next_frame(self, audio_data):
        self.react_to_audio(audio_data)
        self.clear_pixels()

        self.hue_start += 0.002
        hue_range = 0.8

        max_val = 5
        threshold = 2
        division = 6

        ''' map audio to 0-5 '''
        ch = [max(min(int((i-threshold)/division), max_val), 0) for i in audio_data[:5] ]
        ''' map channel colour to 0.0 -> 1.0 and add offset '''
        hues = [ (self.hue_start+self.translate(i,0,5,0.0,hue_range))%1.0 for i in ch] 

        for panel in self.Panels:
            panel.vu_to_rows(ch,hues)

        # self.Panels[0].vu_to_rows(ch,hues)


    def clear_pixels(self):
        for panel in self.Panels:
            panel.clear_pixels()

    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

    def react_to_audio(self, audio_data):
        # print type(audio_data)
        val = map_range(audio_data[1]*2,0,100,0.2,1.0)
        # print val
        for p in self.Panels:
            p.set_val(val)

        beats = audio_data[5:]
        if beats[0] == 'A':
            self.Panels[0].shift_hue(0.01)
        if beats[2] == 'C':
            self.Panels[1].shift_hue(0.02)
        if beats[4] == 'D':
            self.Panels[2].shift_hue(0.06)
        pass

class Shift(Cube_animation):

    def __init__(self, cube_panels, frame_period=100, name='vu_to_rows'):
        Cube_animation.__init__(self, cube_panels, frame_period=frame_period, name=name)
        self.hue = 0

    def next_frame(self, audio_data):
        self.react_to_audio(audio_data)

        self.clear_pixels()
        self.set_hue()

        self.shift_col()
        self.shift_row()


    def set_hue(self):
        for panel in self.Panels:
            panel.shift_hue()


    def clear_pixels(self):
        for panel in self.Panels:
            panel.clear_pixels()

    def shift_col(self):
        for panel in self.Panels:
            panel.shift_pixel()


    def shift_row(self):
        for panel in self.Panels:
            panel.shift_row()

    def react_to_audio(self, audio_data):
        # print type(audio_data)
        val = map_range(audio_data[1]*2,0,100,0.2,1.0)
        # print val
        for p in self.Panels:
            p.set_val(val)

        # beats = audio_data[5:]
        # if beats[0] == 'A':
        #     self.Panels[0].shift_hue(0.01)
        # if beats[2] == 'C':
        #     self.Panels[1].shift_hue(0.02)
        # if beats[4] == 'D':
        #     self.Panels[2].shift_hue(0.06)
        # pass

class Spin_cross(Cube_animation):

    def __init__(self, cube_panels, frame_period=10, name='vu_to_rows'):
        Cube_animation.__init__(self, cube_panels, frame_period=frame_period, name=name)
        self.hue = 0

    def next_frame(self, audio_data):
        
        self.clear_pixels()
        self.set_hue()


    def set_hue(self):
        for panel in self.Panels:
            panel.shift_hue()


    def clear_pixels(self):
        for panel in self.Panels:
            panel.clear_pixels()



    

class Vu_to_ring(Cube_animation):

    def __init__(self, cube_panels, frame_period=10, name='vu_to_ring'):
        Cube_animation.__init__(self, cube_panels, frame_period=frame_period, name=name)
        # print 'vu_to_ring'

    def next_frame(self, audio_data):
        # print 'vu to ring next frame'

        for panel in self.Panels:
            panel.clear_pixels()

        self.Panels[0].shift_hue(step=0.01)
        self.Panels[1].shift_hue(step=0.015)
        self.Panels[2].shift_hue(step=0.025)

        max_val = 3
        threshold = 10
        division = 8

        ch = [max(min(int((i-threshold)/division), max_val), 0) for i in audio_data[:5] ]
        # print audio_data[2], ch[2]

        self.Panels[0].set_ring(ch[0])
        self.Panels[1].set_ring(ch[2])
        self.Panels[2].set_ring(ch[4])

class Vu_to_rect(Cube_animation):

    def __init__(self, cube_panels, frame_period=10, name='vu_to_ring'):
        Cube_animation.__init__(self, cube_panels, frame_period=frame_period, name=name)
        # print 'vu_to_ring'

    def next_frame(self, audio_data):
        # print 'vu to ring next frame'

        for panel in self.Panels:
            panel.clear_pixels()

        self.Panels[0].shift_hue(step=0.01)
        self.Panels[1].shift_hue(step=0.015)
        self.Panels[2].shift_hue(step=0.025)

        max_val = 3
        threshold = 10
        division = 8

        ch = [max(min(int((i-threshold)/division), max_val), 0) for i in audio_data[:5] ]
        # print audio_data[2], ch[2]

        self.Panels[0].set_rect(ch[0])
        self.Panels[1].set_rect(ch[2])
        self.Panels[2].set_rect(ch[4])

class Vu_to_spiral_out(Cube_animation):

    def __init__(self, cube_panels, frame_period=10, name='vu_to_ring'):
        Cube_animation.__init__(self, cube_panels, frame_period=frame_period, name=name)
        # print 'vu_to_ring'
        self.range = cube_panels[0].nPixels

    def next_frame(self, audio_data):
        # print 'vu to ring next frame'

        for panel in self.Panels:
            panel.clear_pixels()

        self.Panels[0].shift_hue(step=0.01)
        self.Panels[1].shift_hue(step=0.015)
        self.Panels[2].shift_hue(step=0.025)

        max_val = 1.0
        threshold = 15
        division = 16

        ch = [max(min(((i-threshold)/division), max_val), 0) for i in audio_data[:5] ]
        # print audio_data[2], ch[2]
        # print ch[0], audio_data[0] 
        self.Panels[0].draw_spiral_out(ch[0])
        self.Panels[1].draw_spiral_out(ch[2])
        self.Panels[2].draw_spiral_out(ch[4])



