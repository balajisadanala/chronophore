import logging
import pathlib
import pytest
from timebook import controller
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


class TestController:
    users_file = pathlib.Path('.', 'tests', 'users.json')
    registered_id = "876543210"

    def test_sign_invalid(self):
        with pytest.raises(ValueError):
            controller.sign(timesheet, "1234567890")

    def test_sign_not_registered(self, timesheet):
        with pytest.raises(ValueError):
            controller.sign(timesheet, "888888888")

    def test_sign_duplicates(self, timesheet):
        """Sign in with multiple instances of being signed in."""
        duplicate_id = self.registered_id
        for _ in range(2):
            e = Entry(duplicate_id)
            timesheet.save_entry(e)
        with pytest.raises(ValueError):
            controller.sign(timesheet, duplicate_id)

    def test_sign_in(self, monkeypatch, timesheet):
        """Sign in with a new ID."""
        # NOTE(amin): remember that time you spent 40 minutes trying to
        # figure out why this test was failing, only to realize with horror
        # that there is a difference between "882870192" and "882870l92"?
        def mock_index(Entry):
            return '3b27d0f8-3801-4319-398f-ace18829d150'
        monkeypatch.setattr(Entry, 'make_index', mock_index)
        user_id = self.registered_id
        controller.sign(timesheet, user_id)
        assert(
            timesheet.sheet['3b27d0f8-3801-4319-398f-ace18829d150']['User ID']
            == user_id
        )

    def test_sign_out(self, timesheet):
        """Sign out with an ID that's currently signed in."""
        self.e = Entry(
            user_id=self.registered_id,
            date="2016-02-17",
            time_in="10:45",
            time_out=None,
            index="2ed2be60-693a-44fe-adc1-2803a674ec9b"
        )
        timesheet.save_entry(self.e)
        controller.sign(timesheet, self.registered_id)
        assert timesheet.sheet[self.e.index] is not None
        assert self.e.index not in timesheet.signed_in
