
#
#
#
# TODO: Incomplete
#
#
#

import unittest

from sandbox import htmlExporter

class TestCriteria(unittest.TestCase):
    
      def testMaxLevels(self):
          tCriteria = {}
          self.assertEqual(htmlExporter('testDirectories/exampleDir0', 'html/template1.tmpl', tCriteria), (0, 3, 0, 14, 25))
          
          #tCriteria = { 'maxLevels':2 }
          #self.assertEqual(htmlExporter('testDirectories/exampleDir0', 'html/template1.tmpl', tCriteria), (0, 3, 0, 7, 6))

      def testFileNameInclusion(self):
          # files ending in .jpg (case sensitive)  
          tCriteria = {'fileinclusionPattern':r"(.*)\.jpg$"}
          self.assertEqual(htmlExporter('testDirectories/exampleDir0', 'html/template1.tmpl', tCriteria), (0, 3, 0, 14, 5))


if __name__ == "__main__":
    unittest.main(verbosity=2)
