import argparse
import csv
import socket

class StreamCsv:
    def __init__(self, filename, host, port, framerate):
        self.filename = filename
        self.host = host
        self.port = port
        self.framerate = framerate

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def stream(self):
        while True:
            with open(self.filename) as file:
                for row in file:
                    self.socket.sendto(row, (self.host, self.port))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stream the FFT")
    parser.add_argument('--host', default='192.168.1.177', help="Host")
    #5009?
    parser.add_argument('--port', type=int, default=5003, help="Port")
    parser.add_argument('--framerate', type=int, default=30, help="Framerate")
    parser.add_argument('--file', help="path to csv")

    args = parser.parse_args()

    stream_csv = StreamCsv(args.file, args.host, args.port, args.framerate)
    stream_csv.stream()




