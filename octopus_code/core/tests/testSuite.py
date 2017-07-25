from core.tests.integrationTestTests import TestIntegrationTest
from core.tests.patternGeneratorTests import TestPatternGenerator


import unittest

if __name__ == '__main__':
    unittest.TestLoader().loadTestsFromTestCase(TestIntegrationTest)
    unittest.TestLoader().loadTestsFromTestCase(TestPatternGenerator)

    unittest.main()