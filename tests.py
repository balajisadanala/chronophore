import os
import timebook
import unittest
import unittest.mock


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
            "1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2": {
                "Date": "2016-02-17",
                "In": "10:45",
                "Out": "13:30",
                "Student ID": "889870966",
            },
            "2ed2be60-693a-44fe-adc1-2803a674ec9b": {
                "Date": "2016-02-17",
                "In": "10:45",
                "Out": "",
                "Student ID": "885894966",
            },
            "7b4ae0fc-3801-4412-998f-ace14829d150": {
                "Date": "2016-02-17",
                "In": "12:45",
                "Out": "16:44",
                "Student ID": "889249566",
            },
        }

    @unittest.mock.patch(
        'timebook.Timesheet._make_index',
        return_value='3b27d0f8-3801-4319-398f-ace18829d150'
    )
    def test_add_entry(self, make_index):
        """Add an entry to an empty timesheet"""
        e = timebook.Entry("2016-02-17", "889870966", "10:45", "13:30")
        self.t.add_entry(e)
        expected_sheet = {
            "3b27d0f8-3801-4319-398f-ace18829d150": {
                "In": "10:45",
                "Date": "2016-02-17",
                "Student ID": "889870966",
                "Out": "13:30",
            },
        }
        self.assertEqual(expected_sheet, self.t.sheet)

    def test_remove_entry(self):
        """Remove an entry from a timesheet with multiple entries"""
        # dicts are mutable; passed by reference unless explicitly copied:
        self.t.sheet = dict(self.example_sheet)
        self.t.remove_entry("1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2")
        self.assertFalse("1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2" in self.t.sheet)

    def test_load_sheet(self):
        """Load a sheet from a file"""
        self.t.load_sheet(timesheet_file=self.example_file)
        result = self.t.sheet
        expected_sheet = self.example_sheet
        self.assertEqual(result, expected_sheet)

    def test_save_sheet(self):
        """Save a sheet to a file"""
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
        self.t.sheet = self.example_sheet
        entries = self.t.find_entry("10:45")
        expected_entries = [
            "1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2",
            "2ed2be60-693a-44fe-adc1-2803a674ec9b"
        ]
        self.assertEqual(entries, expected_entries)

    def test_signed_in(self):
        """Find all entries of people that are currently signed in
        (there is a time_in value, but not a time_out value
        """
        self.t.sheet = self.example_sheet
        entries = self.t.list_signed_in()
        expected_entries = ["2ed2be60-693a-44fe-adc1-2803a674ec9b"]
        self.assertEqual(entries, expected_entries)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
