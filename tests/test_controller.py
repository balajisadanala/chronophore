import logging
import pathlib
import unittest
import unittest.mock
from timebook.controller import Controller
from timebook.model import Entry, Timesheet

logging.disable(logging.CRITICAL)


class ControllerTest(unittest.TestCase):
    test_file = pathlib.Path('.', 'tests', 'test.json')
    users_file = pathlib.Path('.', 'tests', 'users.json')
    registered_id = "876543210"
    c = Controller(users_file)

    def setUp(self):
        self.t = Timesheet(data_file=self.test_file)

    def test_detect_duplicates(self):
        duplicate_keys_file = pathlib.Path(
            '.', 'tests', 'duplicate_keys.json'
        )
        lines = ["{", '"key":1234,', '"key":5678', "}"]
        with duplicate_keys_file.open('w') as f:
            f.write('\n'.join(lines))
        with self.assertRaises(self.c.DuplicateKeysError):
            self.c._detect_duplicates(duplicate_keys_file)
        duplicate_keys_file.unlink()

    def test_is_valid(self):
        self.assertFalse(self.c.is_valid("12"))
        self.assertFalse(self.c.is_valid("1234567890"))
        self.assertFalse(self.c.is_valid("1234 56789"))
        self.assertFalse(self.c.is_valid(""))
        self.assertFalse(self.c.is_valid(" "))
        self.assertFalse(self.c.is_valid("123abc"))
        self.assertFalse(self.c.is_valid('\n'))
        self.assertTrue(self.c.is_valid("123456789"))
        self.assertTrue(self.c.is_valid(" 123456789"))
        self.assertTrue(self.c.is_valid("123456789 "))

    def test_is_registered(self):
        self.assertFalse(self.c.is_registered("888888888"))
        self.assertTrue(self.c.is_registered(self.registered_id))

    def test_sign_invalid(self):
        with self.assertRaises(ValueError):
            self.c.sign(self.t, "1234567890")

    def test_sign_not_registered(self):
        with self.assertRaises(self.c.NotRegisteredError):
            self.c.sign(self.t, "888888888")

    def test_sign_duplicates(self):
        """Sign in with multiple instances of being signed in."""
        duplicate_id = self.registered_id
        for _ in range(2):
            e = Entry(duplicate_id)
            self.t.save_entry(e)
        with self.assertRaises(self.c.DuplicateEntryError):
            self.c.sign(self.t, duplicate_id)

    @unittest.mock.patch(
            'timebook.model.Entry.make_index',
            return_value='3b27d0f8-3801-4319-398f-ace18829d150')
    def test_sign_in(self, make_index):
        """Sign in with a new ID."""
        # NOTE(amin): remember that time you spent 40 minutes trying to
        # figure out why this test was failing, only to realize with horror
        # that there is a difference between "882870192" and "882870l92"?
        user_id = self.registered_id
        self.c.sign(self.t, user_id)
        self.assertEqual(
            self.t.sheet['3b27d0f8-3801-4319-398f-ace18829d150']['User ID'],
            user_id
        )

    def test_sign_out(self):
        """Sign out with an ID that's currently signed in."""
        self.e = Entry(
            user_id=self.registered_id,
            date="2016-02-17",
            time_in="10:45",
            time_out=None,
            index="2ed2be60-693a-44fe-adc1-2803a674ec9b"
        )
        self.t.save_entry(self.e)
        self.c.sign(self.t, self.registered_id)
        self.assertIsNotNone(self.t.sheet[self.e.index])
        self.assertNotIn(self.e.index, self.t.signed_in)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
