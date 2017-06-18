import unittest
import core.octopus.patternGenerator as pg
import core.octopus.layouts.octopus as octopus
import core.octopus.opc

import time

from core.octopus.patterns.rpcTestPattern import RpcTestPattern

# Standard library imports...
from mock import patch, MagicMock


class TestPatternGeneratorMethods(unittest.TestCase):

    # Test OPC connection stuff
    def setUp(self):
        patcher = patch('core.octopus.opc.Client')
        opc_mock = patcher.start()
        opc_mock.can_connect = MagicMock(return_value=True)
        self.pattern_generator = pg.PatternGenerator(octopus.ImportOctopus("./core/tests/test_octopus.json"))

    def test_contains_default_pattern(self):
        self.assertTrue(len(self.pattern_generator.patterns) > 0)

    def test_timeout(self, timeout=0.1):
        start_time = time.time()
        self.pattern_generator.run(timeout=timeout)
        self.assertTrue(time.time() - start_time + timeout*0.01 > timeout)





    # Test UDP connection setuff

    # Test Framerate?

    # Exceptions from pattern generation



    # def test_upper(self):
    #     self.assertEqual('foo'.upper(), 'FOO')

    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)

if __name__ == '__main__':
    unittest.main()