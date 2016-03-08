import os
import signin
import unittest

class FileTest(unittest.TestCase):
    
    entry = signin.Entry("2016-02-17", "889870966", "10:45", "13:30")
    test_file = "./test.json"
    expected = """\
{
    "Date": "2016-02-17",
    "In": "10:45",
    "Out": "13:30",
    "Student ID": "889870966"
}"""

    def setUp(self):
        open(self.test_file, 'a')
        
    def test_save_entry(self):
        signin.save_entry(self.entry, timesheet_file=self.test_file)
        with open(self.test_file, 'r') as f:
            result = f.read()
        self.assertIn(self.expected, result)

    def test_load_entry(self):
        pass
        
        
    def tearDown(self):
        os.remove(self.test_file)
        
if __name__ == '__main__':
    unittest.main(warnings='ignore')
