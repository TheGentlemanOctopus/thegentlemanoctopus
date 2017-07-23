import core.octopus.patternGenerator as pg
import core.octopus.layouts.octopus as octopus
import core.octopus.opc

import os

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

# This may not work on the odroid
try:
    import matplotlib.pyplot as plt
    import core.tests.utils as utils
    plotting = True
except Exception as e:
    plotting = False

Testopus = "./core/tests/test_octopus.json" 
Test_File = "./core/tests/test_data.csv"

def speed_test(pattern, run_time=10):
    print "Speed testing", pattern.__class__.__name__

    pattern_generator = pg.PatternGenerator(octopus.ImportOctopus(Testopus), 
        framerate=20,
        enable_status_monitor=False
        )

    pattern_generator.patterns = [pattern]
    run_start = time.time()
    process = psutil.Process(os.getpid())
    test_file = open(Test_File, "w")

    # Run the Pattern for a bit and log data
    try: 
        while time.time() - run_start < run_time:
            #print int(time.time() - run_start), "/", run_time

            loop_start = time.time()

            pattern_generator.update()

            t = loop_start - run_start
            rate = 1/(time.time() - loop_start)
            mem = process.memory_percent()
            cpu = psutil.cpu_percent(interval=None)

            SpeedTestData(t, rate, cpu, mem).save(test_file)


    except Exception as err:
        raise err

    finally:
        test_file.close()

    print "Test completed.."

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

    plt.show()




if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    #TODO: Print Results
    parser.add_argument('mode', choices=['test', 'plot'], help=
        'test: Test the octopus\n'
        'plot: plot test data csv'
    )
    
    args = parser.parse_args()

    if args.mode == "test":
        speed_test(ShambalaPattern())
    elif args.mode == "plot":
        if not plotting:
            print "Cannot import Matplotlib on this device"

        plot_results(Test_File)
    else:
        print parser.print_help()


