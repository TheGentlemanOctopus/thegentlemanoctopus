import unittest
import core.octopus.patternGenerator as pg
import core.octopus.layouts.octopus as octopus
import core.octopus.opc

import time

import numpy as np

from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patterns.shambalaPattern import ShambalaPattern

# Standard library imports...
from mock import patch, MagicMock

Testopus = "./core/tests/test_octopus.json" 

class TestPatternGeneratorMethods(unittest.TestCase):

    # Mock OPC connectionc
    def setUp(self):
        patcher = patch('core.octopus.opc.Client')
        opc_mock = patcher.start()
        opc_mock.can_connect = MagicMock(return_value=True)
        opc_mock.put_pixels = MagicMock()

        self.pattern_generator = pg.PatternGenerator(octopus.ImportOctopus(Testopus))

    def test_contains_default_pattern(self):
        self.assertTrue(len(self.pattern_generator.patterns) > 0)

    def test_timeout(self, timeout=0.1):
        start_time = time.time()
        self.pattern_generator.run(timeout=timeout)
        self.assertTrue(time.time() - start_time + timeout*0.01 > timeout)

    def test_speed_shambala_pattern(self, run_time=5, framerate=20):
        pattern_generator = pg.PatternGenerator(octopus.ImportOctopus(Testopus), 
            framerate=framerate,
            strict=True
            )

        run_start = time.time()
        loop_times = []

        while time.time() - run_start < run_time:
            loop_start = time.time()

            if pattern_generator.update():
                raise Exception(pattern_generator.current_pattern.__class__.__name__ + "Threw an Exception")

            loop_end = time.time() - loop_start
            loop_times.append(loop_end)

        mean_rate = 1.0/np.mean(loop_times)
        min_rate = 1.0/np.max(loop_times)
        max_rate = 1.0/np.min(loop_times)

        print "Mean Rate", mean_rate
        print "Min Rate", min_rate
        print "Max Rate", max_rate


    def test_continues_on_pattern_exception(self):
        pass

if __name__ == '__main__':
    unittest.main()