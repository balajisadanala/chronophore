import logging
from datetime import datetime

from chronophore import model, utils

logger = logging.getLogger(__name__)


def signed_in_names(timesheet):
    """Return list of names of currently signed in users."""
    return [
        tuple(timesheet[k].name.split())
        for k in timesheet.signed_in
    ]


def user_signed_in(user_id, timesheet):
    """Check whether a given user is signed in.

    Return:
        - None if 0 instances of user_id signed in
        - Key if 1 instance of user_id signed in

    Raise:
        - ValueError if >1 instance of user_id signed in
    """
    [key] = (
        [
            k for k in timesheet.signed_in
            if timesheet.sheet[k]['user_id'] == user_id
        ]
        or [None]
    )
    return key


def sign_in(user_id, name, date=None, time_in=None):
    now = datetime.today()
    if date is None:
        date = datetime.strftime(now, "%Y-%m-%d")
    if time_in is None:
        time_in = datetime.strftime(now, "%H:%M:%S")

    signed_in_entry = model.Entry(
        date=date,
        name=name,
        time_in=time_in,
        time_out=None,
        user_id=user_id,
    )

    logger.debug("Entry object initialized: {}".format(repr(signed_in_entry)))
    return signed_in_entry


def sign_out(entry, time_out=None):
    if time_out is None:
        time_out = datetime.strftime(datetime.today(), "%H:%M:%S")

    signed_out_entry = entry._replace(time_out=time_out)

    logger.info("Entry signed out: {}".format(repr(signed_out_entry)))
    return signed_out_entry


def sign(user_id, timesheet, users_file=None):
    """Check user id for validity, then sign user in or out
    depending on whether or not they are currently signed in.

    Return:
        - status: "Signed in", "Signed out"

    Raise:
        - ValueError if user_id is invalid. Include a
        message to be passed to the caller.
    """

    users = utils.get_users(users_file)

    if not utils.is_valid(user_id):
        logger.debug("Invalid input: {}".format(user_id))
        raise ValueError(
            "Invalid Input: {}".format(user_id)
        )

    elif not utils.is_registered(user_id, users):
        logger.debug("User not registered: {}".format(user_id))
        raise ValueError(
            "{} not registered. Please register at the front desk.".format(
                user_id
            )
        )

    try:
        key = user_signed_in(user_id, timesheet)
    except ValueError:
        # handle duplicates
        duplicate_entry_keys = [
            k for k in timesheet.signed_in
            if timesheet.sheet[k]['user_id'] == user_id
        ]
        logger.warning(
            "Multiple signed in instances of user {}: {}".format(
                user_id, duplicate_entry_keys
            )
        )
        logger.info(
            "Signing out of multiple instances of user {}: {}".format(
                user_id, duplicate_entry_keys
            )
        )
        for key in duplicate_entry_keys:
            timesheet[key] = sign_out(timesheet[key])

        raise ValueError(
            "Signing out of multiple instances of user {}".format(
                user_id
            )
        )
    else:
        if not key:
            user_name = ' '.join(
                utils.user_name(user_id, utils.get_users(users_file))
            )
            key = utils.new_key()
            timesheet[key] = sign_in(user_id, user_name)
            status = "Signed in"
        else:
            timesheet[key] = sign_out(timesheet[key])
            status = "Signed out"

        return status
