import filecmp
import logging
import pathlib
import unittest
import unittest.mock
from datetime import datetime
from timebook.controller import Interface
from timebook.models import Entry, Timesheet

logging.disable(logging.CRITICAL)


class InterfaceTest(unittest.TestCase):
    test_file = pathlib.Path('.', 'tests', 'test.json')
    users_file = pathlib.Path('.', 'tests', 'users.json')
    registered_id = "876543210"
    i = Interface(users_file)

    def setUp(self):
        self.t = Timesheet(data_file=self.test_file)

    def test_detect_duplicates(self):
        duplicate_keys_file = pathlib.Path(
            '.', 'tests', 'duplicate_keys.json'
        )
        lines = ["{", '"key":1234,', '"key":5678', "}"]
        with duplicate_keys_file.open('w') as f:
            f.write('\n'.join(lines))
        with self.assertRaises(self.i.DuplicateKeysError):
            self.i._detect_duplicates(duplicate_keys_file)
        duplicate_keys_file.unlink()

    def test_is_valid(self):
        self.assertFalse(self.i.is_valid("12"))
        self.assertFalse(self.i.is_valid("1234567890"))
        self.assertFalse(self.i.is_valid("1234 56789"))
        self.assertFalse(self.i.is_valid(""))
        self.assertFalse(self.i.is_valid(" "))
        self.assertFalse(self.i.is_valid("123abc"))
        self.assertFalse(self.i.is_valid('\n'))
        self.assertTrue(self.i.is_valid("123456789"))
        self.assertTrue(self.i.is_valid(" 123456789"))
        self.assertTrue(self.i.is_valid("123456789 "))

    def test_is_registered(self):
        self.assertFalse(self.i.is_registered("888888888"))
        self.assertTrue(self.i.is_registered(self.registered_id))

    def test_sign_invalid(self):
        with self.assertRaises(ValueError):
            self.i.sign(self.t, "1234567890")

    def test_sign_not_registered(self):
        with self.assertRaises(self.i.NotRegisteredError):
            self.i.sign(self.t, "888888888")

    def test_sign_duplicates(self):
        """Sign in with multiple instances of being signed in."""
        duplicate_id = self.registered_id
        for _ in range(2):
            e = Entry(duplicate_id)
            self.t.save_entry(e)
        with self.assertRaises(self.i.DuplicateEntryError):
            self.i.sign(self.t, duplicate_id)

    @unittest.mock.patch(
            'timebook.models.Entry._make_index',
            return_value='3b27d0f8-3801-4319-398f-ace18829d150')
    def test_sign_in(self, make_index):
        """Sign in with a new ID."""
        # NOTE(amin): remember that time you spent 40 minutes trying to
        # figure out why this test was failing, only to realize with horror
        # that there is a difference between "882870192" and "882870l92"?
        user_id = self.registered_id
        self.i.sign(self.t, user_id)
        self.assertEqual(
            self.t.sheet['3b27d0f8-3801-4319-398f-ace18829d150']['User ID'],
            user_id
        )

    def test_sign_out(self):
        """Sign out with an ID that's currently signed in."""
        self.e = Entry(
            user_id=self.registered_id,
            date="2016-02-17",
            time_in="10:45",
            time_out=None,
            index="2ed2be60-693a-44fe-adc1-2803a674ec9b"
        )
        self.t.save_entry(self.e)
        self.i.sign(self.t, self.registered_id)
        self.assertIsNotNone(self.t.sheet[self.e.index])
        self.assertNotIn(self.e.index, self.t.signed_in)


