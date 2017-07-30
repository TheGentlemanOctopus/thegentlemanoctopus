#!/usr/bin/env python

from core.audioAnalysis.AudioProcessing import AudioProcessing
from core.fish.fish import Fish
from core.octopus.gentlemanOctopus import GentlemanOctopus
import core.octopus.layouts.octopusLayout as octopusLayout
import core.octopus.patterns.patternList as patternList

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
        self.layout_f = layout

        ''' init control queues '''
        self.ifQueue = controlQueue(100)
        self.fish_ctrl = Queue.Queue(100)
        self.octopus_ctrl = Queue.Queue(100)
        self.audio_ctrl = Queue.Queue(100)

        ''' init queues '''
        self.ELQueue = Queue.Queue(100)
        self.fft_queues = [Queue.Queue(100),Queue.Queue(100)]

        ''' init devices '''
        self.init_audio_processing(self.conf_audio, self.fft_queues, self.audio_ctrl)
        self.init_fish(self.fish_ctrl,fft_queues[0])
        self.init_octopus(self.octopus_ctrl,fft_queues[1])
        
        # init control interface


        pass

    def process_config(self):
        ''' declare specific dictionaries '''
        self.conf_routing = conf['Routing']
        self.conf_fish = conf['Fish']
        self.conf_control = conf['Control']
        self.conf_audio = conf['BeatDetection']   
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

    def init_audio_processing(self, conf, fft_q, ctrl_q):
        self.audio = AudioProcessing(
            conf,
            fft_q, 
            ctrl_q
            )
        self.audio.start()
        pass


    def init_fish(self, conf, fft_q, ctrl_q):
        self.fish = Fish(
            conf, 
            controlQueue=ctrl_q, 
            audio_stream_queue=fft_q
            )
        self.fish.start()


    def init_octopus(self, fft_q, ctrl_q):
        octopus_layout = octopusLayout.Import(self.layout_f)
        self.gentleman_octopus = GentlemanOctopus(
            octopus_layout, 
            control_queue=ctrl_q,
            audio_stream_queue=audio_q,
            opc_host=self.conf_routing['OPC_ip'], 
            opc_port=self.conf_routing['OPC_port'],
            patterns=patternList.patterns
        )
        self.gentleman_octopus.start()


    def init_control(self, fft_q, ctrl_q):
        print 'init control not implimented'


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





    