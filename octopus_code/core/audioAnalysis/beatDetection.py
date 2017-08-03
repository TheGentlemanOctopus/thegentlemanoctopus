import time

'''
BeatDetection class is used to track beats over time
'''
class BeatDetection():

    def __init__(self, channels, threshold=17, stretch=6, rising_step=10):

        self.threshold = threshold
        self.stretch = stretch
        self.rising_step = rising_step

        self.levelsBeat = []
        self.levelsLast = []
        self.levelsEdge = []

        for x in xrange(channels):
            self.levelsBeat.append(False)
            self.levelsLast.append(0)
            self.levelsEdge.append(False)

        timeOfLastBeat = 0.0
        timeSinceLastBeat = 0.0
        timeout = 5.0
        pass

    def detectBeat(self, levels):
        '''
        Simple beat detection by tracking rising edge, noting when it first rises.
        Currently serial/queue out is not enabled
        '''
        #[bass,kick,snare,hh,vocal]
        beat = False

        # print 'bd', levels
        

        ''' Itterate through level '''
        for x in xrange(len(levels)):
            ''' If new level > old level + stretch && new level > threshold 
                level is rising by enough to be a beat '''
            if (levels[x] > self.levelsLast[x]+self.stretch) and (self.levelsEdge[x] == False) and (levels[x] > self.threshold):
                self.levelsBeat[x] = True
                beat = True
                ''' If new level > old level + 2
                level is just rising '''
            elif (levels[x] > self.levelsLast[x]+self.rising_step):
                self.levelsEdge[x] = True
                self.levelsBeat[x] = False
                ''' level is not rising or a beat '''
            else:
                self.levelsEdge[x] = False
                self.levelsBeat[x] = False
            self.levelsLast[x] = levels[x]

        ''' remember time of last beat '''
        if beat:
            self.timeOfLastBeat = time.time()


        return self.levelsBeat

if __name__ == '__main__':

    bd = BeatDetection(7)
