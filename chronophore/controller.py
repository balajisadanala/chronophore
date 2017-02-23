import collections
import logging
import uuid
from datetime import date, datetime

from chronophore import Session
from chronophore.models import Entry, User

logger = logging.getLogger(__name__)


class AmbiguousUserType(Exception):
    """This exception is raised when a user with multiple user types
    tries to sign in.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class UnregisteredUser(Exception):
    """This exception is raised when a user id doesn't match any user in
    the database.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message


#: Status is a namedtuple used by the `sign()` function to return relevant
#: information to the gui about a sign-in or sign-out attempt.
#:
#: .. attribute:: valid
#:
#:    Whether or not the user was valid.
#:
#: .. attribute:: in_or_out
#:
#:    Whether the user was signing in or out.
#:
#: .. attribute:: user_name
#:
#:    The name of the user.
#:
#: .. attribute:: user_type
#:
#:    Whether the user was a student or a tutor.
#:
#: .. attribute:: entry
#:
#:    The `chronophore.models.Entry` object signed into or out of.
#:
Status = collections.namedtuple(
    'Status',
    [
        'valid',
        'in_or_out',
        'user_name',
        'user_type',
        'entry',
    ]
)


def flag_forgotten_entries(session, today=None):
    """Flag any entries from previous days where users forgot to sign
    out.

    :param session: SQLAlchemy session through which to access the database.
    :param today: (optional) The current date as a `datetime.date` object. Used for testing.
    """ # noqa
    today = date.today() if today is None else today

    forgotten = session.query(Entry).filter(
            Entry.time_out.is_(None)).filter(
            Entry.forgot_sign_out.is_(False)).filter(
            Entry.date < today)

    for entry in forgotten:
        e = sign_out(entry, forgot=True)
        logger.debug('Signing out forgotten entry: {}'.format(e))
        session.add(e)

    session.commit()


def signed_in_users(session=None, today=None, full_name=True):
    """Return list of names of currently signed in users.

    :param session: SQLAlchemy session through which to access the database.
    :param today: (optional) The current date as a `datetime.date` object. Used for testing.
    :param full_name: (optional) Whether to display full user names, or just first names.
    :return: List of currently signed in users.
    """ # noqa
    if session is None:
        session = Session()
    else:
        session = session

    if today is None:
        today = date.today()
    else:
        today = today

    signed_in_users = session.query(User).filter(
            Entry.date == today).filter(
            Entry.time_out.is_(None)).filter(
            User.user_id == Entry.user_id).all()

    session.close()
    return signed_in_users


def get_user_name(user, full_name=True):
    """Return the user's name as a string.

    :param user: `models.User` object. The user to get the name of.
    :param full_name: (optional) Whether to return full user name, or just first name.
    :return: The user's name.
    """ # noqa
    try:
        if full_name:
            name = ' '.join([user.first_name, user.last_name])
        else:
            name = user.first_name
    except AttributeError:
        name = None

    return name


def sign_in(user, user_type=None, date=None, time_in=None):
    """Add a new entry to the timesheet.

    :param user: `models.User` object. The user to sign in.
    :param user_type: (optional) Specify whether user is signing in as a `'student'` or `'tutor'`.
    :param date: (optional) `datetime.date` object. Specify the entry date.
    :param time_in: (optional) `datetime.time` object. Specify the sign in time.
    :return: The new entry.
    """ # noqa
    now = datetime.today()
    if date is None:
        date = now.date()
    if time_in is None:
        time_in = now.time()
    if user_type is None:
        if user.is_student and user.is_tutor:
            raise AmbiguousUserType('User is both a student and a tutor.')
        elif user.is_student:
            user_type = 'student'
        elif user.is_tutor:
            user_type = 'tutor'
        else:
            raise ValueError('Unknown user type.')

    new_entry = Entry(
        uuid=str(uuid.uuid4()),
        date=date,
        time_in=time_in,
        time_out=None,
        user_id=user.user_id,
        user_type=user_type,
        user=user,
    )

    logger.info('{} ({}) signed in.'.format(new_entry.user_id, new_entry.user_type))
    return new_entry


