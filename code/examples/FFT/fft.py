
import pyaudio # from http://people.csail.mit.edu/hubert/pyaudio/
import numpy as np
import wave
import struct
import math
import os
import platform
import time
import random
# from core.Serial import SerialThread as serial
import sys
import xmlrpclib

# python -m core.testwav -f=sounds/DaftPunk.wav -d=True -s=2048 

# Modes:
# - vu meter
# - random state driven by beat
# - on/off frequency power threshold


class fft():

    levelsLast = [0,0,0,0,0]
    levelsEdge = [False,False,False,False,False]
    levelsBeat = [False,False,False,False,False]
    chStatus = ['a','b','c','d','e']

    threshold = 17

    timeOfLastBeat = 0.0
    timeSinceLastBeat = 0.0
    timeout = 5.0

    mood = 0
    moodTime = 0.0

    host = 'localhost'
    port = '8000'

    def __init__(self, datasize=2048,mic=None,debug=False,fname="../sounds/test.wav",frate=44100.0, output=False,threshold=17,stretch=4):
        
        print "setup args"
        self.threshold = threshold
        self.stretch = stretch
        self.timeOfLastBeat = time.time()
        self.moodTime = self.timeOfLastBeat

        self.s = xmlrpclib.ServerProxy('http://' + self.host + ':' + self.port)
        print self.s.system.listMethods()

        self.s.test(255,0,0)

        print "detect music"
        self.detectMusic(datasize,mic,debug,fname,frate, output)



        pass


    def detectMusic(self,datasize=2048,mic=None,debug=False,fname="../sounds/test.wav",frate=44100.0,output=False):

        cellFRange = frate / datasize
        p = pyaudio.PyAudio()

        print "choose input"

        # get wav stream in or to work output
        if mic != False:
            # get mic stream 
            # self.list_devices()
            if platform.system() == "Darwin": device = 0
            else: device = 1
            # device = 0
            print "using device", device
            # stream = self.p.open(format = pyaudio.paInt16, rate = 1, input = True, frames_per_buffer = datasize, input_device_index = device)   
            # stream = self.p.open(format = pyaudio.paInt16, channels = 1, rate = 44100, input = True, frames_per_buffer = datasize, input_device_index = device)
            # stream = self.p.open(format = pyaudio.paInt16, channels = 1, rate = 44100, input = True, frames_per_buffer = 1024, input_device_index = 1)
    

            # stream = self.p.open(rate=44100, channels=1, input=True, output=False, input_device_index=1, format=pyaudio.paInt16, frames_per_buffer=1024)
    
            stream = p.open(rate=44100, channels=1, input=True, output=False, format=pyaudio.paInt16, frames_per_buffer=1024)

            print "open audio"
        else: 
            # get wav stream
            print "playing file:", fname
            stream = wave.open(fname, 'rb')
            # stream = wave.open("../../sounds/DaftPunk.wav", 'rb')    

        if output != False:
            print "Setting up output"
            print stream.getsampwidth(), stream.getnchannels(), stream.getframerate()
            streamop = p.open(format=p.get_format_from_width(stream.getsampwidth()),
                    channels=stream.getnchannels(),
                    rate=stream.getframerate(),
                    output=True)
            # streamop = p.open(format=p.get_format_from_width(stream.getsampwidth()),
            #         channels=stream.getnchannels(),
            #         rate=stream.getframerate(),
            #         output=True)

        # start loop
        print "Starting, use Ctrl+C to stop"


        try: 
            while True:
                try:

                    # print ('tick')
                    # Get chunk of audio data from stream
                    if mic:
                        data = stream.read(datasize)
                    else:                     
                        data = stream.readframes(datasize)

                    # print "data read"

                    if output == True:
                        streamop.write(data)

                    # Convert raw sound data to Numpy array
                    fmt = "%dH"%(len(data)/2)
                    data = struct.unpack(fmt, data)
                    data = np.array(data, dtype='h')   

                    # Check if data size is big enough
                    if len(data) < datasize:
                        break

                    fft = self.getLevels(data, datasize, frate)
                    rms = self.calcVolume(fft, debug=False) # work out rms (amplitude of waveform)
                    

                    levels = self.splitLevels(frate,datasize, fft,debug=debug)
                    beats = self.detectBeat(levels, threshold=self.threshold, stretch=self.stretch)

                    self.timeSinceLastBeat = time.time()-self.timeOfLastBeat
                    # print self.timeSinceLastBeat

                    if self.timeSinceLastBeat > self.timeout:
                        status = self.randomOn()
                        self.timeOfLastBeat = time.time()
                        print status

                    # what to do...
                    # if mood?

                    if self.mood == 0:
                        print "Mood 0"
                        status = self.randomOnBeat(beats, debug=debug)
                        print status
                    elif self.mood ==1:
                        print "Mood 1"
                        status = self.allChBeats(beats, debug=debug)



                    # if (time.time()-self.moodTime) > 10:
                    #     self.mood = (self.mood + 1)%2
                    #     self.moodTime = time.time()
                    # print "Mood", self.mood
                    

                    # os.system('clear')
                    # self.printLevels(levels)
                    print ('tick')
                    print "AUDIO"
                    print int(levels[1])
                    self.s.VU(int(levels[1]*10))
                    # self.s.test(255,0,0)
                    # self.s.beat

                    # if dataQueue != None:
                    #     self.sendData(status, dataQueue)
                    # if brainQueue != None:
                    #     self.sendData(status, brainQueue)


                except:
                    # print "NO AUDIO"
                    pass

                time.sleep(1.0/60)


                # end loop

        except KeyboardInterrupt:
            pass
        finally:
            print "\nStopping"
            stream.close()

        pass

    '''
    Scans for audio input devices 
    '''
    def list_devices(self):
        # List all audio input devices
        self.p = pyaudio.PyAudio()
        i = 0
        n = self.p.get_device_count()
        while i < n:
            dev = self.p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                print str(i)+'. '+dev['name']
            i += 1


    '''
    Splits fft data in to five regions for approximate instrument detection 
    '''
    def splitLevels(self,frate,data_size, data,debug=False):
        '''
        kick - 80-100Hz
        snare - 120-240Hz
        Hi-hat and symbols - 200H
        '''
        # each cell covers freq rang
        frange = frate / data_size
        data =np.log(data)-2

        bassCell = int(math.ceil(40.0/frange))
        bass = data[bassCell] *2

        kickCell = int(math.ceil(80.0/frange))
        kick = data[kickCell] *2

        snareCell = int(math.ceil(140.0/frange))
        snare = data[snareCell] *2

        hhCell = int(math.ceil(220.0/frange))
        hh = data[hhCell] *2

        vocalCell = int(math.ceil(400.0/frange))
        vocal = data[vocalCell] *2

        levelList = [bass,kick,snare,hh,vocal]

        # if debug:
        #     os.system('clear')
        #     for x in xrange(len(levelList)):
        #         s = ""
        #         for i in xrange(int(levelList[x])):
        #             s += 'x'
        #         print s



        return levelList



    def getDominantF(self,fftData,frequencies,samplerate):

        # Find the peak in the coefficients
        freqL = np.abs(fftData)
        # print freqL, len(freqL), len(w)
        idx = np.argmax(freqL)
        # print idx
        freq = frequencies[idx]
        # print freq #, freqs[data_size-idx] # 1st half of list is negative values 0 - frate/2 Hz 2nd half is positiv frate/2 - 0 Hz
        freq_in_hertz = abs(freq * samplerate)

        return freq_in_hertz


    '''
    applies fft to return the levels for each frequency cell
    '''
    def getLevels(self, data, chunk, samplerate):

        w = np.fft.fft(data) # apply FFT
        freqs = np.fft.fftfreq(len(w)) # get frequencies

        freqHz = self.getDominantF(w,freqs,samplerate)

        # abs works only on real number so gets rid of complex!
        ffty = np.abs(w) # apply aboslute value for first half of array to make it all positive

        return ffty

    # def sendLevels(self, levels, dataQueue, threshold=17):

    #     #[bass,kick,snare,hh,vocal]
    #     if levels[0] > threshold+3:
    #         print "BOOM"
    #         dataQueue.put('a')
    #     else: dataQueue.put('A')
    #     if levels[1] > threshold:
    #         print "BOOM"
    #         dataQueue.put('b')
    #     else: dataQueue.put('B')
    #     if levels[2] > threshold+3:
    #         print "BOOM"
    #         dataQueue.put('c')
    #     else: dataQueue.put('C')
    #     if levels[3] > threshold:
    #         print "BOOM"
    #         dataQueue.put('d')
    #     else: dataQueue.put('D')
    #     if levels[4] > threshold:
    #         print "BOOM"
    #         dataQueue.put('e')
    #     else: dataQueue.put('E')
    #     pass

    def allChBeats(self, levelsBeat, debug=False):

        on = ['A','B','C','D','E']
        off = ['a','b','c','d','e']

        for x in xrange(len(levelsBeat)):
            if levelsBeat[x]:
                self.chStatus[x] = on[x]
            else: self.chStatus[x] = off[x]

        if debug: print self.chStatus
        return self.chStatus



    def detectBeat(self, levels, threshold=17, stretch=6):
        '''
        Simple beat detection by tracking rising edge, noting when it first rises.
        Currently serial/queue out is not enabled
        '''
        #[bass,kick,snare,hh,vocal]
        beat = False

        for x in xrange(len(levels)):
            if (levels[x] > self.levelsLast[x]+stretch) and (self.levelsEdge[x] == False) and (levels[x] > threshold):
                self.levelsBeat[x] = True
                beat = True;
            elif (levels[x] > self.levelsLast[x]+2):
                self.levelsEdge[x] = True
                self.levelsBeat[x] = False
            else:
                self.levelsEdge[x] = False
                self.levelsBeat[x] = False
            self.levelsLast[x] = levels[x]

        if beat:
            self.timeOfLastBeat = time.time()


        return self.levelsBeat


    def printLevels(self, levels):
            # os.system('clear')
            for x in xrange(len(levels)):
                s = ""
                for i in xrange(int(levels[x])):
                    s += 'x'
                print s

    # def sendData(self, data, dataQueue):

    #     for x in xrange(len(data)):
    #         dataQueue.put(data[x])


    def randomOn(self):
        '''
        Simple beat detection by tracking rising edge, noting when it first rises.
        Currently serial/queue out is not enabled
        '''

        # generate random on/off
        temp = random.randrange(1,32)
        # print temp

        if (temp & 0x01): self.chStatus[0] = 'A'
        else: self.chStatus[0] = 'a'
        if ((temp>>1) & 0x01): self.chStatus[1] = 'B'
        else: self.chStatus[1] = 'b'
        if ((temp>>2) & 0x01): self.chStatus[2] = 'C'
        else: self.chStatus[2] = 'c'
        if ((temp>>3) & 0x01): self.chStatus[3] = 'D'
        else: self.chStatus[3] = 'd'
        if ((temp>>4) & 0x01): self.chStatus[4] = 'E'
        else: self.chStatus[4] = 'e'
            


        return self.chStatus


    def randomOnBeat(self, levelsBeat, debug=False):
        '''
        Simple beat detection by tracking rising edge, noting when it first rises.
        Looks at freqs 2 & 3 only
        '''

        if levelsBeat[1] or levelsBeat[2]:# or self.levelsBeat[2]:
            # print "BOOM!"
            # generate random on/off
            temp = random.randrange(1,32)
            # print temp

            if (temp & 0x01): self.chStatus[0] = 'A'
            else: self.chStatus[0] = 'a'
            if ((temp>>1) & 0x01): self.chStatus[1] = 'B'
            else: self.chStatus[1] = 'b'
            if ((temp>>2) & 0x01): self.chStatus[2] = 'C'
            else: self.chStatus[2] = 'c'
            if ((temp>>3) & 0x01): self.chStatus[3] = 'D'
            else: self.chStatus[3] = 'd'
            if ((temp>>4) & 0x01): self.chStatus[4] = 'E'
            else: self.chStatus[4] = 'e'

            if debug: print self.chStatus
            
        else: 
            # dont do anything
            pass


        return self.chStatus


    def calcVolume(self, data, debug=False):
        # work out rms (amplitude of waveform)
        rms_val = np.sqrt(np.mean(data**2)) / 10000.0
        if not np.isnan(rms_val): 
            if debug:
                # print rms_val
                os.system('clear')
                s = ""
                for i in xrange(int(rms_val/1.0)):
                    s += 'x'
                print s
            return rms_val
        else:
            return 0.0

    

if __name__ == '__main__':


    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="file path and name of wav file.")
    parser.add_argument("-d", "--debug", type=str, help="set true to print to terminal.")
    parser.add_argument("-s", "--datasize", type=int, help="data size/window, default 2048.")
    parser.add_argument("-m", "--mic", type=str, help="set true to print to use microphone input.")
    args = parser.parse_args()


    if args.datasize != None: data_size = args.datasize
    else: data_size = 2048

    if args.file != None: fname = args.file
    else: fname = "../sounds/test.wav"
    frate = 44100.0

    if args.debug != None: debug = True
    else: debug = False

    if args.mic != None:
        mic=True
    else: mic = None

    mic = False

    brain = fft(datasize=data_size,mic=mic,debug=debug,fname=fname,frate=44100.0, output=True)

    exit()






