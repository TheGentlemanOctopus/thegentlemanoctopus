from core.tests.integrationTestTests import TestIntegrationTest
from core.tests.gentlemanOctopusTests import TestGentlemanOctopus


import unittest

#TODO Clean build

def main():
    print "loadinfg"
    unittest.TestLoader().loadTestsFromTestCase(TestIntegrationTest)
    unittest.TestLoader().loadTestsFromTestCase(TestGentlemanOctopus)

    unittest.main()

if __name__ == '__main__':
    main()