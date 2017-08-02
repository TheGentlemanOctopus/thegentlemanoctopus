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


## Once initialised and connected the SerialThread will poll the dataqueue for new data to transmit.  
#
#  Current it does not have a seperate read method.
class SerialThread():
    """docstring for SerialThread - Has 1 thread to read data queue and send it out via serial (wip)"""

    ## Constructor for serial thread, does very little just defines the class.  
    #
    def __init__(self, dataQueue):
        # threading.Thread.__init__(self)
        print "Init serial thread"
        self.port = "/Dev/ttyUSB0"
        self.baud = "57600"
        self.dataQueue = dataQueue

    ## Connect will connect the serial on given port at given baud. Once connected a thread is started
    #  that will poll the data queue for new serial packets to send.
    #
    #  @param string port address
    #  @param string baud rate
    def connect(self, port, baud):
        print "Connect serial thread"
        self.port = port
        self.baud = baud
        self.connection = False

        try:
            self.ser = serial.Serial(port = self.port, baudrate = self.baud, 
            parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, timeout=1)
            self.connection = True
            print "Connected OK "

        except serial.SerialException:
            # self.logQueue.put("Error: Failed to connect to serial on " + self.port + ":" + self.baud)
            print "Error: Failed to connect"
            self.connection = False
            pass


        try: 
            thread = threading.Thread(target = self.threaded_function1)
            thread.daemon = True # serial thread should be daemon so it shuts on closing
            thread.start()

        except:
            # self.writeToLog("Serial thread failed to start")
            print "Serial thread failed to start"
            pass

    ## closes the serial connection
    #
    def close(self):
        self.ser.close()

    ## threaded function will poll data queue for new serial packets to send.
    #
    #  Additionally it will check for ACKs returned by rainbowduino.
    def threaded_function1(self):
        """ I could make it read 4 frame segments then delay """

        print "SerialThread: im running"

        segmentCount = 0

        while self.connection == True:
            if not self.dataQueue.empty():
                msg = self.dataQueue.get()
                with self.dataQueue.mutex:
                    self.dataQueue.queue.clear()
                self.ser.flushOutput()
                self.ser.write(msg)
                # print binascii.hexlify(bytearray(msg))

                # wait for ack - dont really need to read this unless something stops working
                time.sleep(1.0/50.0);
                # ack = self.ser.read(4)
                # if len(ack) == 4:
                #     # print ack[3]
                #     pass
                # else:
                #     print "No ack received"

                segmentCount += 1

            if (segmentCount < 4) :
                # delay between segments
                time.sleep(1.0/50.0);
            else :
                # delay between 
                segmentCount = 0
                time.sleep(1.0/20.0) 

        print "exiting serial thread"
        pass