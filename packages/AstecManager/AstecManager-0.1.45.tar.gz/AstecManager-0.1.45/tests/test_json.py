import unittest
import sys

sys.path.append("../AstecManager/")
from AstecManager.libs.jsonlib import getMetaDataFile, loadMetaData,createMetaDataFile


class TestJson(unittest.TestCase):
    def testFileName(self):
        self.assertIsNotNone(getMetaDataFile())

    def testExistingFile(self):
        embryoPath = "./TEST_DATA/"
        self.assertIsNotNone(loadMetaData(embryoPath))

    def testNotExistingFile(self):
        embryoPath = "./TEST_NODATA/"
        self.assertIsNone(loadMetaData(embryoPath))

    def testNoFolder(self):
        embryoPath = "./FNJEAJID/"
        self.assertIsNone(loadMetaData(embryoPath))

    def testCreateExistingFile(self):
        embryoPath = "./TEST_DATA/"
        self.assertEqual(createMetaDataFile(embryoPath),False)

    def testCreateNonExistingFile(self):
        embryoPath = "./TEST_NODATA/"
        self.assertEqual(createMetaDataFile(embryoPath),True)


if __name__ == '__main__':
    unittest.main()
