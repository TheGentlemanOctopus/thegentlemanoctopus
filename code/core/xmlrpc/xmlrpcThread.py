#!/usr/bin/env python
import threading
import Queue
import time

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib

rpc_path = '/RPC2'

# The RPC server listens at host:port/rpc_path
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = (rpc_path,)

class RpcServerThread(threading.Thread):
    '''
    TODO:
        - create standard message format for queue
            {
                [cmd_type]:['change_pattern']
                [args]:[['EqPattern']]
            }
    '''
    def __init__(self, dataQueue=None, host='127.0.0.1', port=8000):
        #Initialise the thread
        # self._running_flag = False
        # self.stop  = threading.Event()
        threading.Thread.__init__(self)



        self.host = host
        self.port = port
        self.dQueue = dataQueue
        print 'Starting xmlrpc server on -', self.host, ':', self.port

        self.server = SimpleXMLRPCServer((host, port), requestHandler=RequestHandler)

        ''' register functions '''
        self.server.register_introspection_functions()

        ''' pattern API '''
        self.server.register_function(self.setPattern, 'setPattern')
        self.server.register_function(self.setRGB, 'setRGB')
        self.server.register_function(self.setBrightness, 'setBrightness')
        self.server.register_function(self.setFrameRate, 'setFrameRate')

        ''' audio processing API '''
        self.server.register_function(self.setThreshold, 'setThreshold')
        self.server.register_function(self.setStretch, 'setStretch')
        self.server.register_function(self.enableAutogain, 'enableAutogain')
        self.server.register_function(self.setAutogainResetTime, 'setAutogainResetTime')
    

    # def terminate(self):
    #     self.stop.set()

    def run(self):
        self.server.serve_forever()

    ''' Pattern API '''
    def setPattern(self, pattern='EqPattern'):
        msg = {}
        msg['cmd_type'] = 'change_pattern'
        msg['args'] = [pattern]
        self.dQueue.put(msg)
        return "New pattern %s" % pattern   

    def setRGB(self, r=50,g=50,b=50):
        msg = {}
        msg['cmd_type'] = 'change_pattern'
        msg['args'] = ['RGB',r,g,b]
        self.dQueue.put(msg)
        return "RGB {0}:{1}:{2}".format(r,g,b)

    def setBrightness(self, arg=50.0):
        print 'setBrightness', arg
        msg = {}
        msg['cmd_type'] = 'set_brightness'
        msg['args'] = ['Brightness',arg]
        print msg
        self.dQueue.put(msg)
        return "Brightness {0}".format(arg)

    def setFrameRate(self, arg=25.0):
        msg = {}
        msg['cmd_type'] = 'set_framerate'
        msg['args'] = ['FrameRate',arg]
        self.dQueue.put(msg)
        return "FrameRate {0}".format(arg)

    ''' Audio processing API '''
    def setThreshold(self, threshold=85):
        msg = {}
        msg['cmd_type'] = 'change_AudioProc'
        msg['args'] = ['Threshold',threshold]
        self.dQueue.put(msg)
        return "New Threshold {0}".format(threshold)

    def setStretch(self, stretch=18):
        msg = {}
        msg['cmd_type'] = 'change_AudioProc'
        msg['args'] = ['Stretch',stretch]
        self.dQueue.put(msg)
        return "New Threshold {0}".format(stretch)
    
    def enableAutogain(self,state=1):
        msg = {}
        msg['cmd_type'] = 'change_AudioProc'
        msg['args'] = ['Autogain',state]
        self.dQueue.put(msg)
        return "Autogain enable {0}".format(1)

    def setAutogainResetTime(self,arg=30):
        msg = {}
        msg['cmd_type'] = 'change_AudioProc'
        msg['args'] = ['AutogainReset',arg]
        self.dQueue.put(msg)
        return "Autogain extent reset time {0}".format(arg)
 

def processMsg(msg):

    if msg['cmd_type'] == 'change_pattern':
        print 'change_pattern', ",".join(map(str,msg['args']))
    elif msg['cmd_type'] == 'change_AudioProc':
        print 'change_AudioProc', ",".join(map(str,msg['args']))

def testRPCServer():
    dQueue = Queue.Queue(100)
    # Run the Rpc server on a new thread
    rpc_server = RpcServerThread(dataQueue=dQueue,host='localhost',port=8000)
    rpc_server.daemon = True
    rpc_server.start()

    time.sleep(2)

    s = xmlrpclib.ServerProxy('http://127.0.0.1:8000')
    meths = s.system.listMethods()
    for meth in meths[:-2]:
        getattr(s,meth)()

# Example
if __name__ == '__main__':

    dQueue = Queue.Queue(100)
    # Run the Rpc server on a new thread
    rpc_server = RpcServerThread(dataQueue=dQueue,host='localhost',port=8000)
    rpc_server.daemon = True
    rpc_server.start()

    while True:
        if not dQueue.empty():
            msg = dQueue.get()
            processMsg(msg)
        time.sleep(1)   






    