import pyaudio
import wave
import sys
import struct

import numpy as np
from rpcClient import RpcClient

# length of data to read.
chunk = 1024

class StreamWavClient(RpcClient):
    audio_stream = None
    wf = None
    p = None

    def __init__(self, host=""):
        if host!="":
            RpcClient.__init__(self, host)
        else:
            RpcClient.__init__(self)


    #gain: the mean amplitude on its own is a little weak, so we need a gain
    #max_freq_amp: scaling for fft, chosen by running the daft punk example
    def run(self, filename, gain=4, max_freq_amp=15000000):
        self.open_wav(filename)

        self.max_eq = 1

        # play stream (looping from beginning of file to the end)
        audio_data = self.read_chunk()
        while audio_data != '':
            eq_raw = self.eq(audio_data)

            if max(eq_raw) > self.max_eq:
                self.max_eq = max(eq_raw)

            self.put([int(1024.0*x/self.max_eq) for x in eq_raw])
            audio_data = self.read_chunk()

    def open_wav(self, filename):
        #TODO: Handle File-locking with with?
        # open the file for reading.
        self.wf = wave.open(filename, 'rb')
        
        # create an audio object
        self.p = pyaudio.PyAudio()

        # open stream based on the wave object which has been input.
        self.audio_stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
            ) 

    def read_chunk(self):
        nChannels = self.wf.getnchannels()

        # read and play data (based on the chunk size)
        data = self.wf.readframes(chunk*nChannels)

        if data == '':
             # cleanup stuff.
            self.audio_stream.close()    
            self.p.terminate()
            return data

        self.audio_stream.write(data)

        # Convert raw sound data to Numpy array
        # TODO: Does this work for mono?
        interleaved_audio = np.array(struct.unpack("%dH" % (len(data)/2), data), dtype='h')

        #Return the mean
        channels = [interleaved_audio[offset::nChannels] for offset in range(nChannels)]
        summedChannels = np.zeros(len(channels[0]))
        for channel in channels:
            summedChannels += channel

        return np.divide(summedChannels, nChannels)

    def bit_depth(self):
        if self.wf.getsampwidth() == 1:
            return 8
        elif self.wf.getsampwidth() == 2:
            return 16
        else:
            raise Exception("Cannot get bit depth")

    # Wavs are centered around 0
    def max_amplitude(self):
        return 2**self.bit_depth() / 2.0     

    # Sample rate based in current track
    def fft(self, chunk):
        # Power spectrum
        fft = np.abs(np.fft.fft(chunk))
        fft = fft[0:len(fft)/2]

        # Nyquist
        freq = np.linspace(0,1,len(fft)) * self.wf.getframerate() / 2

        return (fft, freq)

    # Returns a 7 band eq,
    def eq(self, chunk):
        # TODO: prolly shouldn't be hardcoded :p
        # Peaks from MSGEQ7
        # See: https://www.sparkfun.com/datasheets/Components/General/MSGEQ7.pdf
        peaks = [
            63,
            160,
            400,
            1000,
            2500,
            6250,
            16000
        ]

        fft, freq = self.fft(chunk)

        # Simple for now, just take the max amp in each band
        crossings = np.array([0])
        for i in range(len(peaks) - 1):
            # Set band borders at the approx bandpass crossings
            crossings = np.append(crossings, np.exp(0.5*(np.log(peaks[i]) + np.log(peaks[i+1]))))
        crossings = np.append(crossings, freq[-1]) 

        # Take the max
        eq_levels = []
        for i in range(len(crossings) - 1):
            start_index = next(x[0] for x in enumerate(freq) if x[1] >= crossings[i])
            end_index = next(x[0] for x in enumerate(freq) if x[1] >= crossings[i+1])
            fft_band = fft[start_index:end_index]
         
            eq_levels.append(np.max(fft_band))

        return eq_levels
   

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Supply filename of wav as first argument"
        quit()

    if len(sys.argv) > 2:
        StreamWavClient(host=sys.argv[2]).run(sys.argv[1])
    else:
        StreamWavClient().run(sys.argv[1])



    