#!/usr/bin/env python

from core.Serial.SerialThreadDB import SerialThreadBD # needs to SchoolOfFish(Device) 
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



class OctopusScene():
    '''
    * GentlemanOctopus
    * EL-Ting
    * Control Input (RPC Server)
    * Audio processing (UDP Server)
    '''
    
    def __init__(self, config, layout, controlQueue):
        ''' config - dictionary '''
        self.config = config
        self.process_config()

        self.ifQueue = controlQueue

        ''' init queues '''
        self.if_Queue = Queue.Queue(100)
        self.fftQueue = Queue.Queue(100) # not used
        self.ELQueue = Queue.Queue(100)

        ''' init devices '''
        self.init_audio_input(self.conf_auto_gain)
        self.init_beat_detection(self.conf_beat, self.conf_EL)

        pass

    def process_config(self):
        ''' declare specific dictionaries '''
        self.conf_routing = conf['Routing']
        self.conf_EL = conf['EL']
        self.conf_control = conf['Control']
        self.conf_beat = conf['BeatDetection']
        self.conf_auto_gain = conf['AutoGain']       
        self.conf_pattern_gen = conf['PatternGenerator'] 
        self.conf_patterns = conf['Patterns']

    def print_config(self, conf):
        ''' 
        method to print the configuration file parameters
        '''
        print '\nConfiguration file loaded....\n'
        ''' sections '''
        for section in conf:
            print '\n____[', section, ']____'
            for item in conf[section]:
                print item, ':', conf[section][item]

    def init_audio_input(self, args):
        '''
        START UDP SERVER
        '''
        if checkInDictEquals(self.conf_control,'UDP',1): 
            ''' set up udp server THREAD '''
            try: 
                self.server = UDPServer(
                    self.fftQueue, 
                    self.ELQueue, 
                    fft_extent_reset_time=args['fft_extent_reset_time']
                    )
                self.server.start()
                print "UDP connected OK!"
            except Exception, e:
                print "Error connecting to UDP", e
                exit()

    def init_beat_detection(self, beat, el):
        '''
        START BEAT DETECTION THREAD
        '''
        if checkInDictEquals(beat,'Enable',1): 
            try: 
                if conf_EL['sim']: 
                    sim = True
                else: 
                    sim = False
                self.thr = SerialThreadBD(
                    ELQueue,
                    sim=sim,
                    port=el['port'], 
                    baud=el['baud'], 
                    threshold=beat['threshold'], 
                    stretch=beat['stretch']
                    )
                self.thr.start()
                print "Serial connected OK!"
            except Exception, e:
                print "SerialThreadBD: Error connecting to serial", e
                exit()

    
    def init_pattern_generator(self, routing, patternG, patterns):
        ''' 
        START PATTERN GENERATOR
        '''
        if checkInDictEquals(patternG,'Enable',1): 
            try: 
                self.pattern_generator = PatternGenerator(
                    octopus.ImportOctopus(f_layout), 
                    fftQueue, 
                    opc_host=routing['OPC_ip'], 
                    opc_port=routing['OPC_port'], 
                    rhythm_channel=patternG['rhythm_channel'],
                    framerate=patternG['framerate']
                    )
            except Exception, e:
                print "Error connecting to UDP", e
                exit()

        ''' register patterns for generator '''
        patterns_list = []
        if checkInDictEquals(patterns,'ShambalaPattern',1):
            patterns_list.append(ShambalaPattern())
        if checkInDictEquals(patterns,'SpiralOutFast',1):
            patterns_list.append(SpiralOutFast())
        if checkInDictEquals(patterns,'LavaLampPattern',1):
            patterns_list.append(LavaLampPattern())
        if checkInDictEquals(patterns,'EqPattern',1):
            patterns_list.append(EqPattern())
        if checkInDictEquals(patterns,'RainbowPlaidEqPattern',1):
            patterns_list.append(RainbowPlaidEqPattern())
        self.pattern_generator.patterns = patterns_list
        print patterns_list

# Example
if __name__ == '__main__':

    
    scene = OctopusScene()





    