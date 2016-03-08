import os
import timebook
import unittest


class EntryTest(unittest.TestCase):
    test_file = "./test.json"
    example_file = "./example.json"

    def setUp(self):
        open(self.test_file, 'a')

    def test_save_entry(self):
        """Create an entry with values, then save them to a file"""
        entry = timebook.Entry("2016-02-17", "889870966", "10:45", "13:30")
        entry.save_entry(timesheet_file=self.test_file)
        with open(self.example_file, 'r') as f:
            expected = f.read()
        with open(self.test_file, 'r') as f:
            result = f.read()
        self.assertEqual(expected, result)

    def test_load_entry(self):
        """Create an empty entry, then load values from a file"""
        entry = timebook.Entry()
        entry.load_entry(timesheet_file=self.example_file)
        result = entry.data
        expected = {'In': '10:45', 'Date': '2016-02-17', 'Student ID': '889870966', 'Out': '13:30'}
        self.assertEqual(expected, result)

    def tearDown(self):
        os.remove(self.test_file)

if __name__ == '__main__':
    unittest.main(warnings='ignore')
