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

    def next_frame(self, audio_data):
        self.react_to_audio(audio_data)


        self.clear_pixels()

        ch = [max(min(int(i/10), 5), 0) for i in audio_data[:5] ]
        for panel in self.Panels:
            panel.vu_to_rows(ch)


    def clear_pixels(self):
        for panel in self.Panels:
            panel.clear_pixels()

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

    def __init__(self, cube_panels, frame_period=10, name='vu_to_rows'):
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

