import argparse
import csv

class StreamCsv:
    def __init__(self, filename, host, port, framerate):
        self.filename = filename
        self.host = host
        self.port = port
        self.framerate = framerate

    def stream(self):
        while True:
            with open(self.filename) as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            
                for row in reader:
                    fft = [int(item) for item in row]
                    print fft





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




