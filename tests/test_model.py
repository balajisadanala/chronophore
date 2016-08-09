import collections
import filecmp
import json
import logging
import pathlib
import pytest
from datetime import datetime
from timebook.model import Entry, Timesheet

logging.disable(logging.CRITICAL)


@pytest.fixture()
def timesheet(request):
    test_file = pathlib.Path('.', 'tests', 'test.json')

    def tearDown():
        if test_file.exists():
            test_file.unlink()
    request.addfinalizer(tearDown)
    return Timesheet(data_file=test_file)


class TestEntry:

    def test_create_entry(self):
        """Create an entry with an ID."""
        e = Entry(
            user_id="882369423",
            now=datetime(2016, 5, 9, 15, 43, 41, 0)
        )
        assert e.date == "2016-05-09"
        assert e.time_in == "15:43:41"
        assert e.time_out == ""
        assert e.index is not None

    def test_repr(self):
        """Test whether the repr of an Entry evaluates to an
        equivalent Entry object.
        """
        e = Entry()
        assert e == eval(repr(e))

    def test_comparison(self):
        """Test whether '==' and '!=' work properly."""
        entry = Entry(
            user_id="889870966",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30",
            index="1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2"
        )
        equal_entry = entry
        assert entry == equal_entry
        assert equal_entry == entry
        assert (entry != equal_entry) is False
        assert (equal_entry != entry) is False

    def test_sign_out(self):
        """Create an entry, then sign out of it."""
        e = Entry(user_id="882369423")
        e.sign_out(time=datetime(2016, 5, 9, 17, 30, 17, 0))
        assert e.time_out == "17:30:17"


class TestTimesheet:

    example_file = pathlib.Path('.', 'tests', 'example.json')
    with example_file.open() as f:
        example_sheet = json.load(f, object_pairs_hook=collections.OrderedDict)

    def test_find_signed_in(self, timesheet):
        """Find all entries of people that are currently signed in
        (all entries that have a time_in value, but not a time_out value).
        """
        timesheet.sheet = self.example_sheet
        timesheet._update_signed_in()
        expected_entries = ["2ed2be60-693a-44fe-adc1-2803a674ec9b"]
        assert timesheet.signed_in == expected_entries

    def test_add_signed_in(self, timesheet):
        """User signs in, and they are added to the list of currently
        signed in users.
        """
        e = Entry(
            user_id="889870966",
            date="2016-02-17",
            time_in="10:45"
        )
        timesheet.save_entry(e)
        assert e.index in timesheet.signed_in

    def test_remove_signed_in(self, timesheet):
        """User signs out, and they are removed from the list of currently
        signed in users.
        """
        timesheet.sheet = dict(self.example_sheet)
        e = Entry(
            user_id="889870966",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30"
        )
        timesheet.save_entry(e)
        assert e.index not in timesheet.signed_in

    def test_load_entry(self, timesheet):
        """Initialize an entry object with data from the timesheet."""
        timesheet.sheet = self.example_sheet
        entry = timesheet.load_entry("1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2")
        expected_entry = Entry(
            user_id="889870966",
            name="Test",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30",
            index="1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2"
        )
        assert entry == expected_entry

    def test_save_entry(self, timesheet):
        """Add an entry to an empty timesheet."""
        e = Entry(
            user_id="889870966",
            name="Test",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30",
            index="3b27d0f8-3801-4319-398f-ace18829d150"
        )
        timesheet.save_entry(e)
        expected_sheet = {
            "3b27d0f8-3801-4319-398f-ace18829d150": {
                "Date": "2016-02-17",
                "In": "10:45",
                "Name": "Test",
                "Out": "13:30",
                "User ID": "889870966",
            },
        }
        assert timesheet.sheet == expected_sheet

    def test_remove_entry(self, timesheet):
        """Remove an entry from a timesheet with multiple entries."""
        index = "1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2"
        # dicts are mutable; passed by reference unless explicitly copied:
        timesheet.sheet = dict(self.example_sheet)
        timesheet.remove_entry(index)
        assert index not in timesheet.sheet

    def test_search_entries(self, timesheet):
        """Find all entries that contain a matching piece of data."""
        timesheet.sheet = self.example_sheet
        indices = timesheet.search_entries("10:45")
        expected_indices = {
            "1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2",
            "2ed2be60-693a-44fe-adc1-2803a674ec9b"
        }
        assert indices == expected_indices

    def test_load_sheet(self, timesheet):
        """Load a sheet from a file."""
        timesheet.load_sheet(data_file=self.example_file)
        loaded_sheet = timesheet.sheet
        assert loaded_sheet == self.example_sheet

    def test_load_invalid_sheet(self, timesheet):
        """Load an invalid json file. Make sure it gets
        renamed a with a '.bak' suffix.
        """
        invalid_file = pathlib.Path('.', 'tests', 'invalid.json')
        backup = invalid_file.with_suffix('.bak')
        with invalid_file.open('w') as f:
            f.write("invalid file contents")
        timesheet.load_sheet(data_file=invalid_file)
        assert backup.is_file()
        assert (invalid_file.is_file()) is False
        backup.unlink()

    def test_save_sheet(self, timesheet):
        """Save a sheet to a file."""
        timesheet.sheet = self.example_sheet
        timesheet.save_sheet()
        assert filecmp.cmp(str(timesheet.data_file), str(self.example_file))
