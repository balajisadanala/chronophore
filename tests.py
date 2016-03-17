import os
import timebook
import unittest


class TimesheetTest(unittest.TestCase):
    def test_add_first_entry(self):
        """Add an entry to an empty timesheet"""
        t = timebook.Timesheet()
        e = timebook.Entry("2016-02-17", "889870966", "10:45", "13:30")
        t.add_entry(e)
        expected_sheet = {'0': {'In': '10:45',
                                'Date': '2016-02-17',
                                'Student ID': '889870966',
                                'Out': '13:30'}}
        self.assertEqual(expected_sheet,t.sheet)

    def test_add_new_entry(self):
        t = timebook.Timesheet()
        e = timebook.Entry("2016-02-17", "889870966", "10:45", "13:30")
        f = timebook.Entry("2016-02-18", "889374992", "13:20", "15:30")
        t.add_entry(e)
        t.add_entry(f)
        newest_entry = {'In': '13:20',
                        'Date': '2016-02-18',
                        'Student ID': '889374992',
                        'Out': '15:30'}
        self.assertEqual(newest_entry,t.sheet['1'])
    #def test_load_sheet(self):

    #def test_save_sheet(self):


class EntryTest(unittest.TestCase):
    test_file = "./test.json"
    example_file = "./example.json"

    def setUp(self):
        open(self.test_file, 'a')

    #todo: make this fail if individual member variables aren't set
    def test_load_entry(self):
        """Create an empty entry, then load values from a file"""
        entry = timebook.Entry()
        entry.load_entry(timesheet_file=self.example_file)
        result = entry.data
        expected_entry = {'In': '10:45',
                          'Date': '2016-02-17',
                          'Student ID': '889870966',
                          'Out': '13:30'}
        self.assertEqual(result, expected_entry)
    
    def test_new_index_for_empty_file(self):
        """Index of current entry will be zero if the file is empty"""
        entry = timebook.Entry("2016-02-17", "889870966", "10:45", "13:30")
        entry.new_index(self.test_file)
        result = entry.index
        expected = 0
        self.assertEqual(result, expected)
        
    def tearDown(self):
        os.remove(self.test_file)

if __name__ == '__main__':
    unittest.main(warnings='ignore')
