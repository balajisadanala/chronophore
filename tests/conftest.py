import logging
import pathlib
import pytest

from chronophore.model import Timesheet

logging.disable(logging.CRITICAL)

DATA_DIR = pathlib.Path(__file__).resolve().parent / 'data'


@pytest.fixture()
def timesheet(request):
    """Return a Timesheet object initialized with a
    fresh data file and the example users file. Remove
    the data file when a test is finished with it.
    """
    test_data = DATA_DIR.joinpath('test.json')
    example_users = DATA_DIR.joinpath('users.json')
    if test_data.exists():
        test_data.unlink()

    def tearDown():
        if test_data.exists():
            test_data.unlink()

    request.addfinalizer(tearDown)
    return Timesheet(data_file=test_data, users_file=example_users)


@pytest.fixture()
def nonexistent_file(request):
    """Return a path to an empty config file.
    Remove the file when a test is finished with it.
    """
    nonexistent = DATA_DIR.joinpath('nonexistent')
    if nonexistent.exists():
        nonexistent.unlink()

    def tearDown():
        if nonexistent.exists():
            nonexistent.unlink()

    request.addfinalizer(tearDown)
    return nonexistent


@pytest.fixture()
def invalid_file(request):
    """Return a path to an invalid file.The file's
    contents make it invalid as either a json or a
    config.ini.
    Remove the file when a test is finished with it.
    """
    invalid_file = DATA_DIR.joinpath('invalid')
    with invalid_file.open('w') as f:
        f.write('this is invalid')

    def tearDown():
        if invalid_file.exists():
            invalid_file.unlink()

    request.addfinalizer(tearDown)
    return invalid_file
