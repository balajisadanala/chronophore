import logging
from chronophore import model, utils

logger = logging.getLogger(__name__)


def signed_in_names(timesheet):
    """Return list of names of currently signed in users."""
    return [timesheet.sheet[i]['Name'] for i in timesheet.signed_in]


def user_signed_in(user_id, timesheet):
    """Check whether a given user is signed in.

    Return:
        - None if 0 instances of user_id signed in
        - user_id if 1 instance of user_id signed in

    Raise:
        - ValueError if >1 instance of user_id signed in
    """
    [entry] = (
        [
            i for i in timesheet.signed_in
            if timesheet.sheet[i]['User ID'] == user_id
        ]
        or [None]
    )
    return entry


def sign(user_id, timesheet):
    """Check user id for validity, then sign user in or out
    depending on whether or not they are currently signed in.

    Return:
        - status: "Signed in", "Signed out", or "Error"

    Raise:
        - ValueError if user_id is invalid. Include a
        message to be passed to the caller.
    """
    users = utils.get_users()

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
        entry = user_signed_in(user_id, timesheet)
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
            "Signing out of multiple instances of user {}: {}".format(
                user_id, duplicate_entries
            )
        )
        for entry in duplicate_entries:
            e = timesheet.load_entry(entry)
            e.sign_out()
            timesheet.save_entry(e)

        raise ValueError(
            "Signing out of multiple instances of user {}".format(
                user_id
            )
        )
    else:
        if not entry:
            # sign in
            timesheet.save_entry(
                model.Entry(
                    user_id=user_id,
                    name=utils.user_name(user_id, users)
                )
            )
            status = "Signed in"
        else:
            # sign out
            e = timesheet.load_entry(entry)
            e.sign_out()
            timesheet.save_entry(e)
            status = "Signed out"

        return status
