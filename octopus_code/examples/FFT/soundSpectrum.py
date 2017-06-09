# Python 2.7 code to analyze sound and interface with Arduino

'''
stolen from http://julip.co/2012/05/arduino-python-soundlight-spectrum/
'''

import pyaudio # from http://people.csail.mit.edu/hubert/pyaudio/
# import serial # from http://pyserial.sourceforge.net/
import numpy # from http://numpy.scipy.org/
import audioop
import sys
import math
import struct
import time
import os
 
'''
Sources
 
http://www.swharden.com/blog/2010-03-05-realtime-fft-graph-of-audio-wav-file-or-microphone-input-with-python-scipy-and-wckgraph/
http://macdevcenter.com/pub/a/python/2001/01/31/numerically.html?page=2
 
'''
 
MAX = 0
 
resolution = 20

def list_devices():
	# List all audio input devices
	p = pyaudio.PyAudio()
	i = 0
	n = p.get_device_count()
	while i < n:
		dev = p.get_device_info_by_index(i)
		if dev['maxInputChannels'] > 0:
			print str(i)+'. '+dev['name']
		i += 1
	 
def arduino_soundlight():
	chunk = 1024 #2**11 # Change if too fast/slow, never less than 2**11 # FFT length or Nfft
	exponent = 5 # Change if too little/too much difference between loud and quiet sounds
	samplerate = 44100
	sampleperiod = 1.0/samplerate
	wordlength = 16 #bits
	TC = float(chunk) / float(samplerate) # length of time that frame observes (frame number of bytes / secs per sample)
	print TC
	FR = 1.0/TC
	 
	# CHANGE THIS TO CORRECT INPUT DEVICE
	# Enable stereo mixing in your sound card
	# to make you sound output an input
	# Use list_devices() to list all your input devices
	device = 0
	p = pyaudio.PyAudio()
	print samplerate, chunk, device
	stream = p.open(format = pyaudio.paInt16, channels = 1, rate = samplerate, input = True, frames_per_buffer = chunk, input_device_index = device)
	print "Starting, use Ctrl+C to stop"
	d = 0
	try: 


		maxValues = [0] * resolution

		while True:

			try:
				data = stream.read(chunk) # 1024 frames
		 
				# Do FFT
				levels = calculate_levels(data, chunk, samplerate)
				
				os.system('clear')
				
				print "D", d
				d += 1
				for x in xrange(resolution):

					maxValues[x] = int(levels[x])

					if maxValues[x] > 0:
						s = ""
						for i in xrange(maxValues[x]):
							s += 'x'

						print s
					else:
						print " "

				# if maxValue[0] > 12:
			except:
				print "NO AUDIO"

			time.sleep(1.0/1000)

			 
	except KeyboardInterrupt:
		pass
	finally:
		print "\nStopping"
		stream.close()
		p.terminate()
	 
def calculate_levels(data, chunk, samplerate):



	# Use FFT to calculate volume for each frequency
	global MAX
	 
	# Convert raw sound data to Numpy array
	fmt = "%dH"%(len(data)/2)
	data2 = struct.unpack(fmt, data)
	data2 = numpy.array(data2, dtype='h')
	 

	# Apply FFT
	fourier = numpy.fft.fft(data2)


	ffty = numpy.abs(fourier[0:len(fourier)/2])/1000 # apply aboslute value for first half of array to make it all positive

	ffty1=ffty[:len(ffty)/2]
	ffty2=ffty[len(ffty)/2::]+2

	ffty2=ffty2[::-1]

	ffty=ffty1+ffty2
	ffty=numpy.log(ffty)-2
	fourier = list(ffty)[4:-4]
	fourier = fourier[:len(fourier)/2]
	size = len(fourier)
	 
	# Add up for 6 lights
	levels = [sum(fourier[i:(i+size/resolution)]) for i in xrange(0, size, size/resolution)][:resolution]
	return levels
	 
if __name__ == '__main__':
	# list_devices()
	arduino_soundlight()

