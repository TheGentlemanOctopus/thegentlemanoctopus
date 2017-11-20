import argparse
import csv
import socket
import time
import threading

spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

class QueueCSV(threading.Thread):
    ''' stream a commas separated csv file of fft data''' 
    def __init__(self, filename, queue, framerate=30):
        self.filename = filename
        self.queue = queue
        self.framerate = framerate

        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        '''endlessly streams'''
        while True:
            with open(self.filename) as file:
                for row in file:
                    self.queue.put(row)

                    #TODO account for socket send
                    time.sleep(1.0/self.framerate)






if __name__ == '__main__':
    # Argin the parsin
    parser = argparse.ArgumentParser(description="Stream the FFT")
    parser.add_argument('--framerate', type=int, default=30, help="Framerate")
    parser.add_argument('--file', help="path to csv")

    args = parser.parse_args()

    # Stream it up!
    stream_csv = StreamCSV(args.file, args.host, args.port, args.framerate)
    stream_csv.start()

    print "Streaming", args.file
    while True:
        pass



