import core.octopus.patternGenerator as pg
import core.octopus.layouts.octopus as octopus
import core.octopus.opc

import os
import sys

import psutil
import time
import csv
import argparse

import numpy as np

from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patterns.shambalaPattern import ShambalaPattern

# Standard library imports...
#from mock import patch, MagicMock
#TODO: deleye
import mock_opc_server

import core.tests.speedTestData as speedTestData
from core.tests.speedTestData import SpeedTestData

# matplotlib may not work on the odroid
try:
    import matplotlib.pyplot as plt
    import core.tests.utils as utils
    plotting = True

except Exception as e:
    plotting = False

Testopus = "./core/tests/test_octopus.json" 
Test_File = "./core/tests/test_data.csv"

def speed_test(pattern, run_time=10):
    pattern_generator = pg.PatternGenerator(octopus.ImportOctopus(Testopus), 
        framerate=20,
        enable_status_monitor=False
        )

    pattern_generator.patterns = [pattern]
    run_start = time.time()
    process = psutil.Process(os.getpid())
    test_file = open(Test_File, "w")

    test_succesful = True

    # Run the Pattern for a bit and log data
    try: 
        while time.time() - run_start < run_time:
            status_string = (
                "Testing ", pattern.__class__.__name__, ": ", 
                int(time.time() - run_start), "s",
                " of ", 
                str(run_time), "s"
            )
            status_string = "".join([str(x) for x in status_string])
            print '\r', status_string,
            sys.stdout.flush()

            #Update the pattern generator
            loop_start = time.time()
            pattern_generator.update()

            t = loop_start - run_start
            rate = 1/(time.time() - loop_start)
            mem = process.memory_percent()
            cpu = psutil.cpu_percent(interval=None)

            SpeedTestData(t, rate, cpu, mem).save(test_file)

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

def print_results(filename):
    results = speedTestData.load_csv(filename)

    t = [result.t for result in results]
    framerate = [result.framerate for result in results]
    mem = [result.mem for result in results]
    cpu = [result.cpu for result in results]

    print "Min Framerate", np.min(framerate)
    print "Max mem", np.max(mem)
    print "Max CPU", np.max(cpu)


def plot_results(filename):
    results = speedTestData.load_csv(filename)

    t = [result.t for result in results]
    framerate = [result.framerate for result in results]
    mem = [result.mem for result in results]
    cpu = [result.cpu for result in results]

    ax = utils.new_axes()
    ax.plot(t, framerate)
    ax.set_title('Framerate')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Framerate')

    ax = utils.new_axes()
    ax.plot(t, mem)
    ax.set_title('Memory Usage')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Memory (Mb)')

    ax = utils.new_axes()
    ax.plot(t, cpu)
    ax.set_title('Framerate')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('CPU')

    print_results(filename)

    plt.show()




if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Test the octopus!"
    )

    #TODO: Print Results
    parser.add_argument('mode', choices=['test', 'plot'], help=
        'test: Test the octopus\n'
        'plot: plot test data csv'
    )

    parser.add_argument('-t', type=int, help="Time to test for in seconds", default=5)
    
    args = parser.parse_args()

    if args.mode == "test":
        speed_test(ShambalaPattern(), run_time=args.t)

    elif args.mode == "plot":
        if not plotting:
            print "Cannot import Matplotlib on this device"
        plot_results(Test_File)

    elif args.mode =="print":
        print_results(Test_File)

    else:
        print parser.print_help()


