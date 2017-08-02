#!/usr/bin/env python
import threading
import Queue
import time
import os
from numpy import interp
import kbHit as kbHit

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib


from core.xmlrpc.xmlrpcThread import RpcServerThread

rpc_path = '/RPC2'

'''
rpc ip  
rpc port

this code reads kv input and sends out through xmlrpc

class1: kb -> queue
class2: queue -> xmlrpc client

TODO:

- Add mutex call for queue interaction

'''

class kb_client():
    """kb_client provides a keyboard cmd line interface. Received
    inputs are sent to the xmlrpc interface."""
   
    def __init__(self, rpc_ip='127.0.0.1', rpc_port=8000):
        
        self.kb = kbHit.KBHit()   
        
        ''' init client '''
        self.s = xmlrpclib.ServerProxy('http://' + rpc_ip + ':' + str(rpc_port))
        print 'available RPC methods: \n', self.s.system.listMethods()

        ''' create meters to display '''
        self.meters = {}
        self.meters['brightness_meter'] = level_meter()
        self.meters['frame_rate'] = level_meter(minimum=20.0, maximum=30.0, start=25.0, increment=1.0)

    def update(self):
        """ Call once per cycle to review he keyboard input. 
        TODO: add current pattern and other status from rpc call"""
        # Handle Keyboard Input
        if self.kb.kbhit():
            key = self.kb.getch()
            # print 'kb in:', key
            if key == 'q':
                print 'Quit'
                return False
                pass
            ''' change pattern '''
            elif key == 'w':
                self.s.helloWorld('helloWorld', key)
                pass
            elif key =='s':
                self.s.helloWorld('helloWorld', key)
                pass
            ''' brightness '''
            elif key == 'e':
                self.meters['brightness_meter'].up()
                self.s.setBrightness(self.meters['brightness_meter'].value)
                pass
            elif key =='d':
                self.meters['brightness_meter'].down()
                self.s.setBrightness(self.meters['brightness_meter'].value)
                pass
            ''' frame_rate '''
            elif key == 'r':
                self.meters['frame_rate'].up()
                self.s.setFrameRate(self.meters['frame_rate'].value)
                pass
            elif key =='f':
                self.meters['frame_rate'].down()
                self.s.setFrameRate(self.meters['frame_rate'].value)
                pass
        self.print_status()
        return True

    def print_status(self):
        ''' prints all data to screen after 'clear' command '''
        #Print some stufff
        os.system('clear')
        print "*" * 50
        print ""

        print "q: exit"
        print "w/s: change pattern \n"
        print 'brightness e/d:', self.meters['brightness_meter'].data, self.meters['brightness_meter'].value
        print 'frame_rate r/f:', self.meters['frame_rate'].data, self.meters['frame_rate'].value
        
class level_meter():
    ''' level_meter tracks paramter values in the cmd tool and generates
    a string representation to print to the screen. '''

    def __init__(self, minimum=0.0, maximum=100.0, start=50.0, length=21, increment=10.0):
        self.minimum = minimum
        self.maximum = maximum
        self.value = start
        self.length = length
        self.increment = increment
        self.create_str_data()
        self.marker_pos = int(interp(start,[self.minimum,self.maximum],[0,self.length]))
        self.data = self.data[:self.marker_pos]+'x'+self.data[self.marker_pos+1:]

    def clamp(self, n, minn, maxn):
        ''' limits a value 'n' to bounds 'minn' & 'maxn' '''
        return max(min(maxn, n), minn)

    def create_str_data(self):
        ''' creates a string representation of meter and marker positions '''
        self.data = '-'*self.length
        self.marker_pos = int(interp(self.value,[self.minimum,self.maximum],[0,self.length]))
        self.data = self.data[:self.marker_pos]+'x'+self.data[self.marker_pos+1:]

    def up(self,increment=None):
        ''' pushes marker up by increment '''
        if increment==None:
            inc = self.increment
        else:
            inc = increment

        self.value = self.clamp((self.value + inc),self.minimum,self.maximum)
        self.create_str_data()

    def down(self,increment=None):
        ''' pushes marker down by increment '''
        if increment==None:
            inc = self.increment
        else:
            inc = increment

        self.value = self.clamp((self.value - inc),self.minimum,self.maximum)
        self.create_str_data()

# Example
if __name__ == '__main__':

    dQueue = Queue.Queue(100)
    
    rpc_server = RpcServerThread(dataQueue=dQueue, host='localhost',port=8000)
    rpc_server.daemon = True
    rpc_server.start()

    kb = kb_client()

    while kb.update():
        if not dQueue.empty():
            msg = dQueue.get()
            print msg
        time.sleep(.1)  

    # rpc_server.terminate()
    # rpc_server.join()

    