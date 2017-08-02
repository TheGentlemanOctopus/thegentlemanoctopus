#!/usr/bin/env python

"""A demo client for Open Pixel Control
http://github.com/zestyping/openpixelcontrol

Creates a shifting rainbow plaid pattern by overlaying different sine waves
in the red, green, and blue channels.

To run:
First start the gl simulator using the included "wall" layout

    make
    bin/gl_server -l layouts/octopus.json

Then run this script in another shell to send colors to the simulator

    python python_clients/octopus_ben.py

"""

from __future__ import division
import time
import math
import sys

import opc
# import color_utils
from colorutils import Color

import threading
import Queue
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlServer

'''
TODO: 
- Creat xml server
- Server passes data through queue to main loop
- Main loop polls queue
'''

class opcClient():
    '''
    The opcClient is the main algorithm for driving the opc leds.
    New commands should be sent via a queue.
    '''

    def __init__(self, eventQueue, opcIP_PORT='127.0.0.1:7890'):
        self.eventQueue = eventQueue
        self.IP_PORT = opcIP_PORT


        self.client = opc.Client(self.IP_PORT)
        if self.client.can_connect():
            print '    connected to %s' % self.IP_PORT
        else:
            # can't connect, but keep running in case the server appears later
            print '    WARNING: could not connect to ' + self.IP_PORT
        


    def run(self):

        r = 0
        g = 0
        b = 0

        n_pixels = 512  # number of pixels in the included "octopus" layout
        fps = 1000         # frames per second


        vuVal = n_pixels

        start_time = time.time()
        #Where are the global coords?
        while True:

            if not self.eventQueue.empty():
                items = self.eventQueue.get()
                with self.eventQueue.mutex:
                    self.eventQueue.queue.clear()
                print items
                if items[0] == 'test':
                    r = items[1]
                    g = items[2]
                    b = items[3]
                elif items[0] == 'VU':
                    vuVal = items[1]%n_pixels

            t = time.time() - start_time
            pixels = []

            # col = Color(hsv=((vuVal/5), 50, 50))

            for ii in range(n_pixels):
                if ii < vuVal:
                    pixels.append((r, g, b))
                    # pixels.append(col.rgb)                    
                else:
                    pixels.append((0, 0, 0))

            self.client.put_pixels(pixels, channel=0)
            # time.sleep(1 / fps)
            #TODO: What is the point of this?
            time.sleep(1/100000000)




if __name__ == '__main__':


    # # import argparse
    # # parser = argparse.ArgumentParser()
    # # parser.add_argument("-f", "--file", type=str, help="file path and name of wav file.")
    # # parser.add_argument("-d", "--debug", type=str, help="set true to print to terminal.")
    # # parser.add_argument("-s", "--datasize", type=int, help="data size/window, default 2048.")
    # # parser.add_argument("-m", "--mic", type=str, help="set true to print to use microphone input.")
    # # args = parser.parse_args()


    # if args.datasize != None: data_size = args.datasize
    # else: data_size = 2048

    # if args.file != None: fname = args.file
    # else: fname = "../sounds/test.wav"
    # frate = 44100.0

    # if args.debug != None: debug = True
    # else: debug = False

    # if args.mic != None:
    #     mic=True
    # else: mic = None

    host = 'localhost'
    port = 8000

    ''' create queues '''
    dataQueue = Queue.Queue(1000)

    ''' thread xml server & pass queue '''
    print "before start xml server" 
    server = xmlServer.ServerThread(host, port, dataQueue)
    server.daemon = True
    server.start()
    print "after start xml server" 

    ''' start opc client '''
    print "before start opc client" 
    # opc = opcClient(dataQueue, opcIP_PORT='192.168.2.6:7790')
    opc = opcClient(dataQueue, opcIP_PORT='192.168.0.100:7790')
    # opc = opcClient(dataQueue)
    print "after start opc client" 
    opc.run()

    exit()


