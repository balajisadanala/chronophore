import pytest
from datetime import date, time
from chronophore import controller
from chronophore.models import Entry

UNREGISTERED_ID = '000000000'


def test_signed_in_users(db_session, test_users):
    """List all signed in users."""
    signed_in_users = [user for user in controller.signed_in_users(db_session)]
    assert [test_users['pippin'], test_users['merry']] == signed_in_users


def test_sign_starting(db_session, test_users):
    """Frodo, who is registered, signs in."""
    status = controller.sign(
        test_users['frodo'].user_id,
        user_type='student',
        session=db_session,
    )
    assert status == 'Signed in: Frodo Baggins'
    assert (
        db_session.query(Entry).filter(
                Entry.user_id == test_users['frodo'].user_id).filter(
                Entry.time_out.is_(None)).one()
    )


def test_sign_finishing(db_session, test_users):
    """Merry is done. He signs out."""
    merry_id = test_users['merry'].user_id

    status = controller.sign(merry_id, session=db_session)

    assert status == 'Signed out: Merry Brandybuck'
    assert (
        db_session.query(Entry).filter(
                Entry.user_id == merry_id).filter(
                Entry.time_out.is_(None)).one_or_none()
    ) is None


def test_sign_not_registered(db_session, test_users):
    """Someone tries to sign in with an unregistered
    ID. They are told to register at the front desk.
    The entry is not added to the database.
    """
    status = controller.sign(UNREGISTERED_ID, session=db_session)

    expected = '{} not registered. Please register at the front desk'.format(
        UNREGISTERED_ID
    )
    assert status == expected
    assert (
        db_session.query(Entry).filter(
                Entry.user_id == UNREGISTERED_ID).one_or_none()
    ) is None


def test_sign_duplicates(db_session, test_users):
    """Somehow, Sam has 2 signed in entries in the
    database. When he tries to sign in, a message is
    displayed and the duplicate entries are all signed
    out.
    """
    sam_id = test_users['sam'].user_id

    db_session.add_all([
        Entry(
            uuid='781d8a2a-104b-480c-baba-98c55f11e80b',
            date=date(2016, 1, 10),
            time_in=time(10, 25, 7),
            time_out=None,
            user_id=sam_id,
            user_type='student',
        ),
        Entry(
            uuid='621d98db-92e0-46d1-9cd5-55013777a7d9',
            date=date(2016, 1, 11),
            time_in=time(13, 55, 00),
            time_out=None,
            user_id=sam_id,
            user_type='student',
        ),
    ])
    db_session.commit()

    status = controller.sign(sam_id, session=db_session)

    assert status == 'Signed out: Sam Gamgee'
    assert (
        db_session.query(Entry).filter(
                Entry.user_id == sam_id).filter(
                Entry.time_out.is_(None)).one_or_none()
    ) is None


def test_auto_sign_out(db_session, test_users):
    """Frodo and sam forgot to sign out yesterday. Their
    entries are signed out and flagged automatically.
    """
    today = date(2016, 2, 17)
    yesterday = date(2016, 2, 16)

    db_session.add_all([
        Entry(
            uuid='f0030733-b216-430b-be34-79fa26cbf87d',
            date=yesterday,
            forgot_sign_out=False,
            time_in=time(14, 5, 2),
            time_out=None,
            user_id=test_users['frodo'].user_id,
            user_type='tutor',
        ),
        Entry(
            uuid='ffac853d-12ac-4a85-8b6f-7c9793479633',
            date=yesterday,
            forgot_sign_out=False,
            time_in=time(10, 45, 3),
            time_out=None,
            user_id=test_users['sam'].user_id,
            user_type='student',
        ),
    ])
    db_session.commit()

    controller.auto_sign_out(db_session, today)

    flagged = db_session.query(Entry).filter(Entry.date == yesterday)
    for entry in flagged:
        assert entry.time_out == time(0, 0)
        assert entry.forgot_sign_out is True


def test_sign_in_student(test_users):
    """Sam, who is just a student, signs in."""
    entry = controller.sign_in(test_users['sam'])
    assert entry.user_type == 'student'


def test_sign_in_tutor(test_users):
    """Gandalf, who is just a tutor, signs in."""
    entry = controller.sign_in(test_users['gandalf'])
    assert entry.user_type == 'tutor'


def test_sign_in_ambiguous(test_users):
    """Frodo, who is both a student and a tutor,
    signs in. An AmbiguousUserType exception is raised
    to be handled by the gui.
    """
    with pytest.raises(controller.AmbiguousUserType):
        controller.sign_in(test_users['frodo'])


def test_get_user_name(test_users):
    """Look up Sam's name."""
    name = controller.get_user_name(test_users['sam'])
    assert name == 'Sam Gamgee'


def test_get_user_first_name(test_users):
    """Look up Sam's first name."""
    name = controller.get_user_name(test_users['sam'], full_name=False)
    assert name == 'Sam'


def test_get_multi_word_user_name(test_users):
    """Get Gandalf's full name, which has more than
    just 2 words.
    """
    name = controller.get_user_name(test_users['gandalf'])
    assert name == 'Gandalf the Grey'
