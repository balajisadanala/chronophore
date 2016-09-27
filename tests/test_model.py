import collections
import filecmp
import json
import logging
import pathlib
import pytest

from chronophore.model import Entry, Timesheet

logging.disable(logging.CRITICAL)


@pytest.fixture()
def timesheet(request):
    test_data = pathlib.Path('.', 'tests', 'test.json')
    test_users = pathlib.Path('.', 'tests', 'test_users.json')

    def tearDown():
        if test_data.exists():
            test_data.unlink()

    request.addfinalizer(tearDown)
    return Timesheet(data_file=test_data, users_file=test_users)


class TestTimesheet:

    example_file = pathlib.Path('.', 'tests', 'example.json')
    with example_file.open() as f:
        example_sheet = json.load(f, object_pairs_hook=collections.OrderedDict)

    def test_getitem(self, timesheet):
        timesheet.sheet = self.example_sheet
        key = "2ed2be60-693a-44fe-adc1-2803a674ec9b"
        assert timesheet[key] == Entry(
            date="2016-02-17",
            name="Pippin Took",
            time_in="10:45",
            time_out=None,
            user_id="885894966"
        )

    def test_setitem(self, timesheet):
        e = Entry(
            date="2016-02-17",
            name="Frodo Baggins",
            time_in="10:45",
            time_out=None,
            user_id="889870966",
        )
        timesheet["test_key"] = e
        assert timesheet.sheet["test_key"] == e._asdict()

    def test_contains(self, timesheet):
        timesheet.sheet = self.example_sheet
        assert "2ed2be60-693a-44fe-adc1-2803a674ec9b" in timesheet
        assert "i don't exist" not in timesheet

    def test_len(self, timesheet):
        timesheet.sheet = self.example_sheet
        assert len(timesheet) == 3

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
        key = "012345"
        e = Entry(
            date="2016-02-17",
            name="Frodo Baggins",
            time_in="10:45",
            time_out=None,
            user_id="889870966",
        )
        timesheet[key] = e
        assert key in timesheet.signed_in

    def test_remove_signed_in(self, timesheet):
        """User signs out, and they are removed from the list of currently
        signed in users.
        """
        timesheet.sheet = dict(self.example_sheet)
        key = "012345"
        e = Entry(
            date="2016-02-17",
            name="Frodo Baggins",
            time_in="10:45",
            time_out="13:30",
            user_id="889870966",
        )
        timesheet[key] = e
        assert key not in timesheet.signed_in

    def test_load_entry(self, timesheet):
        """Initialize an entry object with data from the timesheet."""
        timesheet.sheet = self.example_sheet
        entry = timesheet["1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2"]
        expected_entry = Entry(
            user_id="889870966",
            name="Merry Brandybuck",
            date="2016-02-17",
            time_in="10:45",
            time_out="13:30",
        )
        assert entry == expected_entry

    def test_save_entry(self, timesheet):
        """Add an entry to an empty timesheet."""
        key = "3b27d0f8-3801-4319-398f-ace18829d150"
        e = Entry(
            date="2016-02-17",
            name="Frodo Baggins",
            time_in="10:45",
            time_out="13:30",
            user_id="889870966",
        )
        timesheet[key] = e
        assert timesheet[key] == e

    def test_load_sheet(self, timesheet):
        """Load a sheet from a file."""
        with self.example_file.open() as f:
            timesheet.load_sheet(data=f)
        loaded_sheet = timesheet.sheet
        assert loaded_sheet == self.example_sheet

    def test_load_invalid_sheet(self):
        """Load an invalid json file. Make sure it gets
        renamed a with a '.bak' suffix.
        """
        invalid_file = pathlib.Path('.', 'tests', 'invalid.json')
        backup = invalid_file.with_suffix('.bak')
        with invalid_file.open('w') as f:
            f.write("invalid file contents")
        Timesheet(
            data_file=invalid_file,
            users_file=pathlib.Path('./tests/test_users.json')
        )
        assert backup.is_file()
        assert not invalid_file.is_file()
        backup.unlink()

    def test_save_sheet(self, timesheet):
        """Save a sheet to a file."""
        timesheet.sheet = self.example_sheet
        timesheet.save_sheet()
        assert filecmp.cmp(str(timesheet.data_file), str(self.example_file))
