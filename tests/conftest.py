import logging
import pathlib
import pytest
from datetime import date, time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from chronophore.models import Base, Entry, User

logging.disable(logging.CRITICAL)


@pytest.fixture()
def nonexistent_file(tmpdir, request):
    """Return a path to an empty config file.
    Remove the file when a test is finished with it.
    """
    data_dir = pathlib.Path(str(tmpdir))
    nonexistent = data_dir.joinpath('nonexistent')
    if nonexistent.exists():
        nonexistent.unlink()

    def tearDown():
        if nonexistent.exists():
            nonexistent.unlink()

    request.addfinalizer(tearDown)
    return nonexistent


@pytest.fixture()
def invalid_file(tmpdir, request):
    """Return a path to an invalid config file.
    Remove the file when a test is finished with it.
    """
    data_dir = pathlib.Path(str(tmpdir))
    invalid_file = data_dir.joinpath('invalid')
    with invalid_file.open('w') as f:
        f.write('this is invalid')

    def tearDown():
        if invalid_file.exists():
            invalid_file.unlink()

    request.addfinalizer(tearDown)
    return invalid_file


@pytest.fixture()
def db_session(request):
    """Create an in-memory sqlite database, add
    some test users and entries, and return an
    sqlalchemy session to it.
    Close the session when the test is finished with it.
    """
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    session = Session()

    add_test_users(session)
    add_test_entries(session)

    def tearDown():
        session.close()

    request.addfinalizer(tearDown)
    return session


def add_test_users(session):
    session.add_all([
        User(
            user_id='888000000',
            date_joined=date(2014, 12, 11),
            date_left=None,
            education_plan=False,
            email='baggins.frodo@gmail.com',
            first_name='Frodo',
            last_name='Baggins',
            major='Medicine',
            user_type='Tutor',
        ),
        User(
            user_id='888111111',
            date_joined=date(2015, 2, 16),
            date_left=None,
            education_plan=True,
            email='gamgee.samwise@gmail.com',
            first_name='Sam',
            last_name='Gamgee',
            major='Agriculture',
            user_type='Student',
        ),
        User(
            user_id='888222222',
            date_joined=date(2015, 4, 12),
            date_left=date(2016, 3, 24),
            education_plan=True,
            email='brandybuck.merriadoc@gmail.com',
            first_name='Merry',
            last_name='Brandybuck',
            major='Physics',
            user_type='Tutor',
        ),
        User(
            user_id='888333333',
            date_joined=date(2015, 2, 16),
            date_left=None,
            education_plan=False,
            email='took.peregrin@gmail.com',
            first_name='Pippin',
            last_name='Took',
            major='Botany',
            user_type='Student',
        ),
        User(
            user_id='888444444',
            date_joined=date(2010, 10, 10),
            date_left=None,
            education_plan=False,
            email='mithrandir@gmail.com',
            first_name='Gandalf',
            last_name='the Grey',
            major='Computer Science',
            user_type='Tutor',
        ),
    ])
    session.commit()


def add_test_entries(session):
    session.add_all([
        Entry(
            uuid='4407d790-a05f-45cb-bcd5-6023ce9500bf',
            date=date(2016, 2, 17),
            time_in=time(10, 45, 23),
            time_out=None,
            user_id='888333333'
        ),
        Entry(
            uuid='1f4f10a4-b0c6-43bf-94f4-9ce6e3e204d2',
            date=date(2016, 2, 17),
            time_in=time(10, 45, 48),
            time_out=time(13, 30, 18),
            user_id='888222222'
        ),
        Entry(
            uuid='7b4ae0fc-3801-4412-998f-ace14829d150',
            date=date(2016, 2, 17),
            time_in=time(12, 45, 9),
            time_out=time(16, 44, 56),
            user_id='888111111'
        ),
        Entry(
            uuid='42a1eab2-cb94-4d05-9bab-e1a021f7f949',
            date=date(2016, 2, 17),
            time_in=time(10, 45, 48),
            time_out=None,
            user_id='888222222'
        ),
    ])
    session.commit()
