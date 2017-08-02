import opc
import time
import sys
import Queue
import os
import traceback
import itertools

from core.udp.udpServer import UDPServer

import core.octopus.layouts.octopusLayout as octopusLayout
import core.octopus.kbHit as kbHit

import core.octopus.patterns.patternList as patternList

from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patternStreamData import PatternStreamData

from core.octopus.rpcServer import RpcServer

from device import Device
import argparse

import numpy as np

#Generate patterns and send to a OPC host
class GentlemanOctopus(Device):
    """a GentlemanOctopus is responsible for generating patterns
    and projecting those colors onto its chromatophores (opc host)
    """
    def __init__(self,
        octopus_layout,
        control_queue=None,
        audio_stream_queue=None,
        opc_host="127.0.0.1", 
        opc_port=7890,
        rhythm_channel = 0,
        framerate = 20,
        enable_status_monitor=True,
        queue_receive_timeout=10,
        patterns = None
    ):
        """ octopus is a octopus layout"""

        # Initialise Base contructor
        super(GentlemanOctopus, self).__init__(control_queue, audio_stream_queue)

        self.octopus_layout = octopus_layout

        # TODO Should this go on device? I think fft bad output analysis and receive timeouts should 
        # go on a higher level class
        self.queue_last_receive = 0
        self.queue_receive_timeout = queue_receive_timeout

        # OPC Settings
        self.opc_host = opc_host
        self.opc_port = opc_port

        # TODO This should be in audio stream queue class
        self.rhythm_channel = rhythm_channel

        opc_ip = opc_host + ":" + str(opc_port)
        self.client = opc.Client(opc_ip)

        # If the client is not connected the put_pixels operation is slow as it tries to reconnect
        if not self.client.can_connect():
            raise Exception("Could not connect to opc at " + opc_ip)

        # Make sure we have some pattern!
        self.patterns = patterns if patterns else [RpcTestPattern()]

        #TODO Should we enforce a framerate with sleep or just go as fast as possible approach?
        self.period = 1.0/framerate

        #TODO replace Ben's status monitor with my nicer vertical bars   
        self.enable_status_monitor = enable_status_monitor

        #Initialise data that's fed into patterns
        self.pattern_stream_data = PatternStreamData()
        self.set_default_pattern()
        
        #For detecting keyboard presses
        if self.enable_status_monitor:
            self.kb = kbHit.KBHit()    


    # def run(self):
    #     self.update()

    #Returns None if we should quit
    def update(self):

        # Handle Keyboard Input
        if self.enable_status_monitor:
            if self.kb.kbhit():
                key = self.kb.getch()
                if key == 'q':
                    return None
                elif key == 'w':
                    pattern_index = self.previous_pattern()
                elif key =='s':
                    pattern_index = self.next_pattern()
                elif self.nudge_param(key):
                        self.print_status()

        # Read from data queue
        if not self.audio_stream_queue.empty():
            # Keep it clean and clear
            with self.audio_stream_queue.mutex:
                raw_data = self.audio_stream_queue.queue[-1]
                eq = raw_data[:7]
                beats = raw_data[7:]
                

            # TODO: Set bit depth somewhere
            self.pattern_stream_data.set_eq(tuple([int(eq_level)/1024.0 for eq_level in eq]))
            self.pattern_stream_data.set_beats(beats)
            self.queue_last_receive = time.time()


        # Default Eq data if none is received
        # TODO: Leave this to higher level data?
        if time.time() - self.queue_last_receive > self.queue_receive_timeout:
            self.pattern_stream_data.siney_time()

        # Send some pixels
        try:
            self.current_pattern.next_frame(self.octopus_layout, self.pattern_stream_data)

            # HACK : This is retrofitted for Truefest, mantle shouldnt always have to = tentacle
            cycle = itertools.cycle(self.octopus_layout.tentacles[0].pixels_zig_zag())
            for pixel in self.octopus_layout.mantle.pixels:
                tenty_pixel = next(cycle)
                pixel.color = tenty_pixel.color

            pixels = [pixel.color for pixel in self.octopus_layout.opc_pixels()]
        except Exception as e:
            print "WARNING:", self.current_pattern.__class__.__name__, "throwing exceptions"
            print traceback.format_exc()
            raise e


        self.client.put_pixels(pixels, channel=1)


    # TODO: Delete this silly function?
    def set_default_pattern(self):
        if self.patterns:
            self.set_current_pattern(0)
        else:
            raise Exception("No patterns defined")

    def next_pattern(self):
        self.set_current_pattern(self.pattern_index() + 1)

    def previous_pattern(self):
        self.set_current_pattern(self.pattern_index() - 1)

    def pattern_index(self):
        return self.patterns.index(self.current_pattern) 

    def set_current_pattern(self, index):
        if not self.patterns:
            print "no patterns"
            return

        #Handle out of range indexes
        if index < 0:
            index = 0
        elif index > len(self.patterns) - 1:
            index = len(self.patterns) - 1

        # Switch the pattern
        self.current_pattern = self.patterns[index]
        self.current_pattern.on_pattern_select(self.octopus_layout)
        self.octopus_layout.clear_pixels()

        #Set Key mappings for new parameters
        key_mapping = [
            ('r','f'),
            ('t','g'),
            ('y','h'),
            ('u','j'),
            ('i','k'),
            ('o','l'),
            ('p',';')
        ]

        self.key_mappings = []
        ordered_param_names = sorted(self.current_pattern.params.keys(), key=lambda x: self.current_pattern.params[x].index)
        
        for i in range(min([len(key_mapping), len(ordered_param_names)])):
            name = ordered_param_names[i]
            keys = key_mapping[i]
            param = self.current_pattern.params[name]
            self.key_mappings.append(KeyMapping(name, keys[0], keys[1], param))

        # Update message
        if self.enable_status_monitor:
            self.print_status()

        return index

    # Adjusts the parameter given the keyboard key
    def nudge_param(self, key, num_steps=10):
        nudged = False

        for mapping in self.key_mappings:
            if mapping.nudge_param(key):
                nudged = True
                break

        return nudged

    def print_status(self, meter_height=15, meter_width=9):
        #Print some stufff
        print "*" * 50
        print ""

        print "q: exit"
        print "w/s: change pattern \n"

        for pattern in self.patterns:
            string = ""
            if self.current_pattern == pattern:
                print "(*)", pattern.__class__.__name__
            else:
                print "   ", pattern.__class__.__name__

        # Parameter Meters
        meters = []
        for mapping in self.key_mappings:
            strings = []

            # Header
            strings.append('='*meter_width)
            
            # Name / keys
            max_name_length = meter_width - 2
            strings.append(mapping.name[0:max_name_length])
            strings.append("(" + mapping.up_key + "/" + mapping.down_key + ")")

            # Current Value 
            strings.append("%.1f" % mapping.param.get())

            # Progress bar
            num_dashes = meter_height - 1
            post_marker = int(num_dashes*mapping.param.current_percentage())
            pre_marker = num_dashes - post_marker

            strings.append('='*meter_width)
            strings.extend(list('|' * pre_marker))
            strings.append('<=>')
            strings.extend(list('|' * post_marker))
            strings.append('='*meter_width)

            meters.append(strings)

        # Print the meters
        if meters:
            for j in range(len(meters[0])):
                string = ""
                for i in range(len(meters)):
                    string += meters[i][j][0:meter_width].center(meter_width)
        
                print string

