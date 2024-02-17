import unittest
from src.airflow_dataform_parser.dataform_parser import DataformParser
class TestSimple(unittest.TestCase):
    def test_module_path(self):
        path = DataformParser.getModulePath()
        print(path)
        self.assertEqual(testModule.name, "test-module")

if __name__ == '__main__':
    unittest.main()