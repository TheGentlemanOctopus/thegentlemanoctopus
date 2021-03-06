import time
import numpy as np
import sys

# For a 7 band eq
class PatternStreamData:
    def __init__(self, level=0, eq=(0,0,0,0,0,0,0), rhythm_channel=0, beats=[False, False, False, False, False, False, False]):
        self.level = level
        self.eq = eq
        self.rhythm_channel = rhythm_channel
        self.beats = beats

    def set_eq(self, eq):
        self.eq = eq
        self.level = eq[self.rhythm_channel]

    #TODO: these checks are unnecessary when auidoDetection links up with my integrationTests
    def set_beats(self, beats):

        self.beats = [False for i in range(7)]

        for i in range(min([7, len(beats)])):
            self.beats[i] = beats[i]


    def siney_time(self, frequency=1.0/5):
        t = time.time()
        phase = np.linspace(0, 2*np.pi, 7)
        freqs = frequency * np.ones(7)

        eq = tuple(0.5+0.5*np.sin(2*np.pi*freqs*t + phase))
        
        self.set_eq(eq)


# Siney Time Demo
if __name__ == '__main__':
    pattern_stream_data = PatternStreamData()

    start_time = time.time()
    print ""
    while time.time() - start_time < 5:
        pattern_stream_data.siney_time()

        count = 0
        print "Bands |",
        for band in pattern_stream_data.eq:
            print "|", "(%.2f)" % band,
            count += 1

        print ""
