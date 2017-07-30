import core.octopus.gentlemanOctopus as gentlemanOctopus
import core.octopus.layouts.octopusLayout as octopusLayout
import core.octopus.opc

import os
import sys

import psutil
import time
import csv
import argparse
import threading
import traceback 

import numpy as np

from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patterns.shambalaPattern import ShambalaPattern
import core.octopus.patterns.patternList as patternList

import core.tests.integrationTestData as integrationTestData
from core.tests.integrationTestData import IntegrationTestData

from utils import Testopus

import subprocess

# matplotlib may not work on the odroid
try:
    import matplotlib.pyplot as plt
    import core.tests.utils as utils
    plotting = True

except Exception as e:
    plotting = False


class IntegrationTest:
    def __init__(self,
        filename, 
        framerate=20, 
        patterns = None,
        host="127.0.0.1",
        port=7890
    ):

        self.gentleman_octopus = gentlemanOctopus.GentlemanOctopus(octopusLayout.Import(Testopus), 
            framerate=framerate,
            patterns = patterns,
            opc_host=host, 
            opc_port=port,
        )

        self.filename = filename

        # Start the cpu meter
        self.cpu_percent = 0
        self.lock = threading.Lock()
        thread = threading.Thread(target=self.cpu_fun)
        thread.daemon = True
        thread.start()

    def run(self, run_time=10):        
        run_start = time.time()
        process = psutil.Process(os.getpid())

        test_file = open(self.filename, "w")

        test_succesful = True

        # Run the Pattern for a bit and log data
        try: 
            while time.time() - run_start < run_time:
                status_string = (
                    "Testing ", self.gentleman_octopus.current_pattern.__class__.__name__, ": ", 
                    int(time.time() - run_start), "s",
                    " of ", 
                    str(run_time), "s"
                )
                status_string = "".join([str(x) for x in status_string])
                print '\r', status_string,
                sys.stdout.flush()

                #Update the pattern generator
                loop_start = time.time()

                self.gentleman_octopus.update()

                rate = 1/(time.time() - loop_start)
                t = loop_start - run_start
                mem = process.memory_percent()
                cpu = self.get_cpu()

                status = self.gentleman_octopus.current_pattern.status()

                IntegrationTestData(t, rate, cpu, mem, status).save(test_file)

            print "\n"


        except Exception as err:
            test_succesful = False 
            raise err

        finally:
            test_file.close()

            if test_succesful:
                print "Test completed.."
            else:
                print "TEST FAILED"

    # TODO: Methods to stop cpu meter
    def cpu_fun(self):
        while True:
            cpu_percent = psutil.cpu_percent(interval=0.3)

            with self.lock:
                self.cpu_percent = cpu_percent

    def get_cpu(self):
        with self.lock:
            cpu_percent = self.cpu_percent

        return cpu_percent

# TODO: Put this in utils?
def plot_dashes(x_locations):
    for x in x_locations:
        plt.axvline(x, color='k', linestyle='dashed', linewidth=1)

def print_results(filename, sample_period):
    results = integrationTestData.load_csv(filename, sample_period=sample_period)

    t = [result.t for result in results]
    framerate = [result.framerate for result in results]
    mem = [result.mem for result in results]
    cpu = [result.cpu for result in results]

    print "Min Framerate", np.min(framerate)
    print "Max mem", np.max(mem)
    print "Max CPU", np.max(cpu)

def plot_results(filename, sample_period):
    results = integrationTestData.load_csv(filename, sample_period=sample_period)

    t = [result.t for result in results]
    framerate = [result.framerate for result in results]
    mem = [result.mem for result in results]
    cpu = [result.cpu for result in results]
    names = [result.pattern_name for result in results]

    dashes=[]
    for i, name in enumerate(names[:-1]):
        if name != names[i-1]:
            dashes.append(t[i])

    unique_names = np.unique(names).tolist()

    num_plots = 4
    plt.subplot(num_plots, 1, 1)
    plot_dashes(dashes)
    plt.plot(t, framerate)
    plt.title('Framerate')
    plt.xlabel('Time (s)')
    plt.ylabel('Framerate')


    plt.subplot(num_plots, 1, 2)
    plot_dashes(dashes)
    plt.plot(t, mem)
    plt.title('Memory Usage')
    plt.xlabel('Time (s)')
    plt.ylabel('Memory (Mb)')

    plt.subplot(num_plots, 1, 3)
    plot_dashes(dashes)
    plt.plot(t, cpu)
    plt.title('CPU Usage')
    plt.xlabel('Time (s)')
    plt.ylabel('CPU %')
    plt.ylim([0, 100])

    plt.subplot(num_plots, 1, 4)
    
    
    pos = [unique_names.index(name) for name in names]
    plot_dashes(dashes)
    plt.scatter(t, pos, c=pos, s=100)
    plt.title('Selected Pattern')
    plt.xlabel('Time (s)')
    plt.ylabel('Pattern')
    plt.gca().yaxis.grid(True)
    plt.yticks(range(len(unique_names)), unique_names)

    print_results(filename, sample_period)

    plt.show()




if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Test the octopus!"
    )

    #TODO: Print Results
    parser.add_argument('mode', choices=['test', 'plot', 'print'], help=
        'test: Test the octopus\n'
        'plot: plot test data csv\n'
        'print: print test metrics'
    )

    parser.add_argument('-t', '--time', default=5, type=int, help="Time to test for in seconds")

    parser.add_argument('-i', '--host', help="Host", default="127.0.0.1")
    parser.add_argument('-p', '--port', type=int, help="Port", default=7890)
    parser.add_argument('-f', '--file', default="./core/tests/test_data.csv", help='test file csv')
    parser.add_argument('-s', '--sample-period', default=0, type=float, help="Period when loading data from csv")
    parser.add_argument('--pattern', default="all", help="Choose a pattern by name")

    args = parser.parse_args()

    # Check pattern against the default list
    if args.pattern == "all":
        patterns = patternList.patterns
    elif args.pattern in patternList.pattern_dict:
        patterns = [patternList.pattern_dict[args.pattern]]
    else:
        print "UNKNOWN PATTERN", args.pattern
        print "Available Patterns", "\n".join(pattern_dict.keys())
        quit() 

    # Choose your mode
    if args.mode == "test":
        integration_test = IntegrationTest(args.file, patterns=patterns, host=args.host, port=args.port)
        integration_test.run(run_time=args.time)

    elif args.mode == "plot":
        if not plotting:
            print "Cannot import Matplotlib on this device"
        plot_results(args.file, args.sample_period)

    elif args.mode =="print":
        print_results(args.file, args.sample_period)

    else:
        print parser.print_help()


