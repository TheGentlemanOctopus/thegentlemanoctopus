import core.octopus.patternGenerator as pg
import core.octopus.layouts.octopus as octopus
import core.octopus.opc

import time
import csv

import numpy as np

from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patterns.shambalaPattern import ShambalaPattern

import matplotlib.pyplot as plt

# Standard library imports...
from mock import patch, MagicMock


Testopus = "./core/tests/test_octopus.json" 

Test_File = "./core/tests/test_data.csv"



def speed_test(pattern, run_time=5):
    print "Speed testing", pattern.__class__.__name__

    pattern_generator = pg.PatternGenerator(octopus.ImportOctopus(Testopus), 
        framerate=20,
        enable_status_monitor=False
        )

    pattern_generator.patterns = [pattern]

    run_start = time.time()

    test_file = open(Test_File, "w")
    try: 
        while time.time() - run_start < run_time:
            print "\r", int(time.time() - run_start), "/", run_time,

            loop_start = time.time()

            pattern_generator.update()

            loop_time = time.time() - loop_start
            rate = 1.0/loop_time

            #Log data
            test_file.write(str(rate) + '\n')

    except Exception as err:
        raise err

    finally:
        test_file.close()

    rates = load_csv(Test_File)

    plt.plot(rates)
    plt.show()


    # mean_rate = np.mean(rates)
    # min_rate = np.min(rates)
    # max_rate = np.max(rates)

    # print "Mean Rate", mean_rate
    # print "Min Rate", min_rate
    # print "Max Rate", max_rate

def load_csv(filename):
    rates = []
    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            rates.append(float(row[0]))

    return np.array(rates)





if __name__ == '__main__':
    patcher = patch('core.octopus.opc.Client')
    opc_mock = patcher.start()
    opc_mock.can_connect = MagicMock(return_value=True)
    opc_mock.put_pixels = MagicMock()


    speed_test(ShambalaPattern())