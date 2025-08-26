
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
          tCriteria = {'directory':'testDirectories/testDir0'}
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
          # This directory contains 10 empty subdirectories 
          tCriteria = {'directory':'testDirectories/testDir1'}
          
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=sandbox.search(query=r'.*', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 10, 'Number of total DIrECTORIES should be 10')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)


          

      # TODO: Is it good practice to have many assert in a test?
      def test_search_searchDirectoryContainingOnlyFiles(self):
          tCriteria = {'directory':'testDirectories/testDir2'}
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
          tCriteria = {'directory':'testDirectories/testDir3'}
          # This directory is empty.
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=sandbox.search(query=r'\.*', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Directory should not contain any SUBDIRECTORY')
          self.assertEqual(result[2], 0, 'Directory should not contain any FILES')
          self.assertEqual(result[3], 0, 'Number of ignored objects (DIRECTORIES and FILES) should 0')
               


      def test_search_minimumFileSize(self):
          # Return ONLY FILES with minimum file size 1118488 Bytes
          # NOTE: there is one file with size exactly equal to 1118487 Bytes
          tCriteria = {'directory':'testDirectories/testDir0',
                       'minFileSize':1118488,
                       'noDirs':True}
          
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=sandbox.search(query=r'\.*', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Should return 0 DIRECTORIES.')
          self.assertEqual(result[2], 4, 'Should return 4 FILES with extension with filesize >= 1118488 Bytes')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)


if __name__ == "__main__":
    unittest.main(verbosity=2)
