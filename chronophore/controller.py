# TODO(amin): auto sign out and flag
import logging
import sqlalchemy
import uuid
from datetime import datetime

from chronophore.models import Entry, Session, User

logger = logging.getLogger(__name__)


def signed_in_names(session=None, full_name=True):
    """Return list of names of currently signed in users.
    Full names by default.
    """
    if session is None:
        session = Session()
    else:
        session = session

    signed_in_users = session.query(User.user_id).filter(
                User.user_id == Entry.user_id).filter(
                Entry.time_out.is_(None))

    names = [
        get_user_name(user_id, session, full_name=full_name)
        for (user_id, ) in signed_in_users
    ]
    session.close()
    return names


def get_user_name(user_id, session, full_name=True):
    """Given a user_id, return the user's name as
    a string, or None if there is no such user.
    Full names by default.
    """
    name = None

    user_name = session.query(User.first_name, User.last_name).filter(
            User.user_id == user_id).one_or_none()

    if user_name:
        first, last = user_name
        if full_name:
            name = ' '.join([first, last])
        else:
            name = first

    return name


def sign_in(user_id, session, date=None, time_in=None):
    """Add a new entry to the timesheet."""
    now = datetime.today()
    if date is None:
        date = datetime.strftime(now, "%Y-%m-%d")
    if time_in is None:
        time_in = datetime.strftime(now, "%H:%M:%S")

    new_entry = Entry(
        uuid=str(uuid.uuid4()),
        date=date,
        time_in=time_in,
        time_out=None,
        user_id=user_id,
    )

    session.add(new_entry)
    logger.debug("Signed in: {}".format(repr(new_entry)))


def sign_out(entry, session, time_out=None):
    """Sign out of an existing entry in the timesheet."""
    if time_out is None:
        time_out = datetime.strftime(datetime.today(), "%H:%M:%S")

    entry.time_out = time_out

    session.add(entry)
    logger.info("Signed out: {}".format(repr(entry)))


def sign(user_id, session=None):
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

    user_name = get_user_name(user_id, session)
    if user_name:
        try:
            entry = session.query(Entry).filter(
                    Entry.user_id == user_id).filter(
                    Entry.time_out.is_(None)).one()

        except sqlalchemy.orm.exc.NoResultFound:
            sign_in(user_id, session)
            status = 'Signed in: {}'.format(user_name)

        except sqlalchemy.orm.exc.MultipleResultsFound:
            duplicates = session.query(Entry).filter(
                    Entry.user_id == user_id).filter(
                    Entry.time_out.is_(None)).all()
            for entry in duplicates:
                sign_out(entry, session)
            status = 'Signing out of multiple instances of user {}'.format(
                user_name
            )

        else:
            sign_out(entry, session)
            status = 'Signed out: {}'.format(user_name)

        finally:
            session.commit()
            logger.debug('Database written to.')
    else:
        status = '{} not registered. Please register at the front desk'.format(
            user_id
        )

    return status
