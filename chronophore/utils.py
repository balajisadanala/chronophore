import collections
import json
import logging
import uuid

from chronophore import compat

logger = logging.getLogger(__name__)


def validate_json(json_file):
    """Raise exception if json_file contains errors or key collisions."""
    try:
        with json_file.open('r') as f:
            d = json.load(f, object_pairs_hook=list)
    except compat.InvalidJSONError as e:
        logger.critical("Invalid json file {}: {}.".format(json_file, e))
        raise
    else:
        keys = [key for key, value in d]

        key_collisions = [
            key for key, count
            in collections.Counter(keys).items()
            if count > 1
        ]

        if key_collisions:
            message = "Key collision(s): {} in json file: {}".format(
                key_collisions, json_file
            )
            logger.warning(message)
            raise ValueError(message)
        else:
            logger.debug("{} validated".format(json_file))


def get_users(users_file):
    try:
        validate_json(users_file)
    except FileNotFoundError as e:
        logger.warning(e)
        logger.info('Creating example users file.')
        users = {
            "876543210": {
                "Date Joined": "2015-02-16",
                "Date Left": None,
                "Education Plan": False,
                "Email": "Jensen.Hildegard@live.com",
                "First Name": "Hildegard",
                "Forgot to sign in": True,
                "Last Name": "Jensen",
                "Major": "Computer Science"
            },
            "880000000": {
                "Date Joined": "2013-01-20",
                "Date Left": "2014-05-17",
                "Education Plan": False,
                "Email": "Cyr.Carrie@hotmail.com",
                "First Name": "Carrie",
                "Forgot to sign in": True,
                "Last Name": "Cyr",
                "Major": "Mathematics"
            }
        }
        with users_file.open('w') as f:
            json.dump(users, f, indent=4, sort_keys=True)

    with users_file.open('r') as f:
        users = json.load(f)

    return users


def user_name(user_id, users):
    return (users[user_id]['First Name'], users[user_id]['Last Name'])


def is_valid(user_id, valid_length):
    try:
        int(user_id)
    except ValueError:
        return False
    else:
        return bool(len(user_id) == valid_length)


def is_registered(user_id, users):
    registered_ids = list(users.keys())
    return bool(user_id in registered_ids)


def new_key():
    """Generate a UUID version 4 (basically random)"""
    return str(uuid.uuid4())
