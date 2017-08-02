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

class RpcServer(threading.Thread):
    def __init__(self, dataQueue=1, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port

        #Initialise the thread
        threading.Thread.__init__(self)

        # Python warns about file locking and such with daemon threads
        # but we are not using any resources like that here 
        # https://docs.python.org/2/library/threading.html#thread-objects
        self.daemon = True
        
        self.server = SimpleXMLRPCServer((host, port), 
            requestHandler=RequestHandler,
            logRequests=False
            )
        self.server.register_function(self.put)

        # TODO: 1000 should be more than enough, but we should make sure, 
        # Annoying! LIFO queue's don't have a clear
        self.queue = Queue.Queue(1000)

    def run(self):
        self.server.serve_forever()

    # Request data is expected to be a dictionary since
    # only simple data types can be serialized over xmlrpc (python objects cannot)
    # See: http://www.tldp.org/HOWTO/XML-RPC-HOWTO/xmlrpc-howto-intro.html#xmlrpc-howto-types
    def put(self, requestData):
        with self.queue.mutex:
            self.queue.queue.clear()

        self.queue.put(requestData)

        if self.queue.full():
            print "WARNING! Max data queue limit reached: " + str(self.queue.qsize())

        #Echo for now
        return requestData

    def url(self):
        return "http://%s:%i%s" % (self.host, self.port, rpc_path)

    #LIFO get
    def get(self):
        with self.queue.mutex:
            item = self.queue.queue[-1]
            self.queue.queue.clear()

        return item

# Example
if __name__ == '__main__':
    # Run the Rpc server on a new thread
    rpc_server = RpcServer()
    print "Running XML-RPC server at " + rpc_server.url()
    rpc_server.start()

    # Make a client
    s = xmlrpclib.ServerProxy(rpc_server.url())

    # Echo
    count=0
    while True:
        s.put({"x": count})
        count += 1

        if not rpc_server.queue.empty():
            print "Item received: " + str(rpc_server.queue.get())

        time.sleep(3)