class EntryTest(unittest.TestCase):
    @unittest.mock.patch(
            'timebook.models.Entry._get_current_datetime',
            return_value=datetime(2016, 5, 9, 15, 43, 41, 0))
    def test_create_entry(self, get_current_datetime):
        """Create an entry with an ID."""
        e = Entry(user_id="882369423")
        self.assertEqual(e.date, "2016-05-09")
        self.assertEqual(e.time_in, "15:43:41")
        self.assertEqual(e.time_out, "")
        self.assertIsNotNone(e.index)

    def test_repr(self):
        """Test whether the repr of an Entry evaluates to an
        equivalent Entry object.
        """
        e = Entry()
        self.assertEqual(e, eval(repr(e)))

    def test_comparison(self):
        """Test whether '==' and '!=' work properly."""
        entry = Entry(
            user_id="889870966",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30",
            index="1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2"
        )

        equal_entry = Entry(
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

    @unittest.mock.patch(
            'timebook.models.Entry._get_current_datetime',
            return_value=datetime(2016, 5, 9, 17, 30, 17, 0))
    def test_sign_out(self, get_current_datetime):
        """Create an entry, then sign out of it."""
        e = Entry(user_id="882369423")
        e.sign_out()
        self.assertEqual(e.time_out, "17:30:17")


class TimesheetTest(unittest.TestCase):
    test_file = pathlib.Path('.', 'tests', 'test.json')
    example_file = pathlib.Path('.', 'tests', 'example.json')

    def setUp(self):
        self.maxDiff = None
        self.t = Timesheet(data_file=self.test_file)
        # this matches the contents of the example_file
        self.example_sheet = {
            "1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2": {
                "Date": "2016-02-17",
                "In": "10:45",
                "Name": "Test",
                "Out": "13:30",
                "User ID": "889870966",
            },
            "2ed2be60-693a-44fe-adc1-2803a674ec9b": {
                "Date": "2016-02-17",
                "In": "10:45",
                "Name": "Bork",
                "Out": "",
                "User ID": "885894966",
            },
            "7b4ae0fc-3801-4412-998f-ace14829d150": {
                "Date": "2016-02-17",
                "In": "12:45",
                "Name": "User",
                "Out": "16:44",
                "User ID": "889249566",
            },
        }

    def test_find_signed_in(self):
        """Find all entries of people that are currently signed in
        (all entries that have a time_in value, but not a time_out value).
        """
        self.t.sheet = self.example_sheet
        self.t._update_signed_in()
        expected_entries = ["2ed2be60-693a-44fe-adc1-2803a674ec9b"]
        self.assertEqual(self.t.signed_in, expected_entries)

    def test_add_signed_in(self):
        """User signs in, and they are added to the list of currently
        signed in users.
        """
        e = Entry(
            user_id="889870966",
            date="2016-02-17",
            time_in="10:45"
        )
        self.t.save_entry(e)
        self.assertIn(e.index, self.t.signed_in)

    def test_remove_signed_in(self):
        """User signs out, and they are removed from the list of currently
        signed in users.
        """
        self.t.sheet = dict(self.example_sheet)
        e = Entry(
            user_id="889870966",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30"
        )
        self.t.save_entry(e)
        self.assertNotIn(e.index, self.t.signed_in)

    def test_load_entry(self):
        """Initialize an entry object with data from the timesheet."""
        self.t.sheet = self.example_sheet
        entry = self.t.load_entry("1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2")
        expected_entry = Entry(
            user_id="889870966",
            name="Test",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30",
            index="1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2"
        )
        self.assertEqual(entry, expected_entry)

    @unittest.mock.patch(
            'timebook.models.Entry._make_index',
            return_value='3b27d0f8-3801-4319-398f-ace18829d150')
    def test_save_entry(self, make_index):
        """Add an entry to an empty timesheet."""
        e = Entry(
            user_id="889870966",
            name="Test",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30"
        )
        self.t.save_entry(e)
        expected_sheet = {
            "3b27d0f8-3801-4319-398f-ace18829d150": {
                "Date": "2016-02-17",
                "In": "10:45",
                "Name": "Test",
                "Out": "13:30",
                "User ID": "889870966",
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

    def test_search_entries(self):
        """Find all entries that contain a matching piece of data."""
        self.t.sheet = self.example_sheet
        indices = self.t.search_entries("10:45")
        expected_indices = {
            "1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2",
            "2ed2be60-693a-44fe-adc1-2803a674ec9b"
        }
        self.assertEqual(indices, expected_indices)

    def test_load_sheet(self):
        """Load a sheet from a file."""
        self.t.load_sheet(data_file=self.example_file)
        loaded_sheet = self.t.sheet
        self.assertEqual(loaded_sheet, self.example_sheet)

    def test_load_invalid_sheet(self):
        """Load an invalid json file. Make sure it gets
        renamed a with a '.bak' suffix.
        """
        invalid_file = pathlib.Path('.', 'tests', 'invalid.json')
        backup = invalid_file.with_suffix('.bak')
        with invalid_file.open('w') as f:
            f.write("invalid file contents")
        self.t.load_sheet(data_file=invalid_file)
        self.assertTrue(backup.is_file())
        self.assertFalse(invalid_file.is_file())
        backup.unlink()

    def test_save_sheet(self):
        """Save a sheet to a file."""
        self.t.sheet = dict(self.example_sheet)
        self.t.save_sheet(data_file=self.test_file)
        self.assertTrue(
            filecmp.cmp(
                str(self.test_file),
                str(self.example_file)
            )
        )
        self.test_file.unlink()


if __name__ == '__main__':
    unittest.main(warnings='ignore')
