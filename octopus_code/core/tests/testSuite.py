from core.tests.integrationTestTests import TestIntegrationTest
from core.tests.gentlemanOctopusTests import TestGentlemanOctopus


import unittest

if __name__ == '__main__':
    unittest.TestLoader().loadTestsFromTestCase(TestIntegrationTest)
    unittest.TestLoader().loadTestsFromTestCase(TestGentlemanOctopus)

    unittest.main()