#!/usr/bin/env python

''' for Bens new changes '''
# from core.xmlrpc.xmlrpcThread import RpcServerThread

''' Patterns import '''

# import core.octopus.layouts.octopus as octopus
from core.scene.octopusScene import OctopusScene

''' beat detection class ''' 
from core.audioAnalysis.BeatDetection import BeatDetection

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
	# print 'checkInDictEquals', key, value
	try:
		if key in dic:
			# print 'check- ', dic[key]
			return dic[key] == value
	except KeyError:
		# print 'FALSE'
		return False

def print_config(conf):
	''' 
	method to print the configuration file parameters
	'''
	print '\nConfiguration file loaded....\n'
	''' sections '''
	for section in conf:
		print '\n____[', section, ']____'
		for item in conf[section]:
			print item, ':', conf[section][item]


if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	parser.add_argument("-l", "--layout", type=str, help="layout file eg. octopus.json")
	parser.add_argument("-c", "--config", type=str, help="config file eg. tgo.ini")
	parser.add_argument("-t", "--timeout", type=int, help="timeout, forever if 0")

	args = parser.parse_args()

	if args.layout:
		f_layout = args.layout
	else:
		f_layout = 'core/octopus/layouts/octopus.json'
	if args.config:
		f_config = args.config
	else:
		f_config = 'tgo.ini'
	if args.timeout:
		timeout = args.timeout
	else:
		timeout = 0
	

	''' read config file '''
	conf = {}
	with open(f_config) as fp:
		Config = ConfigParser.ConfigParser()
		Config.optionxform=str
		Config.readfp(fp)
		sections = Config.sections()
		print Config.sections()
		for s in Config.sections():
			# print s#, Config.items(s)
			conf[s]={}

			for i in Config.items(s):
				conf[s][i[0]] = str_to_type(i[1])
				# print i
	print_config(conf)


	''' init queues '''
	rpcQueue = Queue.Queue(100)

	'''
	START RPC INTERFACE
	'''
	if checkInDictEquals(conf['Control'],'RPC',1): 
		rpc_ip = conf['Routing']['RPC_Server_ip']
		rpc_port = conf['Routing']['RPC_Server_port']
		try:
			rpc_server = RpcServerThread(
				dataQueue=rpcQueue,
				host=rpc_ip,
				port=rpc_port
				)
			rpc_server.daemon = True
			rpc_server.start()
		except Exception, e:
			print "Error initiation RpcServerThread", e
			exit()	

	'''
	START SCENE
	'''
	if checkInDictEquals(conf['Control'],'OctopusScene',1): 
		try:
			print 'starting octopusScene'

			scene = OctopusScene(conf, f_layout, rpcQueue)
			scene.main_loop(timeout)
		except Exception, e:
			print "Error initiation OctopusScene", e
			exit()	

	print 'Goodbye!'


	

	
	

    