
#
#
#
# TODO: Incomplete
#
#
#

import unittest

import GUI
import sandbox 

class TestCriteria(unittest.TestCase):
    
      def test_search_MaxLevels(self):
          tCriteria = {'directory':'testDirectories/exampleDir0'}
          self.assertEqual(sandbox.search(query='\.jpg$', criteria=tCriteria), (0, 0, 5, 53))
          
          

      def test_search_FileNameInclusionPattern(self):
          # files ending in .jpg (case sensitive)  
          tCriteria = {'directory':'testDirectories/exampleDir0',
                       'fileinclusionPattern':r"(.*)\.jpg$"}
          self.assertEqual(sandbox.search('', tCriteria), (0, 3, 0, 14, 5))


if __name__ == "__main__":
    unittest.main(verbosity=2)
