import opc
import time
import sys
import Queue

from core.udp.udp_server import UDPServer

from core.octopus.patterns.shambalaPattern import ShambalaPattern

from core.octopus.patterns.simplePattern import SimplePattern
from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patterns.eqPattern import EqPattern
from core.octopus.patterns.rainbowPlaidPattern import RainbowPlaidPattern
from core.octopus.patterns.rainbowPlaidEqPattern import RainbowPlaidEqPattern

#from patterns.solidColorPattern import SolidColorPattern, SpiralOut, PulseOut, IntegrateF, GridPattern, HelicopterEq
from core.octopus.patterns.spiralOutFast import SpiralOutFast
from core.octopus.patterns.spiralInFast import SpiralInFast


from core.octopus.patterns.lavaLampPattern import LavaLampPattern

import core.octopus.layouts.octopus as octopus
import core.octopus.kbHit as kbHit

from core.octopus.rpcServer import RpcServer

import numpy as np

#Generate patterns and send to a OPC host
#Strict throws exceptions if it cannot keep up
#with framerates or if patterns are unstable
class PatternGenerator:
    def __init__(self,
        octopus,
        queue=None,
        opc_host="127.0.0.1", 
        opc_port=7890,
        rhythm_channel = 0,
        framerate = 20,
        strict=False
    ):
        self.octopus = octopus

        if not queue:
            queue = Queue.Queue(1)

        self.queue = queue

        self.opc_host = opc_host
        self.opc_port = opc_port

        self.rhythm_channel = rhythm_channel

        opc_ip = opc_host + ":" + str(opc_port)
        self.client = opc.Client(opc_ip)

        # If the client is not connected the put_pixels operation is slow as it tries to reconnect
        if not self.client.can_connect():
            raise Exception("Could not connect to opc at " + opc_ip)

        self.patterns = [RpcTestPattern()]
        self.current_pattern = []

        self.period = 1.0/framerate

        self.strict = strict

        # For frame loop
        #Initialise data that's fed into patterns
        self.pattern_input_data = self.default_pattern_input_data()
        self.set_default_pattern()
        
        #For detecting keyboard presses
        self.kb = kbHit.KBHit()

    

    def default_pattern_input_data(self):
        return {
            "level": 0,
            "eq": (0,0,0,0,0,0,0), # 7 band
            "rhythm_channel": self.rhythm_channel
        }

    #Strict framerate throws an exception if it cannot keep up  
    def run(self, timeout=0):
        print "Sending pixels forever..."

        run_start = time.time()

        while True:
            loop_start = time.time()

            if self.update():
                break

            if timeout and time.time() - run_start > timeout:
                break

            loop_end = time.time() - loop_start
            loop_time = self.period - loop_end

            if self.strict and loop_time < 0:
                raise Exception("Cannot keep up with framerate")

            time.sleep(max(0, self.period - loop_end))


    def update(self):  
        quit = False

        # Handle Keyboard Input
        if self.kb.kbhit():
            key = self.kb.getch()
            if key == 'q':
                quit = True
                return quit
            elif key == 'w':
                pattern_index = self.previous_pattern()
            elif key =='s':
                pattern_index = self.next_pattern()
            elif self.nudge_param(key):
                self.print_status()


        # Read from data queue
        if not self.queue.empty():
            # Keep it clean and cleat
           
            with self.queue.mutex:
                eq = self.queue.queue[-1]
                self.queue.queue.clear() 

            self.pattern_input_data["eq"] = [eq_level/1024.0 for eq_level in eq]
            self.pattern_input_data["level"] = np.mean(eq)

        # Send some pixels
        try:
            self.current_pattern.next_frame(self.octopus, self.pattern_input_data)
            self.client.put_pixels([pixel.color for pixel in self.octopus.pixels_zig_zag()], channel=1) 
        except:
            if self.strict:
                raise Exception("Pattern throwing exceptions")
            else:
                print "WARNING:", self.current_pattern.__class__.__name__, "throwing exceptions"

        return quit

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
        self.current_pattern.on_pattern_select(self.octopus)
        self.octopus.clear_pixels()

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

    #TODO Pretty args
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


    #TODO: Ben's stuff
    if not use_rpc:
        queue = Queue.Queue(100)
        server = UDPServer(queue, None)
        server.start()

    if num_pos_args == 1:
        pattern_generator = PatternGenerator(octopus.ImportOctopus(sys.argv[1]), queue)
    elif num_pos_args == 2:
        pattern_generator = PatternGenerator(octopus.ImportOctopus(sys.argv[1]), queue, opc_host=sys.argv[2])
    else:
        print "Supply octopus.json as first arg"
        quit()       

    pattern_generator.patterns = [
        ShambalaPattern(),
        SpiralInFast(),
        SpiralOutFast(),
        LavaLampPattern(),
        RpcTestPattern(),
        EqPattern(),
        RainbowPlaidEqPattern()
    ]

    pattern_generator.run()

