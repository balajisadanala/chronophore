import collections
import json
import logging
import pathlib
from timebook.model import Entry

logger = logging.getLogger(__name__)


class Controller():
    class DuplicateEntryError(Exception):
        pass

    class DuplicateKeysError(Exception):
        pass

    class NotRegisteredError(Exception):
        pass

    def __init__(self, users_file=None):
        if users_file is None:
            users_file = pathlib.Path('.', 'data', 'users.json')

        self.users_file = users_file

        try:
            self._detect_duplicates(self.users_file)
        except json.decoder.JSONDecodeError as e:
            logger.critical("Invalid users file: {}.".format(e))
            raise SystemExit
        except self.DuplicateKeysError as e:
            logger.error(e)

        logger.debug("Controller object initialized")

    def _detect_duplicates(self, json_file):
        """Raise exception if json_file contains multiple identical keys."""
        with json_file.open('r') as f:
            d = json.load(f, object_pairs_hook=list)

        keys = [key_value_pair[0] for key_value_pair in d]

        duplicate_keys = [
            key for key, count
            in collections.Counter(keys).items()
            if count > 1
        ]

        if len(duplicate_keys) != 0:
            raise self.DuplicateKeysError(
                "Duplicate key(s): {} in json file: {}".format(
                    duplicate_keys, json_file
                )
            )

    def _get_name(self, user_id):
        with self.users_file.open('r') as f:
            user_data = json.load(f)

        name = user_data[user_id]['First Name']
        return name

    @staticmethod
    def is_valid(user_id):
        user_id = user_id.strip()

        try:
            int(user_id)
        except ValueError:
            return False
        else:
            return bool(len(user_id) == 9)

    def is_registered(self, user_id):
        user_id = user_id.strip()
        with self.users_file.open('r') as f:
            registered_ids = list(json.load(f).keys())
        return bool(user_id in registered_ids)

    def sign(self, timesheet, user_id):
        user_id = user_id.strip()

        if not self.is_valid(user_id):
            logger.debug("Invalid input: {}".format(user_id))
            raise ValueError(
                "Invalid Input: {}".format(user_id)
            )

        elif not self.is_registered(user_id):
            logger.debug("User not registered: {}".format(user_id))
            raise self.NotRegisteredError(
                "{} not registered. Please register at the front desk.".format(
                    user_id
                )
            )

        try:
            [entry] = (
                [
                    i for i in timesheet.signed_in
                    if timesheet.sheet[i]['User ID'] == user_id
                ]
                or [None]
            )

        except ValueError:
            # handle duplicates
            duplicate_entries = [
                i for i in timesheet.signed_in
                if timesheet.sheet[i]['User ID'] == user_id
            ]
            logger.warning(
                "Multiple signed in instances of user {}: {}".format(
                    user_id, duplicate_entries
                )
            )
            logger.info(
                "Signing out of duplicate instances of user {}: {}".format(
                    user_id, duplicate_entries
                )
            )
            for entry in duplicate_entries:
                e = timesheet.load_entry(entry)
                e.sign_out()
                timesheet.save_entry(e)

            raise self.DuplicateEntryError(
                "Signing out of duplicate instances of user {}".format(
                    user_id
                )
            )

        else:
            # sign in or out
            if not entry:
                timesheet.save_entry(
                    Entry(
                        user_id=user_id,
                        name=self._get_name(user_id)
                    )
                )
            else:
                e = timesheet.load_entry(entry)
                e.sign_out()
                timesheet.save_entry(e)
        finally:
            timesheet.save_sheet()
