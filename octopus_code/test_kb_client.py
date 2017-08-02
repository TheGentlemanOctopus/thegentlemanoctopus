
#!/usr/bin/env python
import threading
import Queue
import time
import os
from core.kb_client.kb_client import kb_client
from core.xmlrpc.xmlrpcThread import RpcServerThread

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