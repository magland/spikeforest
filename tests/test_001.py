import os, sys
import unittest
def append_to_path(dir0): # A convenience function
    if dir0 not in sys.path:
        sys.path.append(dir0)
append_to_path(os.getcwd()+'/..')
import spikeforest as sf
 
class Test001(unittest.TestCase):
    def setUp(self):
      pass
        
    def tearDown(self):
        pass
     
    def test_toy_example1(self):
      print('no tests yet')
 
if __name__ == '__main__':
    unittest.main()
