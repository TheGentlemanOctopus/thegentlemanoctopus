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
import Queue

import SerialThread as serial

 
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
	 
def arduino_soundlight(dataQueue):
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

	stream = wave.open("DaftPunk.wav", 'rb')

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
	 
			# Do FFT
			levels = calculate_levels(data, chunk, samplerate)
			
			os.system('clear')
			for x in xrange(resolution):

				maxValues[x] = int(levels[x]/3)

				if maxValues[x] > 0:
					s = ""
					for i in xrange(maxValues[x]):
						s += 'x'

					print s
				else:
					print " "


			if maxValues[1] > 14:
				print "BOOM"
				dataQueue.put('a')

			if maxValues[8] > 14:
				print "BOOM"
				dataQueue.put('b')

			if maxValues[13] > 14:
				print "BOOM"
				dataQueue.put('c')


			if maxValues[17] > 14:
				print "BOOM"
				dataQueue.put('d')


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
	''' init rainbowduino '''
	# create queues
	dataQueue = Queue.Queue(100)
	# connect serial


	try: 
		ser = serial.SerialThread(dataQueue)
		ser.connect("/dev/tty.usbmodem1421","9600")
		# ser.connect("/dev/tty.usbserial-A5029V9S","115200")
		# ser.connect("COM5","115200")
		
		print "Serial connected OK!"
	except Exception, e:
	    print "Error connecting to serial", e
	    exit()

	arduino_soundlight(dataQueue)

