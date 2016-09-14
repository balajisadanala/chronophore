import logging
import pathlib
import pytest

from chronophore import compat, utils

logging.disable(logging.CRITICAL)


def test_invalid_json():
    invalid_file = pathlib.Path(
        '.', 'tests', 'invalid.json'
    )
    with invalid_file.open('w') as f:
        f.write("asdfasdfasdf")
    with pytest.raises(compat.InvalidJSONError):
        utils.validate_json(invalid_file)
    invalid_file.unlink()


def test_key_collision():
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
    assert not utils.is_valid("12")
    assert not utils.is_valid("1234567890")
    assert not utils.is_valid("1234 56789")
    assert not utils.is_valid("")
    assert not utils.is_valid(" ")
    assert not utils.is_valid("123abc")
    assert not utils.is_valid('\n')
    assert not utils.is_valid(" 123456789")
    assert not utils.is_valid("123456789 ")
    assert utils.is_valid("123456789")


def test_is_registered():
    registered_id = "876543210"
    users_file = pathlib.Path('.', 'tests', 'users.json')
    users = utils.get_users(users_file)
    assert not utils.is_registered("888888888", users)
    assert utils.is_registered(registered_id, users)
