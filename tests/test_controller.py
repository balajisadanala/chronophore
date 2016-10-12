from datetime import date, time
from chronophore import controller
from chronophore.models import Entry


def test_signed_in_names(db_session):
    """List all signed in user names."""
    expected = ['Pippin Took', 'Merry Brandybuck']
    assert set(controller.signed_in_names(db_session)) == set(expected)


def test_signed_in_first_names(db_session):
    """List all signed in user first names."""
    expected = ['Pippin', 'Merry']
    assert (
        set(controller.signed_in_names(db_session, full_name=False))
        == set(expected)
    )


def test_sign_starting(db_session):
    """Frodo, who is registered, signs in."""
    frodo_id = '888000000'
    status = controller.sign(frodo_id, db_session)

    assert status == 'Signed in: Frodo Baggins'
    assert (
        db_session.query(Entry).filter(
                Entry.user_id == frodo_id).filter(
                Entry.time_out.is_(None)).one()
    )


def test_sign_finishing(db_session):
    """Merry is done. He signs out."""
    merry_id = '888222222'
    status = controller.sign(merry_id, db_session)

    assert status == 'Signed out: Merry Brandybuck'
    assert (
        db_session.query(Entry).filter(
                Entry.user_id == merry_id).filter(
                Entry.time_out.is_(None)).one_or_none()
    ) is None


def test_sign_not_registered(db_session):
    """Someone tries to sign in with an unregistered
    ID. They are told to register at the front desk.
    The entry is not added to the database.
    """
    unregistered_id = '000000000'
    status = controller.sign(unregistered_id, db_session)

    expected = '{} not registered. Please register at the front desk'.format(
        unregistered_id
    )
    assert status == expected
    assert (
        db_session.query(Entry).filter(
                Entry.user_id == unregistered_id).one_or_none()
    ) is None


def test_sign_duplicates(db_session):
    """Somehow, Sam has 2 signed in entries in the
    database. When he tries to sign in, a message is
    displayed and the duplicate entries are all signed
    out.
    """
    sam_id = '888111111'
    db_session.add_all([
        Entry(
            uuid='781d8a2a-104b-480c-baba-98c55f11e80b',
            date=date(2016, 1, 10),
            time_in=time(10, 25, 7),
            time_out=None,
            user_id=sam_id
        ),
        Entry(
            uuid='621d98db-92e0-46d1-9cd5-55013777a7d9',
            date=date(2016, 1, 11),
            time_in=time(13, 55, 00),
            time_out=None,
            user_id=sam_id
        ),
    ])
    status = controller.sign(sam_id, db_session)

    expected = 'Signing out of multiple instances of user Sam Gamgee'
    assert status == expected
    assert (
        db_session.query(Entry).filter(
                Entry.user_id == sam_id).filter(
                Entry.time_out.is_(None)).one_or_none()
    ) is None


def test_auto_sign_out(db_session):
    """Frodo and sam forgot to sign out yesterday. Their
    entries are signed out and flagged automatically.
    """
    frodo_id = '888000000'
    sam_id = '888111111'
    today = date(2016, 2, 17)
    yesterday = date(2016, 2, 16)

    db_session.add_all([
        Entry(
            uuid='f0030733-b216-430b-be34-79fa26cbf87d',
            date=yesterday,
            forgot_sign_out=False,
            time_in=time(14, 5, 2),
            time_out=None,
            user_id=frodo_id,
        ),
        Entry(
            uuid='ffac853d-12ac-4a85-8b6f-7c9793479633',
            date=yesterday,
            forgot_sign_out=False,
            time_in=time(10, 45, 3),
            time_out=None,
            user_id=sam_id,
        ),
    ])
    db_session.commit()

    controller.auto_sign_out(db_session, today)

    flagged = db_session.query(Entry).filter(Entry.date == yesterday)
    for entry in flagged:
        assert entry.time_out == time(0, 0)
        assert entry.forgot_sign_out is True


def test_get_user_name(db_session):
    """Look up Sam's name from his ID."""
    sam_id = '888111111'
    name = controller.get_user_name(sam_id, db_session)
    assert name == 'Sam Gamgee'


def test_get_user_first_name(db_session):
    """Look up Sam's first name from his ID."""
    sam_id = '888111111'
    name = controller.get_user_name(sam_id, db_session, full_name=False)
    assert name == 'Sam'


def test_get_multi_word_user_name(db_session):
    """Get Gandalf's full name, which has more than
    just 2 words.
    """
    gandalf_id = '888444444'
    name = controller.get_user_name(gandalf_id, db_session)
    assert name == 'Gandalf the Grey'


def test_no_user_name(db_session):
    """Try to look up the name associated an
    unregistered ID. Return None.
    """
    unregistered_id = '000000000'
    name = controller.get_user_name(unregistered_id, db_session)
    assert name is None
