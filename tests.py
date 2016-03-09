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
        entry.make_dict()
        entry.save_entry(timesheet_file=self.test_file)
        with open(self.example_file, 'r') as f:
            expected = f.read()
        with open(self.test_file, 'r') as f:
            result = f.read()
        self.assertEqual(result, expected)

    #todo: make this fail if individual member variables aren't set
    def test_load_entry(self):
        """Create an empty entry, then load values from a file"""
        entry = timebook.Entry()
        entry.load_entry(timesheet_file=self.example_file)
        result = entry.data
        expected = {'In': '10:45', 'Date': '2016-02-17', 'Student ID': '889870966', 'Out': '13:30'}
        self.assertEqual(result, expected)
    
    def test_new_index_for_empty_file(self):
        """Index of current entry will be zero if the file is empty"""
        entry = timebook.Entry("2016-02-17", "889870966", "10:45", "13:30")
        entry.new_index()
        result = entry.index
        expected = 0
        self.assertEqual(result, expected)
        
    def test_new_index_for_populated_file(self):
        """Index of current entry will be one larger than the current
        file's highest index"""
        entry = timebook.Entry("2016-02-17", "889870966", "10:45", "13:30")
        entry.new_index(self.example_file)
        result = entry.index
        expected = 1
        self.assertEqual(result, expected)
        
    def tearDown(self):
        os.remove(self.test_file)

if __name__ == '__main__':
    unittest.main(warnings='ignore')
