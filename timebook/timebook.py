import json
import logging
import pathlib
import uuid
from datetime import datetime
from timebook import gui

log = logging.getLogger(__name__)


def setup_logger():
    log.setLevel(logging.DEBUG)

    fh = logging.FileHandler('debug.log')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        "{asctime} {levelname}: {message}", style='{'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)


class Entry():
    """Contains all data for a single entry"""

    def __init__(self, user_id=None, date=None, time_in=None,
                 time_out=None, index=None):
        """Parameters have different default behaviors, and can all be
        overwritten.

        Default Behaviors:
            date, time_in: assigned the current date/time
            user_id, time_out: left as empty strings
            index: assigned a uuid
        """
        now = self._get_current_datetime()
        if date is None:
            self.date = datetime.strftime(now, "%Y-%m-%d")
        else:
            self.date = date
        if user_id is None:
            self.user_id = ""
        else:
            self.user_id = user_id
        if time_in is None:
            self.time_in = datetime.strftime(now, "%H:%M:%S")
        else:
            self.time_in = time_in
        if time_out is None:
            self.time_out = ""
        else:
            self.time_out = time_out
        if index is None:
            self.index = self._make_index()
        else:
            self.index = index
        log.debug("Entry object initialized: {}".format(repr(self)))

    def __repr__(self):
        """Return an unambiguous representation of the entry."""
        entry = ("timebook.Entry(user_id='{}', date='{}', time_in='{}', "
                 "time_out='{}', index='{}')")
        return entry.format(
            self.user_id,
            self.date,
            self.time_in,
            self.time_out,
            self.index
        )

    def __eq__(self, other):
        """'==' returns true if both objects are instances of Entry
        and have identical attributes.
        """
        if isinstance(other, Entry):
            return self.__dict__ == other.__dict__
        return false

    def __ne__(self, other):
        """'!=' returns the opposite of '=='."""
        return not self == other

    def _get_current_datetime(self):
        """Serves as a mockable reference to datetime.today().
        Mocking is used in the unit tests.
        """
        return datetime.today()

    def _make_index(self):
        """Generate a UUID version 4 (basically random)"""
        return str(uuid.uuid4())

    def sign_out(self):
        """Get the time the user signed out"""
        now = self._get_current_datetime()
        self.time_out = datetime.strftime(now, "%H:%M:%S")
        log.info("Entry signed out: {}".format(repr(self)))


class Timesheet():
    """Contains multiple entries"""

    def __init__(self, data_file=None):
        self.sheet = {}
        self.signed_in = []
        data_dir = pathlib.Path('.', 'data')

        if data_file is None:
            today = datetime.strftime(datetime.today(), "%Y-%m-%d")
            file_name = today + ".json"
            self.data_file = data_dir.joinpath(file_name)
        else:
            self.data_file = data_file

        if self.data_file.exists():
            self.load_sheet()
        elif not data_dir.exists():
            # make the data folder
            data_dir.mkdir(exist_ok=False, parents=True)

        log.debug("Timesheet object initialized.")
        log.debug("Timesheet data file: {}".format(self.data_file))

        self._update_signed_in()

    def _update_signed_in(self):
        """Update the list of all entries that haven't been signed out."""
        # NOTE(amin): This doesn't prevent or detect multiple entries
        # with the same user signed in. This needs to be checked for
        # elsewhere. It also scales inefficiently with the total size
        # of the sheet.

        # TODO(amin): Make this add or remove an entry every time one is
        # saved, rather than scanning the whole sheet every time.
        self.signed_in = [k for k, v in self.sheet.items() if v['Out'] == ""]
        log.debug("Signed in entries: {}".format(self.signed_in))

    def load_entry(self, index):
        """Load an entry into its own object."""
        entry = Entry(
                    self.sheet[index]['User ID'],
                    self.sheet[index]['Date'],
                    self.sheet[index]['In'],
                    self.sheet[index]['Out'],
                    index
                )
        log.debug("Entry loaded: {}".format(repr(entry)))
        return entry

    def save_entry(self, entry, index=None):
        """Format an entry as a dictionary and add it to the timesheet
        with its index as the key.
        """
        if index is None:
            index = entry.index
        else:
            index = index

        entry_data = {}
        entry_data['Date'] = entry.date
        entry_data['User ID'] = entry.user_id
        entry_data['In'] = entry.time_in
        entry_data['Out'] = entry.time_out

        self.sheet[index] = entry_data
        log.debug("Entry saved: {}".format(repr(entry)))
        self._update_signed_in()

    def remove_entry(self, index):
        """Delete a single entry from the timesheet."""
        removed_entry = self.load_entry(index)
        del self.sheet[str(index)]
        log.debug("Entry removed: {}".format(removed_entry))
        self._update_signed_in()

    def search_entries(self, search_term):
        """Look through the values of all entries.
        Return a set of the indices of all entries that have a value matching
        the search term.
        """
        indices = {
            k for k, v in self.sheet.items() if search_term in str(v.items())
        }
        log.debug("Searched for {}. Results: {}".format(search_term, indices))
        return indices

    def load_sheet(self, data_file=None):
        """Read the timesheet from a json file."""
        if data_file is None:
            data_file = self.data_file

        with data_file.open('r') as f:
            self.sheet = json.load(f)
        log.debug("Sheet loaded from {}".format(data_file.resolve()))
        self._update_signed_in()

    def save_sheet(self, data_file=None):
        """Write the timesheet to json file."""
        if data_file is None:
            data_file = self.data_file

        with data_file.open('w') as f:
            json.dump(self.sheet, f, indent=4, sort_keys=True)
        log.debug("Sheet saved to {}".format(data_file.resolve()))


