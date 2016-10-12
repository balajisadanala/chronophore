import logging
from sqlalchemy import event, Boolean, Column, ForeignKey, String
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    """This class defines the schema for the 'users'
    table. Each row of 'users' is an instance of
    User().
    """
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True, unique=True)

    date_joined = Column(String)
    date_left = Column(String, nullable=True)
    education_plan = Column(Boolean)
    email = Column(String, nullable=True)
    first_name = Column(String)
    forgot_sign_out = Column(Boolean)
    last_name = Column(String)
    major = Column(String, nullable=True)
    user_type = Column(String)

    # TODO(amin): use this relationship to simplify controller code
    entries = relationship('Entry', back_populates='user')

    def __repr__(self):
        return (
            'User('
            + 'user_id="{}",'.format(self.user_id)
            + ' date_joined={},'.format(self.date_joined)
            + ' date_left={},'.format(self.date_left)
            + ' education_plan={},'.format(self.education_plan)
            + ' email={},'.format(self.email)
            + ' first_name={},'.format(self.first_name)
            + ' forgot_sign_out={},'.format(self.forgot_sign_out)
            + ' last_name={},'.format(self.last_name)
            + ' major={},'.format(self.major)
            + ' user_type={}'.format(self.user_type)
            + ')'
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Entry(Base):
    """This class defines the schema for the 'timesheet'
    table. Each row of 'timesheet' is an instance of
    Entry().
    """
    __tablename__ = 'timesheet'

    uuid = Column(String, primary_key=True, unique=True)

    date = Column(String)
    time_in = Column(String)
    time_out = Column(String)
    user_id = Column(String, ForeignKey('users.user_id'))

    # TODO(amin): use this relationship to simplify controller code
    user = relationship('User', back_populates='entries')

    def __repr__(self):
        return (
            'Entry('
            + 'uuid={},'.format(self.uuid)
            + ' date={},'.format(self.date)
            + ' time_in={},'.format(self.time_in)
            + ' time_out={},'.format(self.time_out)
            + ' user_id={}'.format(self.user_id)
            + ')'
        )


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Upon every db connection, issue a command
    to ensure foreign key constraints are enforced.

    This is a sqlite-specific issue:
    http://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
    http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#foreign-key-support
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def add_test_users(session):
    """Add two hobbits and a wizard to the
    users table for testing purposes. These
    are not necessarily the same test users
    as in the unit tests.

    This function is idempotent.
    """
    test_users = [
        User(
            user_id='000000000',
            date_joined='2014-12-11',
            date_left=None,
            education_plan=False,
            email='baggins.frodo@gmail.com',
            first_name='Frodo',
            forgot_sign_out=False,
            last_name='Baggins',
            major='Medicine',
            user_type='Tutor',
        ),
        User(
            user_id='000111111',
            date_joined='2015-02-16',
            date_left=None,
            education_plan=True,
            email='gamgee.samwise@gmail.com',
            first_name='Sam',
            forgot_sign_out=False,
            last_name='Gamgee',
            major='Agriculture',
            user_type='Student',
        ),
        User(
            user_id='000222222',
            date_joined='2010-10-10',
            date_left=None,
            education_plan=False,
            email='mithrandir@gmail.com',
            first_name='Gandalf',
            forgot_sign_out=False,
            last_name='the Grey',
            major='Computer Science',
            user_type='Tutor',
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
