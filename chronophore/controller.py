import logging
import uuid
from datetime import date, datetime, time

from chronophore import Session
from chronophore.models import Entry, User

logger = logging.getLogger(__name__)


class AmbiguousUserType(Exception):
    """This exception is raised when a user
    with multiple user types tries to sign in.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def auto_sign_out(session, today=None):
    """Check for any entries from previous days
    where users forgot to sign out on previous days.
    Sign out and flag those entries.
    """
    today = date.today() if today is None else today

    logger.info('Signing out and flagging forgotten entries.')

    stale = session.query(Entry).filter(
            Entry.time_out.is_(None)).filter(
            Entry.date < today)

    # TODO(amin): replace time.min with a configurable value
    for entry in stale:
        e = sign_out(entry, time_out=time.min, forgot=True)
        logger.debug('Signing out forgotten entry: {}'.format(e))
        session.add(e)

    session.commit()


def signed_in_users(session=None, full_name=True):
    """Return list of names of currently signed in users.
    Full names by default.
    """
    if session is None:
        session = Session()
    else:
        session = session

    signed_in_users = session.query(User).filter(
            User.user_id == Entry.user_id).filter(
            Entry.time_out.is_(None)).all()

    session.close()
    return signed_in_users


def get_user_name(user, full_name=True):
    """Return the user's name as a string.
    Full names by default.
    """
    try:
        if full_name:
            name = ' '.join([user.first_name, user.last_name])
        else:
            name = user.first_name
    except AttributeError:
        name = None

    return name


def sign_in(user, user_type=None, date=None, time_in=None):
    """Add a new entry to the timesheet."""
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

    return new_entry


def sign_out(entry, time_out=None, forgot=False):
    """Sign out of an existing entry in the timesheet.
    If the user forgot to sign out, flag the entry.
    """
    if time_out is None:
        time_out = datetime.today().time()

    entry.time_out = time_out

    if forgot:
        entry.forgot_sign_out = True
        logger.info('{} forgot to sign out.'.format(entry.user_id))

    return entry


def sign(user_id, user_type=None, session=None):
    """Check user id for validity, then sign user in or out
    depending on whether or not they are currently signed in.

    Return:
        - status: A string reporting the result of the sign
        attempt.
    """
    if session is None:
        session = Session()
    else:
        session = session

    user = session.query(User).filter(User.user_id == user_id).one_or_none()

    if user:
        signed_in_entries = user.entries.filter(Entry.time_out.is_(None)).all()

        if not signed_in_entries:
            new_entry = sign_in(user, user_type=user_type)
            session.add(new_entry)
            status = 'Signed in: {}'.format(
                get_user_name(user, session), repr(new_entry)
            )

        else:
            for entry in signed_in_entries:
                signed_out_entry = sign_out(entry)
                session.add(signed_out_entry)
                status = 'Signed out: {}'.format(
                    get_user_name(user, session), repr(signed_out_entry)
                )

        session.commit()
        logger.debug('Commit to database.')

    else:
        status = '{} not registered. Please register at the front desk'.format(
            user_id
        )

    return status
