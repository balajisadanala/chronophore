import json
import logging
import os
import uuid
from datetime import datetime, timedelta

log = logging.getLogger(__name__)


def setup_logger():
    log.setLevel(logging.DEBUG)

    fh = logging.FileHandler('debug.log')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    formatter = logging.Formatter("{asctime} {levelname}: {message}", style='{')
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
        log.debug("Entry signed out: {}".format(repr(self)))


class Timesheet():
    """Contains multiple entries"""

    def __init__(self):
        self.sheet = {}
        self.signedin = []
        self._update_signed_in()

    def _update_signed_in(self):
        """Update the list of all entries that haven't been signed out."""
        # NOTE(amin): This doesn't prevent or detect multiple entries
        # with the same user signed in. This needs to be checked for
        # elsewhere. It also scales inefficiently with the total size 
        # of the sheet.

        # TODO(amin): Make this add or remove an entry every time one is
        # saved, rather than scanning the whole sheet every time.
        self.signedin = [k for k, v in self.sheet.items() if v['Out'] == ""]
        log.debug("Signed in entries: {}".format(self.signedin))

    def load_entry(self, index):
        """Load an entry into its own object."""
        entry = Entry(
                    self.sheet[index]['User ID'],
                    self.sheet[index]['Date'],
                    self.sheet[index]['In'],
                    self.sheet[index]['Out'],
                    index
                )
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
        del self.sheet[str(index)]
        log.debug("Entry removed: {}".format(load_entry(index)))
        self._update_signed_in()

    def search_entries(self, search_term):
        """Look through the values of all entries.
        Return a set of the indices of all entries that have a value matching
        the search term.
        """
        indices = {
            k for k, v in self.sheet.items() if search_term in str(v.items())
        }
        return indices

    def load_sheet(self, timesheet_file='./timesheet.json'):
        """Read the timesheet from a json file."""
        with open(timesheet_file, 'r') as f:
            self.sheet = json.load(f)
        log.debug("Sheet loaded from {}".format(timesheet_file))
        self._update_signed_in()

    def save_sheet(self, timesheet_file='./timesheet.json'):
        """Write the timesheet to json file."""
        with open(timesheet_file, 'w') as f:
            json.dump(self.sheet, f, indent=4, sort_keys=True)
        log.debug("Sheet saved to {}".format(timesheet_file))


def sign(timesheet, user_id):
    try:
        [entry] = [i for i in timesheet.signedin if
                   timesheet.sheet[i]['User ID'] == user_id] or [None]
    except ValueError as e:
        # TODO(amin): catch and resolve this without exiting
        print(e)
        raise SystemExit
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
    t.load_sheet()

    while True:
        print("Timebook")
        print("========")
        print("1. Sign In or Out")
        print("2. List Signed In")
        print("q. Exit\n")
        menu_choice = input("Enter a choice: ")
        if menu_choice == '1':
            user_id = input("Enter User ID: ")
            sign(t, user_id)
        elif menu_choice == '2':
            print("Currently Signed In:")
            for i in t.signedin:
                print(t.sheet[i]['User ID'])
        elif menu_choice == 'q':
            break
        else:
            print("Invalid choice.")
        print("\n")
        t.save_sheet()
    t.save_sheet()

    log.debug("Program stopping")


if __name__ == '__main__':
    main()
