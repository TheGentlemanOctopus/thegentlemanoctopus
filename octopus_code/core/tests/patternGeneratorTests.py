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

class TestPatternGenerator(unittest.TestCase):

    # Mock OPC connectionc
    def setUp(self):
        patcher = patch('core.octopus.opc.Client')
        opc_mock = patcher.start()
        opc_mock.can_connect = MagicMock(return_value=True)
        opc_mock.put_pixels = MagicMock()

        self.pattern_generator = pg.PatternGenerator(octopus.ImportOctopus(utils.Testopus), enable_status_monitor=False)

        print_string = "".join(["\n", "Running ", self._testMethodName, "\n"])
        print print_string, "*"*len(print_string)

    # Useful for testing more than anything else
    def test_contains_default_pattern(self):
        self.assertTrue(len(self.pattern_generator.patterns) > 0)

    # Useful for testing more than anything else
    def test_timeout(self, timeout=0.1):
        start_time = time.time()
        self.pattern_generator.run(timeout=timeout)
        self.assertTrue(time.time() - start_time + timeout*0.01 > timeout)

    # Use integration tests to ensure we dont expect exceptions, 
    # but let's not punish ourselves during production!
    def test_continues_on_pattern_exception(self):
        self.pattern_generator.patterns = [RpcTestPattern]
        with patch('core.octopus.patterns.rpcTestPattern.RpcTestPattern.next_frame') as mock:
            mock.side_effect = Exception("PURPOSELY BROKEN TEST PATTERN")

            self.pattern_generator.run(timeout=0.1)

    # Default pattern stimulation by the siney time
    def test_siney_time_on_quiet_queue(self, timeout=0.1):
        self.pattern_generator.queue_receive_timeout = timeout

        # goes straight into siney time
        self.assertTrue(not self.eq_quiet())

        # Resets on input
        self.pattern_generator.queue.put({"eq": (0,0,0,0,0,0,0)})
        self.assertTrue(self.eq_quiet())

        # Returns to siney time on timeout
        time.sleep(timeout)
        self.assertTrue(not self.eq_quiet())


    def eq_quiet(self):
        self.pattern_generator.update()
        return 0 == np.sum(np.abs(self.pattern_generator.pattern_stream_data.eq))


if __name__ == '__main__':
    unittest.main()