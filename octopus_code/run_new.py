# test

# from core import soundreaction
# from core.Serial.SerialThread import serial
from core.Serial.SerialThreadDB import SerialThreadBD
from core.octopus.patternGenerator import PatternGenerator


from core.udp.udp_server import UDPServer

from core.octopus.patterns.shambalaPattern import ShambalaPattern

from core.octopus.patterns.simplePattern import SimplePattern
from core.octopus.patterns.rpcTestPa# from core import soundreaction
# from core.Serial.SerialThread import serial
from core.Serial.SerialThreadDB import SerialThreadBD
from core.octopus.patternGenerator import PatternGenerator
from core.udp.udp_server import UDPServer
from core.octopus.rpcServer import RpcServer

''' for Bens new changes '''
from core.xmlrpc.xmlrpcThread import RpcServerThread

''' Patterns import '''
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

''' standard imports '''
import numpy as np
import Queue
import argparse
import time
import sys
import ConfigParser


'''
To run: python run.py core/octopus/layouts/octopus.json
'''

def str_to_type(s):
	''' 
	method to cast a str value to most appropriate type 
	'''
	try: 
		int(s)
		return int(s)
	except ValueError:
		try: 
			float(s)
			return float(s)
		except ValueError:
			return s

def checkInDictEquals(dic, key, value):
	''' 
	method to check for key existance in dictionary with value
	'''
	try:
		if key in dic:
			return dic[key] == value
	except KeyError:
		return False


if __name__ == '__main__':


	parser = argparse.ArgumentParser()
	
	parser.add_argument("-l", "--layout", help="layout file eg. octopus.json", action="store_true")
	parser.add_argument("-c", "--config", help="config file eg. tgo.ini", action="store_true")

	args = parser.parse_args()

	if args.layout:
		f_layout = args.layout
	else:
		f_layout = 'core/octopus/layouts/octopus.json'
	if args.config:
		f_config = args.config
	else:
		f_config = 'tgo.ini'
	

	''' read config file '''
	conf = {}
	with open(f_config) as fp:
		Config = ConfigParser.ConfigParser()
		Config.optionxform=str
		Config.readfp(fp)
		sections = Config.sections()
		print Config.sections()
		for s in Config.sections():
			print s#, Config.items(s)
			conf[s]={}

			for i in Config.items(s):
				conf[s][i[0]] = str_to_type(i[1])
				print i
	print_config(conf)


	''' init queues '''
	controlQueue = Queue.Queue(100)

	'''
	START RPC INTERFACE
	'''
	if checkInDictEquals(conf_control,'RPC',1): 
		rpc_ip = conf_routing['RPC_Server_ip']
		rpc_port = conf_routing['RPC_Server_port']

		try:
			rpc_server = RpcServerThread(
							dataQueue=controlQueue,
							host=rpc_ip,
							port=rpc_port
						)
			rpc_server.daemon = True
			rpc_server.start()
		except Exception, e:
			print "Error initiation RpcServerThread", e
			exit()	





	

	
	

    