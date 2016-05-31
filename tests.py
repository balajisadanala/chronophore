import filecmp
import json
import os
import timebook
import unittest
import unittest.mock
from datetime import datetime


class InterfaceTest(unittest.TestCase):
    def setUp(self):
        self.e = timebook.Entry(
            user_id="885894966",
            date="2016-02-17",
            time_in="10:45",
            time_out=None,
            index="2ed2be60-693a-44fe-adc1-2803a674ec9b"
        )
        self.t = timebook.Timesheet()
        self.t.save_entry(self.e)

    @unittest.mock.patch(
        'timebook.Entry._make_index',
        return_value='3b27d0f8-3801-4319-398f-ace18829d150'
    )
    def test_sign_in(self, make_index):
        """Sign in with a new ID."""
        timebook.sign(self.t, "882870l92")
        self.assertEqual(
            self.t.sheet['3b27d0f8-3801-4319-398f-ace18829d150']['User ID'],
            "882870l92")

    def test_sign_out(self):
        """Sign out with an ID that's currently signed in."""
        timebook.sign(self.t, "885894966")
        self.assertIsNotNone(self.t.sheet[self.e.index])
        self.assertNotIn(self.e.index, self.t.signedin)


class EntryTest(unittest.TestCase):
    @unittest.mock.patch(
        'timebook.Entry._get_current_datetime',
        return_value=datetime(2016, 5, 9, 15, 43, 41, 0)
    )
    def test_create_entry(self, get_current_datetime):
        """Create an entry with an ID."""
        e = timebook.Entry(user_id="882369423")
        self.assertEqual(e.date, "2016-05-09")
        self.assertEqual(e.time_in, "15:43:41")
        self.assertEqual(e.time_out, "")
        self.assertIsNotNone(e.index)

    def test_comparison(self):
        """Test whether '==' and '!=' work properly."""
        entry = timebook.Entry(
            user_id="889870966",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30",
            index="1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2"
        ) 

        equal_entry = timebook.Entry(
            user_id="889870966",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30",
            index="1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2"
        ) 

        self.assertTrue(entry == equal_entry)
        self.assertTrue(equal_entry == entry)
        self.assertFalse(entry != equal_entry)
        self.assertFalse(equal_entry != entry)

    def test_repr(self):
        """Test whether the repr of an Entry evaluates to an
        equivalent Entry object.
        """
        e = timebook.Entry()
        self.assertEqual(e, eval(repr(e)))

    @unittest.mock.patch(
            'timebook.Entry._get_current_datetime',
            return_value=datetime(2016, 5, 9, 17, 30, 17, 0)
    )
    def test_sign_out(self, get_current_datetime):
        """Create an entry, then sign out of it."""
        e = timebook.Entry(user_id="882369423")
        e.sign_out()
        self.assertEqual(e.time_out, "17:30:17")


class TimesheetTest(unittest.TestCase):
    test_file = "./test.json"
    example_file = "./example.json"

    def setUp(self):
        self.t = timebook.Timesheet()
        # this matches the contents of the example_file
        self.example_sheet = {
            "1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2": {
                "Date": "2016-02-17",
                "In": "10:45",
                "Out": "13:30",
                "User ID": "889870966",
            },
            "2ed2be60-693a-44fe-adc1-2803a674ec9b": {
                "Date": "2016-02-17",
                "In": "10:45",
                "Out": "",
                "User ID": "885894966",
            },
            "7b4ae0fc-3801-4412-998f-ace14829d150": {
                "Date": "2016-02-17",
                "In": "12:45",
                "Out": "16:44",
                "User ID": "889249566",
            },
        }

    @unittest.mock.patch(
        'timebook.Entry._make_index',
        return_value='3b27d0f8-3801-4319-398f-ace18829d150'
    )
    def test_save_entry(self, make_index):
        """Add an entry to an empty timesheet."""
        e = timebook.Entry("889870966", "2016-02-17", "10:45", "13:30")
        self.t.save_entry(e)
        expected_sheet = {
            "3b27d0f8-3801-4319-398f-ace18829d150": {
                "In": "10:45",
                "Date": "2016-02-17",
                "User ID": "889870966",
                "Out": "13:30",
            },
        }
        self.assertEqual(self.t.sheet, expected_sheet)

    def test_remove_entry(self):
        """Remove an entry from a timesheet with multiple entries."""
        index = "1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2"
        # dicts are mutable; passed by reference unless explicitly copied:
        self.t.sheet = dict(self.example_sheet)
        self.t.remove_entry(index)
        self.assertFalse(index in self.t.sheet)

    def test_load_sheet(self):
        """Load a sheet from a file."""
        self.t.load_sheet(timesheet_file=self.example_file)
        loaded_sheet = self.t.sheet
        self.assertEqual(loaded_sheet, self.example_sheet)

    def test_save_sheet(self):
        """Save a sheet to a file."""
        self.t.sheet = dict(self.example_sheet)
        self.t.save_sheet(timesheet_file=self.test_file)
        self.assertTrue(filecmp.cmp(self.test_file, self.example_file))
        os.remove(self.test_file)

    def test_search_entries(self):
        """Find all entries that contain a matching piece of data."""
        self.t.sheet = self.example_sheet
        indices = self.t.search_entries("10:45")
        expected_indices = {
            "1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2",
            "2ed2be60-693a-44fe-adc1-2803a674ec9b"
        }
        self.assertEqual(indices, expected_indices)

    def test_load_entry(self):
        """Initialize an entry object with data from the timesheet"""
        self.t.sheet = self.example_sheet
        entry = self.t.load_entry("1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2")
        expected_entry = timebook.Entry(
            user_id="889870966",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30",
            index="1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2"
        )
        self.assertEqual(entry, expected_entry)

    def test_find_signed_in(self):
        """Find all entries of people that are currently signed in
        (there is a time_in value, but not a time_out value).
        """
        self.t.sheet = self.example_sheet
        self.t._update_signed_in()
        expected_entries = ["2ed2be60-693a-44fe-adc1-2803a674ec9b"]
        self.assertEqual(self.t.signedin, expected_entries)

    @unittest.mock.patch(
        'timebook.Entry._make_index',
        return_value='3b27d0f8-3801-4319-398f-ace18829d150'
    )
    def test_sign_in(self, make_index):
        """User signs in, and they are added to the list of currently
        signed in users.
        """
        e = timebook.Entry("889870966", "2016-02-17", "10:45")
        self.t.save_entry(e)
        self.assertIn("3b27d0f8-3801-4319-398f-ace18829d150", self.t.signedin)

    def test_sign_out(self):
        """User signs out, and they are removed from the list of currently
        signed in users.
        """
        self.t.sheet = dict(self.example_sheet)
        e = timebook.Entry("889870966", "2016-02-17", "10:45", "13:30")
        index = "2ed2be60-693a-44fe-adc1-2803a674ec9b"
        self.t.save_entry(e, index)
        self.assertNotIn(index, self.t.signedin)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
