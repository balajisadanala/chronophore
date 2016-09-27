import logging
import pathlib
import pytest

from chronophore import compat, utils

logging.disable(logging.CRITICAL)

DATA_DIR = pathlib.Path(__file__).resolve().parent / 'data'
EXAMPLE_USERS = DATA_DIR.joinpath('users.json')

VALID_LENGTH = 9


def test_invalid_json(invalid_file):
    """Raise an exception when a json file is invalid."""
    with pytest.raises(compat.InvalidJSONError):
        utils.validate_json(invalid_file)


def test_key_collision():
    """Detect when a json file has duplicate keys."""
    key_collision_file = pathlib.Path(
        '.', 'tests', 'duplicate_keys.json'
    )
    lines = ["{", '"key":1234,', '"key":5678', "}"]
    with key_collision_file.open('w') as f:
        f.write('\n'.join(lines))
    with pytest.raises(ValueError):
        utils.validate_json(key_collision_file)
    key_collision_file.unlink()


def test_is_valid():
    """Validate various IDs."""
    assert not utils.is_valid("12", VALID_LENGTH)
    assert not utils.is_valid("1234567890", VALID_LENGTH)
    assert not utils.is_valid("1234 56789", VALID_LENGTH)
    assert not utils.is_valid("", VALID_LENGTH)
    assert not utils.is_valid(" ", VALID_LENGTH)
    assert not utils.is_valid("123abc", VALID_LENGTH)
    assert not utils.is_valid('\n', VALID_LENGTH)
    assert not utils.is_valid(" 123456789", VALID_LENGTH)
    assert not utils.is_valid("123456789 ", VALID_LENGTH)
    assert not utils.is_valid("abcdefhij", VALID_LENGTH)
    assert utils.is_valid("123456789", VALID_LENGTH)


def test_is_registered():
    """Users are only registered if their ID is
    in the users file.
    """
    registered_id = "876543210"
    users = utils.get_users(EXAMPLE_USERS)
    assert not utils.is_registered("888888888", users)
    assert utils.is_registered(registered_id, users)


def test_no_users_file(nonexistent_file):
    """Create a default users file when none exists."""
    test_users = nonexistent_file
    users = utils.get_users(test_users)
    assert set(['876543210', '880000000']) == set(users.keys())
    assert test_users.is_file()
