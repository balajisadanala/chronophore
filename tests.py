import os
import timebook
import unittest


#class EntryTest(unittest.TestCase):
    #def test_create_empty_entry(self):
    #def test_create_entry(self):
    #def test_validate_entry(self):


class TimesheetTest(unittest.TestCase):
    test_file = "./test.json"
    example_file = "./example.json"

    def setUp(self):
        self.t = timebook.Timesheet()
        self.example_sheet = {
                                 "2": {
                                     "Date": "2016-02-17",
                                     "In": "12:45",
                                     "Index": 2,
                                     "Out": "16:44",
                                     "Student ID": "889249566"
                                 },
                                 "1": {
                                     "Date": "2016-02-17",
                                     "In": "10:45",
                                     "Index": 1,
                                     "Out": "15:35",
                                     "Student ID": "885894966"
                                 },
                                 "0": {
                                     "Date": "2016-02-17",
                                     "In": "10:45",
                                     "Index": 0,
                                     "Out": "13:30",
                                     "Student ID": "889870966"
                                 }
                             }


    def test_add_first_entry(self):
        """Add an entry to an empty timesheet"""
        e = timebook.Entry("2016-02-17", "889870966", "10:45", "13:30")
        self.t.add_entry(e)
        expected_sheet = {'0': {'In': '10:45',
                                'Date': '2016-02-17',
                                'Student ID': '889870966',
                                'Out': '13:30'}}
        self.assertEqual(expected_sheet, self.t.sheet)

    def test_add_additional_entry(self):
        """Add an entry to a timesheet that already has one. Make sure
        a new index is made."""
        t = timebook.Timesheet()
        e = timebook.Entry("2016-02-17", "889870966", "10:45", "13:30")
        f = timebook.Entry("2016-02-18", "889374992", "13:20", "15:30")
        self.t.add_entry(e)
        self.t.add_entry(f)
        newest_entry = {'In': '13:20',
                        'Date': '2016-02-18',
                        'Student ID': '889374992',
                        'Out': '15:30'}
        self.assertEqual(newest_entry, self.t.sheet['1'])

    def test_remove_entry(self):
        """Remove an entry from a timesheet with multiple entries"""
        t = timebook.Timesheet()
        # dicts are mutable; passed by reference unless explicitly copied:
        self.t.sheet = dict(self.example_sheet)
        self.t.remove_entry(1)
        self.assertFalse('1' in self.t.sheet)

    def test_load_sheet(self):
        """Load a sheet from a file"""
        t = timebook.Timesheet()
        self.t.load_sheet(timesheet_file=self.example_file)
        result = self.t.sheet
        expected_sheet = self.example_sheet
        self.assertEqual(result, expected_sheet)

    def test_save_sheet(self):
        """Save a sheet to a file"""
        t = timebook.Timesheet()
        self.t.sheet = self.example_sheet
        self.t.save_sheet(timesheet_file=self.test_file)
        with open(self.test_file, 'r') as f:
            result = f.read()
        with open(self.example_file, 'r') as e:
            expected_file = e.read()
        # NOTE: Watch out for trailing newline after editing file 
        self.assertMultiLineEqual(result, expected_file)
        os.remove(self.test_file)

    def test_find_entry(self):
        """Find all entries that contain a piece of data"""
        t = timebook.Timesheet()
        self.t.sheet = self.example_sheet
        entries = self.t.find_entry("10:45")
        expected_entries = ['0', '1']
        self.assertEqual(entries, expected_entries)



if __name__ == '__main__':
    unittest.main(warnings='ignore')