class Interface():

    class NotRegisteredError(Exception):
        pass

    class DuplicateEntryError(Exception):
        pass

    def __init__(self, users_file=None):
        if users_file is None:
            self.users_file = pathlib.Path('.', 'data', 'users.json')
        else:
            self.users_file = users_file
        log.debug("Interface object initialized")

    def is_valid(self, user_id):
        user_id = user_id.strip()

        valid = True

        try:
            _ = int(user_id)
        except ValueError:
            valid = False
        else:
            if len(user_id) != 9:
                valid = False
        finally:
            return valid

    def is_registered(self, user_id):
        user_id = user_id.strip()
        with self.users_file.open('r') as f:
            registered_ids = list(json.load(f).keys())
        if user_id in registered_ids:
            return True
        else:
            return False

    def sign(self, timesheet, user_id):
        user_id = user_id.strip()

        if not self.is_valid(user_id):
            log.debug("Invalid input: {}".format(user_id))
            raise ValueError(
                "Invalid Input: {}".format(user_id)
            )
        elif not self.is_registered(user_id):
            log.debug("User not registered: {}".format(user_id))
            raise self.NotRegisteredError(
                "{} not registered. Please register at the front desk.".format(
                    user_id
                )
            )

        try:
            [entry] = (
                [
                    i for i in timesheet.signed_in
                    if timesheet.sheet[i]['User ID'] == user_id
                ]
                or [None]
            )
        except ValueError:
            duplicate_entries = (
                [
                    i for i in timesheet.signed_in
                    if timesheet.sheet[i]['User ID'] == user_id
                ]
            )
            log.warning(
                "Multiple signed in instances of user {}: {}".format(
                    user_id, duplicate_entries
                )
            )
            log.info(
                "Signing out of duplicate instances of user {}: {}".format(
                    user_id, duplicate_entries
                )
            )
            for entry in duplicate_entries:
                e = timesheet.load_entry(entry)
                e.sign_out()
                timesheet.save_entry(e)

            raise self.DuplicateEntryError(
                "Signing out of duplicate instances of user {}".format(
                    user_id
                )
            )
        else:
            if not entry:
                timesheet.save_entry(Entry(user_id))
            else:
                e = timesheet.load_entry(entry)
                e.sign_out()
                timesheet.save_entry(e)


def main():
    setup_logger()
    log.debug("Program initialized")

    t = Timesheet()
    i = Interface()
    ui = gui.TimebookUI(t, i)

    log.debug("Program stopping")


if __name__ == '__main__':
    main()
