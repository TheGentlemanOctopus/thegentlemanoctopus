# test

# from core import soundreaction
# from core.Serial.SerialThread import serial
from core.Serial.SerialThreadDB import SerialThreadBD
from core.octopus.patternGenerator import PatternGenerator


from core.udp.udp_server import UDPServer

from core.octopus.patterns.shambalaPattern import ShambalaPattern

from core.octopus.patterns.simplePattern import SimplePattern
from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patterns.eqPattern import EqPattern
from core.octopus.patterns.rainbowPlaidPattern import RainbowPlaidPattern
from core.octopus.patterns.rainbowPlaidEqPattern import RainbowPlaidEqPattern

#from patterns.solidColorPattern import SolidColorPattern, SpiralOut, PulseOut, IntegrateF, GridPattern, HelicopterEq
from core.octopus.patterns.spiralOutFast import SpiralOutFast


from core.octopus.patterns.lavaLampPattern import LavaLampPattern

import core.octopus.layouts.octopus as octopus
import core.octopus.kbHit

''' beat detection class ''' 
from core.audioAnalysis.beatDetection import BeatDetection

import numpy as np

import Queue
import argparse

import time
import sys

import ConfigParser


'''
To run: python run.py core/octopus/layouts/octopus.json
'''

if __name__ == '__main__':

	

	conf = {}

	with open('tgo.ini') as fp:
		Config = ConfigParser.ConfigParser()
		Config.readfp(fp)
		sections = Config.sections()
		print Config.sections()
		for s in Config.sections():
			print s, Config.items(s)
			for i in Config.items(s):
				print i
				conf[i[0]] = int(i[1])

	print conf


	fftQueue = Queue.Queue(100)
	ELQueue = Queue.Queue(100)
	patternQueue = Queue.Queue(100)

	#Determine if using rpc or not
	use_rpc = False

	num_pos_args = len(sys.argv)-1
	for i in range(num_pos_args):
		if sys.argv[i] == "--rpc":
			host = sys.argv[i+1]

			rpc_server = RpcServer(host="127.0.0.1", port=8000)
			rpc_server.start()
			queue = rpc_server.queue

			num_pos_args -= 2
			use_rpc = True
			break


	''' set up udp server THREAD '''
	if not use_rpc:
		try: 
			server = UDPServer(patternQueue, ELQueue, fft_extent_reset_time=conf['fft_extent_reset_time'])
			server.start()
			print "UDP connected OK!"
		except Exception, e:
			print "Error connecting to UDP", e
			exit()

	''' set up beat detection serial THREAD '''
	try: 
		# print "test 1"
		thr = SerialThreadBD(ELQueue,sim=False,port="/dev/ttyUSB0", baud="57600", threshold=conf['threshold'], stretch=conf['stretch'])
		# print "test 2"
		thr.start()
		print "Serial connected OK!"
	except Exception, e:
		print "Error connecting to serial", e
		exit()



	''' Set up pattern generator class ''' 
	if num_pos_args == 1:
		pattern_generator = PatternGenerator(octopus.ImportOctopus(sys.argv[1]), patternQueue)
	elif num_pos_args == 2:
		pattern_generator = PatternGenerator(octopus.ImportOctopus(sys.argv[1]), patternQueue, opc_host=sys.argv[2], rhythm_channel=conf['rhythm_channel'],framerate=conf['framerate'])
	else:
		print "Supply octopus.json as first arg"
		quit()       

	''' register patterns for generator '''
	pattern_generator.patterns = [
		ShambalaPattern(),
		SpiralOutFast(),
		LavaLampPattern(),
		EqPattern(),
		RainbowPlaidEqPattern(),
	]

	''' run pattern generator ''' 
	pattern_generator.run()
	

    