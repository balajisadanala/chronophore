import collections
import json
import logging
from timebook import config

logger = logging.getLogger(__name__)


def validate_json(json_file):
    """Raise exception if json_file contains errors or key collisions."""
    try:
        with json_file.open('r') as f:
            d = json.load(f, object_pairs_hook=list)
    except json.decoder.JSONDecodeError as e:
        logger.critical("Invalid json file: {}.".format(e))
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


def get_users(users_file):
    validate_json(users_file)
    with users_file.open('r') as f:
        users = json.load(f)
    return users


def user_name(user_id, users):
    return (users[user_id]['First Name'], users[user_id]['Last Name'])


def is_valid(user_id):
    try:
        int(user_id)
    except ValueError:
        return False
    else:
        return bool(len(user_id) == config.USER_ID_LENGTH)


def is_registered(user_id, users):
    registered_ids = list(users.keys())
    return bool(user_id in registered_ids)
