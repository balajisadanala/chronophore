import logging
from datetime import date
from sqlalchemy import event, Boolean, Column, Date, ForeignKey, String
from sqlalchemy.dialects.sqlite import TIME
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

logger = logging.getLogger(__name__)

Base = declarative_base()
SQLite_Time = TIME(storage_format='%(hour)02d:%(minute)02d:%(second)02d')


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Upon every db connection, issue a command to ensure foreign key
    constraints are enforced.

    This is a sqlite-specific issue:
    http://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
    http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#foreign-key-support
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class User(Base):
    """Schema for the 'users' table."""
    __tablename__ = 'users'

    #: The user's unique ID (*Primary Key*).
    user_id = Column(String, primary_key=True, unique=True)

    #: The date on which the user was registered.
    date_joined = Column(Date)

    #: The date on which the user was no longer registered.
    date_left = Column(Date, nullable=True)

    #: `1` if the user has submitted an education plan, `0` otherwise.
    education_plan = Column(Boolean, default=False)

    #: The user's school email.
    school_email = Column(String, nullable=True)

    #: The user's personal email.
    personal_email = Column(String, nullable=True)

    #: The user's first name.
    first_name = Column(String)

    #: The user's last name.
    last_name = Column(String)

    #: The user's declared major.
    major = Column(String, nullable=True)

    #: `1` if the user is a student, `0` otherwise.
    is_student = Column(Boolean, default=True)

    #: `1` if the user is a tutor, `0` otherwise.
    is_tutor = Column(Boolean, default=False)

    entries = relationship('Entry', back_populates='user', lazy='dynamic')

    def __repr__(self):
        return (
            'User('
            + 'user_id={},'.format(self.user_id)
            + ' date_joined={},'.format(self.date_joined)
            + ' date_left={},'.format(self.date_left)
            + ' education_plan={},'.format(self.education_plan)
            + ' school_email={},'.format(self.school_email)
            + ' personal_email={},'.format(self.personal_email)
            + ' first_name={},'.format(self.first_name)
            + ' last_name={},'.format(self.last_name)
            + ' major={},'.format(self.major)
            + ' is_student={},'.format(self.is_student)
            + ' is_tutor={},'.format(self.is_tutor)
            + ')'
        )


class Entry(Base):
    """Schema for the 'timesheet' table."""
    __tablename__ = 'timesheet'

    #: A unique ID for each entry (*Primary Key*).
    uuid = Column(String, primary_key=True, unique=True)

    #: The date the user signed in.
    date = Column(Date)

    #: `1` if the user never signed out, `0` otherwise.
    forgot_sign_out = Column(Boolean, default=False)

    #: Sign in time.
    time_in = Column(SQLite_Time)

    #: Sign out time.
    time_out = Column(SQLite_Time)

    #: The user's unique ID (*Foreign Key*).
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)

    #: Whether the user signed in as a `student` or a `tutor`.
    user_type = Column(String, nullable=False)

    user = relationship('User', back_populates='entries')

    def __repr__(self):
        return (
            'Entry('
            + 'uuid={},'.format(self.uuid)
            + ' date={},'.format(self.date)
            + ' forgot_sign_out={},'.format(self.forgot_sign_out)
            + ' time_in={},'.format(self.time_in)
            + ' time_out={},'.format(self.time_out)
            + ' user_id={},'.format(self.user_id)
            + ' user_type={},'.format(self.user_type)
            + ')'
        )


def add_test_users(session):
    """Add two hobbits and a wizard to the users table for testing
    purposes. These are not necessarily the same test users as in the
    unit tests.

    This function is idempotent.
    """
    test_users = [
        User(
            user_id='000000000',
            date_joined=date(2014, 12, 11),
            date_left=None,
            education_plan=False,
            personal_email='baggins.frodo@gmail.com',
            first_name='Frodo',
            last_name='Baggins',
            major='Medicine',
            is_student=True,
            is_tutor=True,
        ),
        User(
            user_id='000111111',
            date_joined=date(2015, 2, 16),
            date_left=None,
            education_plan=True,
            personal_email='gamgee.samwise@gmail.com',
            first_name='Sam',
            last_name='Gamgee',
            major='Agriculture',
            is_student=True,
            is_tutor=False,
        ),
        User(
            user_id='000222222',
            date_joined=date(2010, 10, 10),
            date_left=None,
            education_plan=False,
            personal_email='mithrandir@gmail.com',
            first_name='Gandalf',
            last_name='the Grey',
            major='Computer Science',
            is_student=False,
            is_tutor=True,
        ),
    ]

    registered_ids = {
        user_id for (user_id, )
        in session.query(User.user_id).all()
    }

    for user in test_users:
        if user.user_id not in registered_ids:
            session.add(user)
            name = ' '.join([user.first_name, user.last_name])
            logger.info(
                'Adding test user: {} ({}).'.format(user.user_id, name)
            )

    session.commit()