def sign_out(entry, time_out=None, forgot=False):
    """Sign out of an existing entry in the timesheet. If the user
    forgot to sign out, flag the entry.

    :param entry: `models.Entry` object. The entry to sign out.
    :param time_out: (optional) `datetime.time` object. Specify the sign out time.
    :param forgot: (optional) If true, user forgot to sign out. Entry will be flagged as forgotten.
    :return: The signed out entry.
    """ # noqa
    if time_out is None:
        time_out = datetime.today().time()

    if forgot:
        entry.forgot_sign_out = True
        logger.info(
            '{} forgot to sign out on {}.'.format(entry.user_id, entry.date)
        )

    else:
        entry.time_out = time_out

    logger.info('{} ({}) signed out.'.format(entry.user_id, entry.user_type))
    return entry


def undo_sign_in(entry, session=None):
    """Delete a signed in entry.

    :param entry: `models.Entry` object. The entry to delete.
    :param session: (optional) SQLAlchemy session through which to access the database.
    """ # noqa
    if session is None:
        session = Session()
    else:
        session = session

    entry_to_delete = session.query(Entry).filter(
            Entry.uuid == entry.uuid).one_or_none()

    if entry_to_delete:
        logger.info('Undo sign in: {}'.format(entry_to_delete.user_id))
        logger.debug('Undo sign in: {}'.format(entry_to_delete))
        session.delete(entry_to_delete)
        session.commit()
    else:
        error_message = 'Entry not found: {}'.format(entry)
        logger.error(error_message)
        raise ValueError(error_message)


def undo_sign_out(entry, session=None):
    """Sign in a signed out entry.

    :param entry: `models.Entry` object. The entry to sign back in.
    :param session: (optional) SQLAlchemy session through which to access the database.
    """ # noqa
    if session is None:
        session = Session()
    else:
        session = session

    entry_to_sign_in = session.query(Entry).filter(
            Entry.uuid == entry.uuid).one_or_none()

    if entry_to_sign_in:
        logger.info('Undo sign out: {}'.format(entry_to_sign_in.user_id))
        logger.debug('Undo sign out: {}'.format(entry_to_sign_in))
        entry_to_sign_in.time_out = None
        session.add(entry_to_sign_in)
        session.commit()
    else:
        error_message = 'Entry not found: {}'.format(entry)
        logger.error(error_message)
        raise ValueError(error_message)


def sign(user_id, user_type=None, today=None, session=None):
    """Check user id for validity, then sign user in if they are signed
    out, or out if they are signed in.

    :param user_id: The ID of the user to sign in or out.
    :param user_type: (optional) Specify whether user is signing in as a `'student'` or `'tutor'`.
    :param today: (optional) The current date as a `datetime.date` object. Used for testing.
    :param session: (optional) SQLAlchemy session through which to access the database.
    :return: `Status` named tuple object. Information about the sign attempt.
    """ # noqa
    if session is None:
        session = Session()
    else:
        session = session

    if today is None:
        today = date.today()
    else:
        today = today

    user = session.query(User).filter(User.user_id == user_id).one_or_none()

    if user:
        signed_in_entries = user.entries.filter(
                Entry.date == today).filter(
                Entry.time_out.is_(None)).all()

        if not signed_in_entries:
            new_entry = sign_in(user, user_type=user_type)
            session.add(new_entry)
            status = Status(
                valid=True,
                in_or_out='in',
                user_name=get_user_name(user),
                user_type=new_entry.user_type,
                entry=new_entry
            )

        else:
            for entry in signed_in_entries:
                signed_out_entry = sign_out(entry)
                session.add(signed_out_entry)
                status = Status(
                    valid=True,
                    in_or_out='out',
                    user_name=get_user_name(user),
                    user_type=signed_out_entry.user_type,
                    entry=signed_out_entry
                )

        session.commit()

    else:
        raise UnregisteredUser(
            '{} not registered. Please register at the front desk.'.format(
                user_id
            )
        )

    logger.debug(status)
    return status
