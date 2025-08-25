
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

      # TODO: Is it good practice to have many assert in a test?
      def test_search_simpleSearch(self):
          tCriteria = {'directory':'testDirectories/exampleDir0'}
          # There are exactly 5 files with extension .jpg in this directory
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=sandbox.search(query=r'\.jpg$', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Should return 0 DIRECTORIES.')
          self.assertEqual(result[2], 5, 'Should return 5 FILES with extension .jpg (case sensitive)')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)


      # TODO: Is it good practice to have many assert in a test?
      def test_search_searchDirectoryContainingOnlyEmptySubdirectories(self):
          tCriteria = {'directory':'testDirectories/exampleDir1'}
          # This subdirectory does not contain subdirectories; only files.
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=sandbox.search(query=r'.*', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 10, 'Number of total DIrECTORIES should be 10')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)


          

      # TODO: Is it good practice to have many assert in a test?
      def test_search_searchDirectoryContainingOnlyFiles(self):
          tCriteria = {'directory':'testDirectories/exampleDir2'}
          # This subdirectory does not contain subdirectories; only files.
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=sandbox.search(query=r'\.pdf$', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Directory should not contain any SUBDIRECTORY')
          self.assertEqual(result[2], 6, 'Directory should contain ONLY 6 pdf FILES')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)


          
      # TODO: Is it good practice to have many assert in a test?
      def test_search_searchEmptyDirectory(self):
          tCriteria = {'directory':'testDirectories/exampleDir3'}
          # This subdirectory does not contain subdirectories; only files.
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=sandbox.search(query=r'\.*', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Directory should not contain any SUBDIRECTORY')
          self.assertEqual(result[2], 0, 'Directory should not contain any FILES')
          self.assertEqual(result[3], 0, 'Number of ignored objects (DIRECTORIES and FILES) should 0')
               


if __name__ == "__main__":
    unittest.main(verbosity=2)
