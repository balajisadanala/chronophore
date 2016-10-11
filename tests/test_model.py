import logging
import pytest
import sqlalchemy

from chronophore.models import Entry, User

logging.disable(logging.CRITICAL)


class TestEntry:

    def test_foreign_key_constraint(self, db_session):
        """Try to add an entry for a user that
        doesn't exist in the database.
        Assert that IntegrityError is raised.
        """
        unregistered_id = '000000000'
        db_session.add(
            Entry(
                uuid='74ae3943-4dc8-4d84-bc42-826652ca9943',
                date='2016-02-02',
                time_in='10:45:31',
                time_out=None,
                user_id=unregistered_id,
            )
        )
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            db_session.commit()


class TestUser:

    def test_unique_constraint(self, db_session):
        """Try to add a user with the id of another,
        already-registered user.
        Assert that IntegrityError is raised.
        """
        frodo_id = '888000000'
        db_session.add(
            User(
                user_id=frodo_id,
                date_joined='2014-12-12',
                date_left=None,
                education_plan=False,
                email='smeagol@gmail.com',
                first_name='Smeagol',
                forgot_sign_out=False,
                last_name='',
                major='Conservation',
                user_type='Student',
            ),
        )
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            db_session.commit()
