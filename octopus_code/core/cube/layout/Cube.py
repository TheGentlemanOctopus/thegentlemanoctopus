
import sys
import Panel
from multiprocessing import Queue
from fft import Fft
import device
import opc
import time

''' TODO NOTES:
 - could audio / fft data be a udp multicast instead of a queue?
'''

def map_range(value, OldMin, OldMax, NewMin,NewMax):
    OldRange = (OldMax - OldMin)  
    NewRange = (NewMax - NewMin)  
    NewValue = (((value - OldMin) * NewRange) / OldRange) + NewMin
    return max(min(255,NewValue),0)

class Cube(device.Device):

    def __init__(self, origin=(0.0,0.0,0.0),width=5,height=5,gap=0.1,step=0.3, frame_period=1000, opc_ip='127.0.0.1:7890'):
        device.Device.__init__(self,frame_period=frame_period, opc_ip=opc_ip)

        xP = Panel.Panel(origin=(origin[0]+(width-1)*step, origin[1]-gap, origin[2]), colShift=(-step,0.0,0.0), rowShift=(0.0,0.0,-step), nPixelsWide=width, nPixelsHigh=height)
        yP = Panel.Panel(origin=(origin[0]+-gap, origin[1], origin[2]-(width-1)*step), colShift=(0.0,0.0,step), rowShift=(0.0,step,0.0), nPixelsWide=width, nPixelsHigh=height)
        zP = Panel.Panel(origin=(origin[0]+0.0, origin[1]+(width-1)*step, origin[2]+gap), colShift=(0.0,-step,0.0), rowShift=(step,0.0,0.0), nPixelsWide=width, nPixelsHigh=height)
        
        self.Panels = [xP,yP,zP]

        self.pixels = []
        self.colors = []
        self.val = 0.2

        for panel in self.Panels:
            for strip in panel.rows:
                for pixel in strip.pixels:
                    self.pixels.append(pixel.location)
                    self.colors.append(pixel.color)

        self.nPixels = len(self.pixels)
        
        # return self.pixels

    def get_pixels(self):
        return self.pixels

    def get_colours(self):
    	colours = []
        for panel in self.Panels:
            colours.extend(panel.get_colours())
        # print colours
        return colours

    def update_audio(self, audio_data):
        # print audio_data[:5]
        self.val = map_range(audio_data[1]*2,0,100,0.2,1.0)
        for p in self.Panels:
            p.set_val(self.val)

        beats = audio_data[5:]
        if beats[0] == 'A':
            self.Panels[0].shift_hue(0.01)
        if beats[2] == 'C':
            self.Panels[1].shift_hue(0.02)
        if beats[4] == 'D':
            self.Panels[2].shift_hue(0.06)
        pass

    def shift_col(self):
    	for panel in self.Panels:
            panel.shift_pixel()

    def shift_row(self):
        for panel in self.Panels:
            panel.shift_row()

    def clear_pixels(self):
    	for panel in self.Panels:
    		panel.clear_pixels()

    def vu_to_rows(self):
        # dir(self)
        # print self.audio_data
        ch = [max(min(int(i/10), 5), 0) for i in self.audio_data[:5] ]
        for panel in self.Panels:
            panel.vu_to_rows(ch)

    def next_frame(self):
        # print 'next frame cube'
        self.clear_pixels()
        self.vu_to_rows()
        # self.shift_col()
        # self.shift_row()


if __name__ == '__main__':
    ''' to run
    - ensure an opc server is running 
        $ bin/gl_server -l layouts/cubeLayout.json 127.0.0.1:7890

    - then 
        $ Cube.py -f DaftPunk.wav 

    '''

    #-------------------------------------------------------------------------------
    # handle command line

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip_host", type=str, help="ip:port defauls to 127.0.0.1:7890.")
    parser.add_argument("-f", "--file", type=str, help="file path and name of wav file.")
    parser.add_argument("-d", "--debug", type=str, help="set true to print to terminal.")
    parser.add_argument("-s", "--datasize", type=int, help="data size/window, default 2048.")
    parser.add_argument("-m", "--mic", type=str, help="set true to print to use microphone input.")
    args = parser.parse_args()

    if args.ip_host != None: IP_PORT = args.ip_host
    else: IP_PORT = '127.0.0.1:7890'

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


    ''' cube config '''
    audio_queue = Queue()
    cube = Cube(origin=(0,0,0), frame_period=100, opc_ip=IP_PORT)
    cube.daemon = True
    control_queue = cube.control_queue
    pixel_queue = cube.pixel_queue
    cube.start()

    ''' FFT config '''
    mic = False
    fft = Fft(datasize=data_size,mic=mic,debug=debug,fname=fname,frate=44100.0, output=True, dataqueue=cube.audio_queue)
    fft.daemon = True
    fft.start()


    time.sleep(1)

    client = opc.Client(IP_PORT)
    if client.can_connect():
        print('    connected to %s' % IP_PORT)
    else:
        # can't connect, but keep running in case the server appears later
        print('    WARNING: could not connect to %s' % IP_PORT)
    print('')





    while True:

        control_queue.put('get_colours')
        while pixel_queue.empty():
            time.sleep(.10)
        client.put_pixels(pixel_queue.get(), channel=0)
        

