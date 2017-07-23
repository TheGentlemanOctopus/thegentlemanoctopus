import core.octopus.patternGenerator as pg
import core.octopus.layouts.octopus as octopus
import core.octopus.opc

import os

import psutil
import time
import csv

import numpy as np

from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patterns.shambalaPattern import ShambalaPattern

import matplotlib.pyplot as plt

# Standard library imports...
#from mock import patch, MagicMock
import mock_opc_server


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

            loop_time = time.time() - loop_start
            rate = 1.0/loop_time

            mem = process.memory_percent()
            cpu = psutil.cpu_percent(interval=None)

            #Log data
            data = [time.time(), rate, mem, cpu]
            test_file.write(",".join([str(x) for x in data]) + '\n')


    except Exception as err:
        raise err

    finally:
        test_file.close()

    plot_results(Test_File)


def plot_results(filepath):
    t, rates, mems, cpus = load_csv(filepath)

    plt.plot(t, mems)
    plt.show()

def load_csv(filename):
    t = []
    rates = []
    mem = []
    cpu = []
    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            t.append(float(row[0]))
            rates.append(float(row[1]))
            mem.append(float(row[2]))
            cpu.append(float(row[3]))

    return t, rates, mem, cpu

if __name__ == '__main__':
    speed_test(ShambalaPattern())