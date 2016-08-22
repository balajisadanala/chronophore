import logging
from timebook import config, utils
from timebook.model import Entry

logger = logging.getLogger(__name__)


def signed_in_names(timesheet):
    return [timesheet.sheet[i]['Name'] for i in timesheet.signed_in]


def sign(timesheet, user_id):
    """
    parameters:
        - timesheet: timesheet object
        - user_id: string of user's unique login ID.
    returns:
        - status: "Signed in", "Signed out", or "Error"
    """
    users_file = config.USERS_FILE
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
                Entry(
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
        timesheet.save_sheet()
        return status
