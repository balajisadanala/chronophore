import json
import os
import uuid
from datetime import datetime, timedelta

# TODO:
# - [ ] user-facing command line interface
# - [ ] exceptions/validation
# - [ ] protect agains accidental file overwrite
# - [ ] logging
# - [ ] command line mvp
# - [ ] load timesheet file partially into memory if possible
# - [ ] auto-completion


class Entry():
    """Contains all data for a single entry"""

    # NOTE(amin): Use __slots__ here if this ever get's to a scale where memory
    # needs to be saved (thousands of instances).

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

    # TODO(amin): update use this as __str__() and make a new __repr()__
    def __repr__(self):
        """Return the entry as it will appear in the json file."""
        data = {}
        data['Date'] = self.date
        data['Student ID'] = self.user_id
        data['In'] = self.time_in
        data['Out'] = self.time_out
        entry = {}
        entry[self.index] = data
        return json.dumps(entry, indent=4, sort_keys=True)

    def _get_current_datetime(self):
        """Serves as a mockable reference to datetime.today(). Mocking is used
        in the unit tests.
        """
        return datetime.today()

    def _make_index(self):
        """Generate a UUID version 4 (basically random)"""
        return str(uuid.uuid4())

    def sign_out(self):
        """Get the time the user signed out"""
        now = self._get_current_datetime()
        self.time_out = datetime.strftime(now, "%H:%M:%S")


class Timesheet():
    """Contains multiple entries"""

    # TODO(amin): add __repr()__ and __str()__

    def __init__(self):
        self.sheet = {}
        self.signedin = []

    def _update_signed_in(self):
        """Update the list of all entries that haven't been signed out."""
        # TODO(amin): throw an exception if a duplicate is assigned
        self.signedin = [k for k, v in self.sheet.items() if v['Out'] == ""]

    def load_entry(self, index):
        """Load an entry into its own object."""
        entry = Entry(
                    self.sheet[index]['Student ID'],
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
        entry_data['Student ID'] = entry.user_id
        entry_data['In'] = entry.time_in
        entry_data['Out'] = entry.time_out

        self.sheet[index] = entry_data
        self._update_signed_in()

    def remove_entry(self, index):
        """Delete a single entry from the timesheet."""
        del self.sheet[str(index)]
        self._update_signed_in()

    def search_entries(self, search_term):
        """Look through the values of all entries.
        Return a list of the indices of all entries that have a value matching
        the search term.
        """
        # NOTE(amin): use a tuple instead of a list here?
        entries = [
            k for k, v in self.sheet.items() if search_term in str(v.items())
        ]
        return sorted(entries)

    def load_sheet(self, timesheet_file='./timesheet.json'):
        """Read the timesheet from a json file."""
        with open(timesheet_file, 'r') as f:
            self.sheet = json.load(f)
        self._update_signed_in()

    def save_sheet(self, timesheet_file='./timesheet.json'):
        """Write the timesheet to json file."""
        with open(timesheet_file, 'w') as f:
            json.dump(self.sheet, f, indent=4, sort_keys=True)


def sign(timesheet, user_id):
    try:
        [entry] = [i for i in timesheet.signedin if
                   timesheet.sheet[i]['Student ID'] == user_id] or [None]
    except ValueError as e:
        # TODO(amin): decide how to catch this
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
    t = Timesheet()
    for uid in range(50):
        sign(t, uid)
    for uid in range(50):
        sign(t, uid)
    t.save_sheet()


if __name__ == '__main__':
    main()
