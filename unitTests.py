
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
          tCriteria = { 'maxLevels':2,
                      'maxTime': -1,
                      'fileinclusionPattern':'',
                      'fileexclusionPattern':'',
                      'dirinclusionPattern': '',
                      'direxclusionPattern':'',
                      'minFileSize':-1,
                      'maxFileSize':-1,
                      'maxDirs':-1,
                      'maxFiles':-1,
                      'creationDateOp':'=',
                      'creationDate':None, 
                      'lastModifiedDateOp':'=',
                      'lastModifiedDate':''}
          self.assertEqual(htmlExporter('exampleDir', 'html/template1.html', tCriteria), (-100, -1, -1, -1, -1))



if __name__ == "__main__":
    unittest.main(verbosity=2)
