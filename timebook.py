import json
import os
import uuid
from datetime import datetime, timedelta

# TODO:
# - [ ] user-facing command line interface
# - [ ] exceptions/validation
# - [ ] protect agains accidental file overwrite
# - [ ] command line mvp
# - [ ] load timesheet file partially into memory if possible
# - [ ] auto-completion


class Entry():
    """Contains all data for a single entry"""
    def __init__(self, user_id=None, date=None, time_in=None,
                 time_out=None, index=None):
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

    def __repr__(self):
        data = {}
        data['Date'] = self.date
        data['Student ID'] = self.user_id
        data['In'] = self.time_in
        data['Out'] = self.time_out
        entry = {}
        entry[self.index] = data
        return json.dumps(entry, indent=4, sort_keys=True)

    def _get_current_datetime(self):
        """Serves as a mockable reference to datetime.today()"""
        return datetime.today()

    def _make_index(self):
        return str(uuid.uuid4())

    def sign_out(self):
        now = self._get_current_datetime()
        self.time_out = datetime.strftime(now, "%H:%M:%S")


class Timesheet():
    """Contains multiple entries"""
    def __init__(self):
        self.sheet = {}
        self.signedin = []

    def _make_dict(self, entry):
        data = {}
        data['Date'] = entry.date
        data['Student ID'] = entry.user_id
        data['In'] = entry.time_in
        data['Out'] = entry.time_out
        return data

    def _update_signed_in(self):
        self.signedin = [k for k, v in self.sheet.items() if v['Out'] == ""]

    def find_entry(self, search_term):
        # NOTE(amin): use a tuple instead of a list here?
        entries = [
            k for k, v in self.sheet.items() if search_term in str(v.items())
        ]
        return sorted(entries)

    def load_entry(self, index):
        entry = Entry(
                    self.sheet[index]['Student ID'],
                    self.sheet[index]['Date'],
                    self.sheet[index]['In'],
                    self.sheet[index]['Out'],
                    index
                )
        return entry

    def save_entry(self, entry, index=None):
        if index is None:
            index = entry.index
        else:
            index = index
        entry_data = self._make_dict(entry)
        self.sheet[index] = entry_data
        self._update_signed_in()

    def remove_entry(self, index):
        del self.sheet[str(index)]
        self._update_signed_in()

    def load_sheet(self, timesheet_file='./timesheet.json'):
        with open(timesheet_file, 'r') as f:
            self.sheet = json.load(f)
        self._update_signed_in()

    def save_sheet(self, timesheet_file='./timesheet.json'):
        with open(timesheet_file, 'w') as f:
            json.dump(self.sheet, f, indent=4, sort_keys=True)


def main():
    t = Timesheet()
    x = Entry("889870966")
    y = Entry("883830333")
    t.save_entry(x)
    entries = t.find_entry("889870966")
    for index in entries:
        print(index)
        e = t.load_entry(index)
        print(e.index)
        print(e.user_id)
        print(e.date)
        print(e.time_in)
        print(e.time_out)
    t.save_entry(y)
    t.save_sheet()


if __name__ == '__main__':
    main()
