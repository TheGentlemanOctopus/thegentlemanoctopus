import unittest
import core.octopus.gentlemanOctopus as gentlemanOctopus
import core.octopus.layouts.octopus as octopus
import core.octopus.opc

import time

import numpy as np

from core.octopus.patterns.rpcTestPattern import RpcTestPattern
from core.octopus.patterns.shambalaPattern import ShambalaPattern

import utils

# Standard library imports...
from mock import patch, MagicMock

class TestGentlemanOctopus(unittest.TestCase):

    # Mock OPC connectionc
    def setUp(self):
        patcher = patch('core.octopus.opc.Client')
        opc_mock = patcher.start()
        opc_mock.can_connect = MagicMock(return_value=True)
        opc_mock.put_pixels = MagicMock()

        self.gentleman_octopus = gentlemanOctopus.GentlemanOctopus(octopus.ImportOctopus(utils.Testopus), enable_status_monitor=False)

        print_string = "".join(["\n", "Running ", self._testMethodName, "\n"])
        print print_string, "*"*len(print_string)

    # Useful for testing more than anything else
    def test_contains_default_pattern(self):
        self.assertTrue(len(self.gentleman_octopus.patterns) > 0)

    # Useful for testing more than anything else
    def test_timeout(self, timeout=0.1):
        start_time = time.time()
        self.gentleman_octopus.run(timeout=timeout)
        self.assertTrue(time.time() - start_time + timeout*0.01 > timeout)

    # Use integration tests to ensure we dont expect exceptions, 
    # but let's not punish ourselves during production!
    def test_continues_on_pattern_exception(self):
        self.gentleman_octopus.patterns = [RpcTestPattern]
        with patch('core.octopus.patterns.rpcTestPattern.RpcTestPattern.next_frame') as mock:
            mock.side_effect = Exception("PURPOSELY BROKEN TEST PATTERN")

            self.gentleman_octopus.run(timeout=0.1)

    # Default pattern stimulation by the siney time
    def test_siney_time_on_quiet_queue(self, timeout=0.1):
        self.gentleman_octopus.queue_receive_timeout = timeout

        # goes straight into siney time
        self.assertTrue(not self.eq_quiet())

        # Resets on input
        self.gentleman_octopus.queue.put({"eq": (0,0,0,0,0,0,0)})
        self.assertTrue(self.eq_quiet())

        # Returns to siney time on timeout
        time.sleep(timeout)
        self.assertTrue(not self.eq_quiet())


    def eq_quiet(self):
        self.gentleman_octopus.update()
        return 0 == np.sum(np.abs(self.gentleman_octopus.pattern_stream_data.eq))


if __name__ == '__main__':
    unittest.main()