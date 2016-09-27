import pathlib
import pytest

from chronophore import controller, utils
from chronophore.model import Entry, Timesheet

DATA_DIR = pathlib.Path(__file__).resolve().parent / 'data'
EXAMPLE_DATA = DATA_DIR.joinpath('data.json')
EXAMPLE_USERS = DATA_DIR.joinpath('users.json')
REGISTERED_ID = "876543210"


def test_signed_in_names():
    """List all signed in users."""
    timesheet = Timesheet(
        data_file=EXAMPLE_DATA,
        users_file=EXAMPLE_USERS
    )
    expected = [("Pippin", "Took")]
    assert controller.signed_in_names(timesheet) == expected


def test_sign_in():
    """Test that the proper Entry object is returned."""
    signed_in_entry = controller.sign_in(
        "883406720",
        "Frodo Baggins",
        date="2016-08-31",
        time_in="13:08:25",
    )
    expected = Entry(
        date="2016-08-31",
        name="Frodo Baggins",
        time_in="13:08:25",
        time_out=None,
        user_id="883406720",
    )
    assert signed_in_entry == expected


def test_sign_out():
    """Sign out an entry, and verify that the entry's
    time_out value is appropriately updated."""
    e = Entry(
        date="2016-08-31",
        name="Frodo Baggins",
        time_in="13:08:25",
        time_out=None,
        user_id="883406720",
    )
    signed_out_entry = controller.sign_out(e, time_out="13:08:25")
    assert signed_out_entry == e._replace(time_out="13:08:25")


def test_sign_invalid(timesheet):
    """Assert that ValueError is raised when someone
    signs in with an invalid id.
    """
    with pytest.raises(ValueError):
        controller.sign("1234567890", timesheet)


def test_sign_not_registered(timesheet):
    """Assert that ValueError is raised when someone
    signs in with an id that, though valid,  isn't
    in the user file.
    """
    with pytest.raises(ValueError):
        controller.sign("888888888", timesheet)


def test_sign_duplicates(timesheet):
    """Sign in with an id that is already signed in."""
    duplicate_id = REGISTERED_ID
    for _ in range(2):
        e = Entry(
            date="2016-08-31",
            name="Hildegard Jensen",
            time_in="10:00",
            time_out=None,
            user_id=duplicate_id,
        )
        timesheet[utils.new_key()] = e
    with pytest.raises(ValueError):
        controller.sign(duplicate_id, timesheet)


def test_sign_user_in(monkeypatch, timesheet):
    """Sign in with a new ID."""
    # NOTE(amin): remember that time you spent 40 minutes trying to
    # figure out why this test was failing, only to realize with horror
    # that there is a difference between "882870192" and "882870l92"?
    user_id = REGISTERED_ID

    def mock_new_key():
        return '3b27d0f8-3801-4319-398f-ace18829d150'

    monkeypatch.setattr('chronophore.utils.new_key', mock_new_key)
    k = utils.new_key()
    print(k)
    controller.sign(user_id, timesheet)
    assert(
        timesheet['3b27d0f8-3801-4319-398f-ace18829d150'].user_id
        == user_id
    )


def test_sign_user_out(timesheet):
    """Sign out with an ID that's currently signed in."""
    key = "2ed2be60-693a-44fe-adc1-2803a674ec9b"
    e = Entry(
        date="2016-02-17",
        name="Hildegard Jensen",
        time_in="10:45",
        time_out=None,
        user_id=REGISTERED_ID,
    )
    timesheet[key] = e
    controller.sign(REGISTERED_ID, timesheet)
    assert timesheet[key] is not None
    assert key not in timesheet.signed_in
