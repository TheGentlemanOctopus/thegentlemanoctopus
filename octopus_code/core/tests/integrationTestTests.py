import unittest
import time
import numpy as np
# Standard library imports...
from mock import patch, MagicMock


import utils


from core.octopus.patterns.rpcTestPattern import RpcTestPattern

from core.tests.integrationTest import IntegrationTest

class TestIntegrationTest(unittest.TestCase):
    # Mock OPC connectionc
    # TODO: DRY up setup code
    def setUp(self):
        patcher = patch('core.octopus.opc.Client')
        opc_mock = patcher.start()
        opc_mock.can_connect = MagicMock(return_value=True)
        opc_mock.put_pixels = MagicMock()

        self.integration_test = IntegrationTest(patterns=[RpcTestPattern()])

        print_string = "".join(["\n", "Running ", self._testMethodName, "\n"])
        print print_string, "*"*len(print_string)

    def test_fails_on_exception(self):
        with patch('core.octopus.patterns.rpcTestPattern.RpcTestPattern.next_frame') as mock:
            mock.side_effect = Exception("PURPOSELY BROKEN TEST PATTERN")

            with self.assertRaises(Exception):
                self.integration_test.run(0.1)


if __name__ == '__main__':
    unittest.main()