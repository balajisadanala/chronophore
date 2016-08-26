import logging
import pathlib
import pytest
from chronophore import controller
from chronophore.model import Entry, Timesheet

logging.disable(logging.CRITICAL)


users_file = pathlib.Path('.', 'tests', 'users.json')
registered_id = "876543210"


@pytest.fixture()
def timesheet(request):
    test_file = pathlib.Path('.', 'tests', 'test.json')

    def tearDown():
        if test_file.exists():
            test_file.unlink()
    request.addfinalizer(tearDown)
    return Timesheet(data_file=test_file)


def test_signed_in_names():
    timesheet = Timesheet(data_file=pathlib.Path('.', 'tests', 'example.json'))
    expected = ["Bork"]
    assert controller.signed_in_names(timesheet) == expected


def test_sign_invalid():
    with pytest.raises(ValueError):
        controller.sign("1234567890", timesheet)


def test_sign_not_registered(timesheet):
    with pytest.raises(ValueError):
        controller.sign("888888888", timesheet)


def test_sign_duplicates(timesheet):
    """Sign in with multiple instances of being signed in."""
    duplicate_id = registered_id
    for _ in range(2):
        e = Entry(duplicate_id)
        timesheet.save_entry(e)
    with pytest.raises(ValueError):
        controller.sign(duplicate_id, timesheet)


def test_sign_in(monkeypatch, timesheet):
    """Sign in with a new ID."""
    # NOTE(amin): remember that time you spent 40 minutes trying to
    # figure out why this test was failing, only to realize with horror
    # that there is a difference between "882870192" and "882870l92"?
    def mock_index(Entry):
        return '3b27d0f8-3801-4319-398f-ace18829d150'
    monkeypatch.setattr(Entry, 'make_index', mock_index)
    user_id = registered_id
    controller.sign(user_id, timesheet)
    assert(
        timesheet.sheet['3b27d0f8-3801-4319-398f-ace18829d150']['User ID']
        == user_id
    )


def test_sign_out(timesheet):
    """Sign out with an ID that's currently signed in."""
    e = Entry(
        user_id=registered_id,
        date="2016-02-17",
        time_in="10:45",
        time_out=None,
        index="2ed2be60-693a-44fe-adc1-2803a674ec9b"
    )
    timesheet.save_entry(e)
    controller.sign(registered_id, timesheet)
    assert timesheet.sheet[e.index] is not None
    assert e.index not in timesheet.signed_in