# For mapping keys to parameters
class KeyMapping:
    def __init__(self, name, up_key, down_key, param):
        self.name = name
        self.up_key = up_key
        self.down_key = down_key
        self.param = param

    # Adjusts the parameter given the keyboard key
    # Returns True if the key arg matches, False otherwise
    def nudge_param(self, key, num_steps=10):
        nudged = True

        # Find how big a nudge
        step = (float(self.param.max) - self.param.min)/num_steps
        value = self.param.get()
        
        # Nudge it up or down
        if key==self.up_key:
            value += step 
        elif key==self.down_key:
            value -= step
        else:
            nudged = False

        self.param.set(value)

        return nudged



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs TGO for pattern funtimes')
    parser.add_argument('-l', '--layout', default=os.path.dirname(__file__) + "/layouts/octopusLayout.json",
                        help='Path to octopus json')

    parser.add_argument('-i', '--host', default="127.0.0.1", help="opc host")
    parser.add_argument('-p', '--port', type=int, default=7890, help="opc port")
    parser.add_argument('-t', '--time', type=int, default=0, help="How long to run TGO for (seconds)")

    args = parser.parse_args()

    octopus_layout = octopusLayout.Import(args.layout)

    gentleman_octopus = GentlemanOctopus(octopus_layout, 
        opc_host=args.host, 
        opc_port=args.port,
        patterns=patternList.patterns
    )

    gentleman_octopus.run(args.time)

    quit()    




