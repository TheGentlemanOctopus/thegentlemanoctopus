# Python 2.7 code to analyze sound and interface with Arduino

'''
stolen from http://julip.co/2012/05/arduino-python-soundlight-spectrum/
'''

import pyaudio # from http://people.csail.mit.edu/hubert/pyaudio/
import wave
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
 
resolution = 32

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
	# exponent = 5 # Change if too little/too much difference between loud and quiet sounds
	samplerate = 44100 # 44100 gives maximum detectable frequency of 20KHz 
	sampleperiod = 1.0/samplerate
	wordlength = 16 #bits
	TC = float(chunk) / float(samplerate) # length of time that frame observes (frame number of bytes / secs per sample)
	print TC, sampleperiod
	FR = 1.0/TC
	 
	# CHANGE THIS TO CORRECT INPUT DEVICE
	# Enable stereo mixing in your sound card
	# to make you sound output an input
	# Use list_devices() to list all your input devices

	stream = wave.open("DaftPunk.wav", 'rb')
	# stream = wave.open("test1600.wav", 'rb')

	device = 0

	p = pyaudio.PyAudio()
	
	# get mic stream
	# stream = p.open(format = pyaudio.paInt16, channels = 1, rate = samplerate, input = True, frames_per_buffer = chunk, input_device_index = device)
	
	# get wav stream
	print stream.getsampwidth(), stream.getnchannels(), stream.getframerate()
	streamop = p.open(format=p.get_format_from_width(stream.getsampwidth()),
                channels=stream.getnchannels(),
                rate=stream.getframerate(),
                output=True)

	print "Starting, use Ctrl+C to stop"

	try: 


		maxValues = [0] * resolution

		while True:

			# data = stream.read(chunk) # 1024 frames from mic
			data = stream.readframes(chunk) # 1024 frames from wav
			streamop.write(data)
	 
			# print "len of data: %s" % len(data)

			# Do FFT
			levels = calculate_levels(data, chunk, samplerate)
			
			os.system('clear')
			# for x in xrange(resolution):

			

			# # kick
			# maxValues[0] = int(levels[0]/3)
			# s = ""
			# if maxValues[0] > 0:
			# 	for i in xrange(maxValues[0]): s += 'x'
			# print s
			
			# print "\n\n"

			# snare = 18
			# maxValues[snare] = int(levels[snare]/3)
			# s = ""
			# if maxValues[snare] > 0:
			# 	for i in xrange(maxValues[snare]): s += 'x'
			# print s
			
			print " "

			for x in xrange(resolution):

				maxValues[x] = int(levels[x])

				if maxValues[x] > 0:
					s = ""
					for i in xrange(maxValues[x]):
						s += 'x'

					print s
				else:
					print " "


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
	# print len(data2), data2[0], data[0]
	data2 = numpy.array(data2, dtype='h')
	 

	# Apply FFT
	fourier = numpy.fft.fft(data2)
	# print len(fourier)

	ffty = numpy.abs(fourier[0:len(fourier)/2])/1000 # apply aboslute value for first half of array to make it all positive
	# print len(ffty)

	ffty1=ffty[:len(ffty)/2]    # first half of ffty
	ffty2=ffty[len(ffty)/2::]+2 # last half of ffty with 2 added to each value

	ffty2=ffty2[::-1]			# the -1 reverses the order of the array
	# print type(ffty1), len(ffty1), type(ffty2), len(ffty2)
	

	ffty=ffty1+ffty2			# zips or added together each corresponding element, remember first half was made positive
	# print type(ffty), len(ffty), type(ffty1), len(ffty1)
	ffty=numpy.log(ffty)-2 		# log the numbers, dont know why -2 though. 
	# print len(ffty)
	fourier = list(ffty)[4:-4]	# remove first 4 and last 4 elements?
	# print len(fourier)
	fourier = fourier[:len(fourier)/2] # discard last last of data?
	# print len(fourier)
	size = len(fourier)
	# print size 
	# Add up for 6 lights
	# add up values for one 20th segment of data / resolution 
	levels = [sum(fourier[i:(i+size/resolution)]) for i in xrange(0, size, size/resolution)][:resolution]
	return levels
	 
if __name__ == '__main__':
	# list_devices()

	arduino_soundlight( )

