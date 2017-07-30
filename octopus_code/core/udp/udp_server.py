import threading
import socket
import Queue
import time
import numpy as np
import csv
import argparse

#from collections import deque

def map_val(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class UDPServer(threading.Thread):
    """docstring for UDPServer"""
    def __init__(self,
        dataqueue, 
        arduino_ip = '192.168.1.177',
        local_ip = '',
        start_port = 5003,
        data_port = 5009,
        start_message = "Start",
        buffer_size = 100,
        fft_extent_reset_time = 10,
        autogainEnable = 1,
        no_sound_frequency = 0.2,
        ambient_level = 512,
        no_mic_level = 100,
        ):

        print local_ip
        print "-----------"
        self.arduino_ip = arduino_ip
        self.local_ip = local_ip
        self.start_port = start_port
        self.data_port = data_port
        self.start_message = start_message

        self.ambient_level = ambient_level
        self.no_mic_level = no_mic_level

        self.autogainEnable = autogainEnable

        threading.Thread.__init__(self)
        self.daemon = True

        # There are 7 FFT channels being read from the MSGEQ7
        self.num_fft_chan = 7

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

        self.sock.bind((self.local_ip, self.data_port))
        self.sock.settimeout(1)
        self.connected = False
        self.buffer_size = buffer_size

        self.fft_queue = dataqueue
        self.no_sound_frequency = no_sound_frequency

        self.reset_fft_extents()

        self.fft_extent_reset_time = fft_extent_reset_time


    def reset_fft_extents(self):
        self.min_fft = 1024
        self.max_fft = 0
        self.no_sound = True
        self.last_fft_extent_reset = time.time()


    def udp_reader(self):

        if self.connected == False:
            try:
                self.sock.sendto(self.start_message, (self.arduino_ip, self.start_port))
                print "sending message:", self.start_message
            except:
                self.FFTData = "0,0,0,0,0,0,0"


        try:
            self.FFTData = self.sock.recv(1024) # udp recieve  buffer size is 1024 bytes
            self.connected = True
            #print "recieved message:", FFTData
        except socket.timeout:
            self.FFTData = "0,0,0,0,0,0,0"
            self.connected = False


    def run(self):

        while True:

            self.udp_reader()


            # Parse the data csv style
            parsedData = self.FFTData.split(",", self.num_fft_chan)

            if time.time() - self.last_fft_extent_reset > self.fft_extent_reset_time:
                self.reset_fft_extents()

            for i in range(len(parsedData)):
                # Fix for if broken data is recieved
                if parsedData[i].find(',') < 0:
                    # Convert data to integers
                    parsedData[i] = int(parsedData[i])

                    if self.autogainEnable:
                        # Reassign the max & min fftnumbers for scaling
                        if parsedData[i] < self.min_fft:
                            self.min_fft = parsedData[i]

                        if parsedData[i] > self.max_fft:
                            self.max_fft = parsedData[i]

                        if self.min_fft != self.max_fft:
                            scale = self.ambient_level if self.max_fft < self.ambient_level else self.max_fft
                            parsedData[i] = map_val(parsedData[i], self.min_fft, self.max_fft, 0, scale)
                        else:
                            parsedData = [0,0,0,0,0,0,0]
                            break

                else:
                    parsedData = [0,0,0,0,0,0,0]
                    break


            #print parsedData

            if self.max_fft > self.no_mic_level:
                self.no_sound = False

            # does siney outputs if there's no sound.
            if self.no_sound:
                offsets = np.linspace(0, (12.0/7)*np.pi, 7)
                levels = 512*(np.cos(2*np.pi*self.no_sound_frequency*time.time() + offsets) + 1)
                parsedData = levels.tolist()


            
            with self.fft_queue.mutex:
                self.fft_queue.queue.clear()
            #add to the queue
            self.fft_queue.put(parsedData)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Gimme FFT")
    parser.add_argument('--file', default=None, help="Where To Save CSV")

    args = parser.parse_args()

    dataqueue = Queue.Queue(100)
    server = UDPServer(dataqueue)
    server.start()

    if args.file:
        
        with open(args.file, 'wb') as csvfile:
            datawriter = csv.writer(csvfile, delimiter=',', quotechar='|',quoting=csv.QUOTE_MINIMAL)
            
            while True:
                if not dataqueue.empty():
                    data = dataqueue.get()
                    datawriter.writerow(data)
                    print data
    else:

        while True:
            if not dataqueue.empty():
                data = dataqueue.get()
                print data



