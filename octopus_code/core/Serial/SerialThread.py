#!/usr/bin/python
# -*- coding: utf-8 -*-
# using python 2.7.6

## @package Serial
#  This module hosts the serial tools
#
#  @author B Winstone
#  @date 03/06/2014

import threading 
import Queue
import time    
import serial
import binascii


class SerialThread(threading.Thread):
    """docstring for SerialThread - Has 1 thread to read data queue and send it out via serial (wip)"""

    ## Constructor for serial thread, does very little just defines the class.  
    #
    def __init__(self, dataQueue, sim=False, port="/dev/ttyUSB0", baud="57600", name="SerialThread", threshold=45, stretch=12):
        # threading.Thread.__init__(self)
        print "Init serial thread"
        self.port = port
        self.baud = baud
        self.dataQueue = dataQueue
        self.sim = sim
        threading.Thread.__init__(self,name=name)
        self.process = None
        self.daemon = True


    '''
    Run is called by parent class start()
    '''
    def run(self):
        """ main control loop """
        print "Thread: %s starts" % (self.getName( ),)

        self.connect(self.port,self.baud)

        data = ['a','b','c','d','e','f','g']

        while self.connection == True:

            if not self.dataQueue.empty():
                msg = self.dataQueue.get()

                self.ser.flushOutput()
                for i in xrange(len(msg)):
                    # if beats[i]:
                    #     data[i] = chr(65+i)
                    # else:
                    #     data[i] = chr(97+i)
                    if beats[i]:
                        c = chr(97+i)
                        self.ser.write(c)

                time.sleep(1.0/10000.0);

            if self.sim:
                # print "Tick tick"
                time.sleep(5)

        print "exiting serial thread"
        pass

    ''' 
    Connect will connect the serial on given port at given baud. Once connected a thread is started
    that will poll the data queue for new serial packets to send.
    @param string port address
    @param string baud rate
    '''
    def connect(self, port, baud):
        print "Connect serial thread"
        self.port = port
        self.baud = baud
        self.connection = False

        if not self.sim:
            ''' Connect to serial port '''
            try:
                self.ser = serial.Serial(port = self.port, baudrate = self.baud) 
                # self.ser = serial.Serial(port = self.port, baudrate = self.baud, 
                # parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout=1)
                self.connection = True
                print "Connected OK "

            except serial.SerialException:
                # self.logQueue.put("Error: Failed to connect to serial on " + self.port + ":" + self.baud)
                print "Error: Failed to connect"
                self.connection = False
                pass
        else:
            self.connection = True


    def stop(self):
        print "Trying to stop thread "
        
        if not self.sim: self.ser.close() # closer serial connection

        self.exit()


if __name__ == '__main__':

    dataQueue = Queue.Queue(1000)

    thr = SerialThread(dataQueue,sim=True,port="/dev/ttyUSB0", baud="57600", name='ELSerialThread')
    thr.start()
