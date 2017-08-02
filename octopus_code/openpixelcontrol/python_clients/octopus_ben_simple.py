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
import random

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

    def __init__(self,opcIP_PORT='127.0.0.1:7890'):
        
        self.IP_PORT = opcIP_PORT


        self.client = opc.Client(self.IP_PORT)
        if self.client.can_connect():
            print '    connected to %s' % self.IP_PORT
        else:
            # can't connect, but keep running in case the server appears later
            print '    WARNING: could not connect to ' + self.IP_PORT
        


    def run(self):

        # print "tick"

        r = 0
        g = 0
        b = 0

        n_pixels = 512  # number of pixels in the included "octopus" layout
        fps = 10         # frames per second

        mid = 0


        vuVal = n_pixels

        start_time = time.time()
        #Where are the global coords?
        while True:
            mid = (mid + 4)%255

        
            pixels = []
            print 'tick', mid
            for ii in range(n_pixels):

                p = (mid + random.randint(1, 40)) % 255

                # h 0-255, s 0.0-1.0, v 0.0-1.0
                col = Color(hsv=(p, random.uniform(0.2,0.8) , random.uniform(0.2,0.8) ))
                print p, col.rgb
                pixels.append(col.rgb)                    

            self.client.put_pixels(pixels, channel=1)
            time.sleep(1 / fps)
            # time.sleep(1/fps)




if __name__ == '__main__':


    host = '192.168.1.52'
    port = 7890

    arg = '192.168.1.52:7890'

    ''' start opc client '''
    print "before start opc client" 
    # opc = opcClient(dataQueue, opcIP_PORT='192.168.2.6:7790')
    # opc = opcClient(opcIP_PORT='192.168.0.100:7790')

    opc = opcClient(opcIP_PORT=arg)
    print "after start opc client" 
    opc.run()

    exit()


