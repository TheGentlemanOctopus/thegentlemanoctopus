import udp_server
import time
from collections import deque
import numpy as np
from detect_peaks import detect_peaks
from rpcClient import RpcClient

class PeakDetector(RpcClient):
	def __init__(self, delay=0.001):
		RpcClient.__init__(self)

		self.udp_server = udp_server.UDPServer()
		self.udp_server.start()

		# Create a list of rolling buffers for the FFT data.
		self.eq_data = []
		self.peak_buffer_size = 50
		self.delay = delay

		for row in range(self.udp_server.num_fft_chan):
			# Each FFT channel has a rolling deque that will be used for peak detection
			self.eq_data.append(deque([0 for i in range(self.peak_buffer_size)], maxlen = self.peak_buffer_size))

	def run(self):
		while True:
			if len(self.udp_server.fft_queue) != 0:
				fft = self.udp_server.fft_queue.pop()

				for i in range(len(fft)):
					self.eq_data[i].appendleft(fft[i])

				self.udp_server.fft_queue.clear()
				self.peak_detect()

				self.put({"eq": [float(x) for x in fft]})

			time.sleep(self.delay)

	#Threshold relative to buffer mean
	def peak_detect(self, 
		threshold=1.2,
		high_limit=700, 
		lower_limit = 300,
		peak_length = 0.002 # in seconds, TBD in
		):

		fft_peaks = []
		for row in range(self.udp_server.num_fft_chan):
		    fft_peaks.append(False)

		led_data = 0
		fft_index = 0   
		for fft_buffer in self.eq_data:
			# Auto thresholding for the peaks
			FFTThreshold = np.mean(fft_buffer) * threshold
			if FFTThreshold > high_limit:
				FFTThreshold = high_limit	
			if FFTThreshold < lower_limit:
				FFTThreshold = lower_limit	

			indexes = detect_peaks(fft_buffer, mph = FFTThreshold, mpd = peak_length/self.delay)
			
			if len(indexes):
				if indexes[0]==1: 
					fft_peaks[fft_index] = True	

			fft_index += 1

		self.fft_peaks = fft_peaks

if __name__ == '__main__':
	peak_detector = PeakDetector()
	peak_detector.run()



		