
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

      def test_search_simpleSearch(self):
          tCriteria = {'directory':'testDirectories/exampleDir0'}
          # There are exactly 5 files with extension .jpg in this directory
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          self.assertEqual(sandbox.search(query=r'\.jpg$', criteria=tCriteria)[2], 5)


          
      def test_search_NonRecursive(self):
          tCriteria = {'directory': 'testDirectories/exampleDir0',
                       'nonRecursive': True}
          self.assertEqual(sandbox.search(query=r'\.*', criteria=tCriteria), (0, 3, 9, 0))
          
          

      def test_search_FileNameInclusionPattern(self):
          # files ending in .jpg (case sensitive)  
          tCriteria = {'directory':'testDirectories/exampleDir0',
                       'fileinclusionPattern':r"(.*)\.jpg$"}
          self.assertEqual(sandbox.search('', tCriteria), (0, 3, 0, 14, 5))


if __name__ == "__main__":
    unittest.main(verbosity=2)
