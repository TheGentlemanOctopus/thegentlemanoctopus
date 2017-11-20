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
import color_utils

import threading
import Queue
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


## EyeServer provides a clean xml wrapper to the rainbowduino class.
#
class opcXMLServer():

    def __init__(self, host, port, dataQueue):

        print "before enable xmlrpc server"
        print "host: ", host, " port: ", port, " types ", type(host), type(port)
        self.localServer = SimpleXMLRPCServer((host, port), requestHandler=RequestHandler)

        # self.localServer = SimpleXMLRPCServer(("192.168.1.40", 8050), requestHandler=RequestHandler)

        print "after enable xmlrpc server"

        self.dataQueue = dataQueue

        self.localServer.register_introspection_functions()

        self.localServer.register_function(self.test, 'test')
        self.localServer.register_function(self.VU, 'VU')
        self.localServer.register_function(self.beat, 'beat')


    def test(self, r,g,b):
        print "XML server Test"
        self.dataQueue.put(('test',r,g,b))
        return "test"  

    def VU(self, arg):
        print "XML server VU"
        self.dataQueue.put(('VU',arg))
        return "VU" 

    def beat(self):
        print "XML server beat"
        self.dataQueue.put(('beat'))
        return "beat"   

     


## Server thread inherits both thread and eyeserver so that the xml can run 
#  simultanious with the tkinter thread.
#
class ServerThread(threading.Thread, opcXMLServer):
    def __init__(self, host, port, dataQueue):
        threading.Thread.__init__(self)
        print "before EyeServer"
        opcXMLServer.__init__(self, host, port, dataQueue)
        print "after EyeServer"
    def run(self):
        self.localServer.serve_forever()


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
    server = ServerThread(host, port, dataQueue)
    server.daemon = True
    server.start()
    print "after start xml server" 

    ''' start opc client '''
    print "before start opc client" 
    opc = opcClient(dataQueue)
    print "after start opc client" 
    opc.run()

    exit()


