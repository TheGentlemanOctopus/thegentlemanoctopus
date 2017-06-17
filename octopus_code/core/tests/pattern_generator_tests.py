import unittest
import core.octopus.patternGenerator as pg
import core.octopus.layouts.octopus as octopus
import core.octopus.opc

# Standard library imports...
from mock import patch, MagicMock


class TestPatternGeneratorMethods(unittest.TestCase):

    # Test OPC connection stuff
    @patch("core.octopus.opc.Client")
    def test_construction(self, opc_mock):
        opc_mock.can_connect = MagicMock(return_value=True)
        
        pattern_generator = pg.PatternGenerator(octopus.ImportOctopus("./core/tests/test_octopus.json"))





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