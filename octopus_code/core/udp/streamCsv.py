import argparse
import csv
import socket
import time
import threading

class StreamCSV(threading.Thread):
    ''' stream a commas separated csv file of fft data''' 
    def __init__(self, filename, host="127.0.0.1", port=5009, framerate=10):
        self.filename = filename
        self.host = host
        self.port = port
        self.framerate = framerate

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        while True:
            with open(self.filename) as file:
                for row in file:
                    self.socket.sendto(row, (self.host, self.port))

                    #TODO account for socket send
                    time.sleep(1.0/self.framerate)






if __name__ == '__main__':
    # Argin the parsin
    parser = argparse.ArgumentParser(description="Stream the FFT")
    parser.add_argument('--host', default='127.0.0.1', help="Host")
    #5009?
    parser.add_argument('--port', type=int, default=5009, help="Port")
    parser.add_argument('--framerate', type=int, default=30, help="Framerate")
    parser.add_argument('--file', help="path to csv")

    args = parser.parse_args()

    # Stream it up!
    stream_csv = StreamCSV(args.file, args.host, args.port, args.framerate)
    stream_csv.start()

    print "Streaming", args.file, "to", args.host + ":" + str(args.port)
    while True:
        pass



