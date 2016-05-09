import json
import os
import uuid
from datetime import datetime, timedelta

# TODO:
# - [ ] user-facing command line interface
# - [ ] exceptions/validation
# - [ ] command line mvp
# - [ ] load timesheet file partially into memory if possible
# - [ ] auto-completion


class Entry():
    """Contains all data for a single entry"""
    def __init__(self, date=None, user_id=None, time_in=None, time_out=None):
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

    def _get_current_datetime(self):
        """Serves as a mockable reference to datetime.today()"""
        return datetime.today()

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

    def _make_index(self):
        return str(uuid.uuid4())

    def _update_signed_in(self):
        self.signedin = [k for k, v in self.sheet.items() if v['Out'] == ""]

    def find_entry(self, search_term):
        entries = [
            k for k, v in self.sheet.items() if search_term in str(v.items())
        ]
        return sorted(entries)

    def add_entry(self, entry, index=None):
        if index == None:
            index = self._make_index()
        entry_data = self._make_dict(entry)
        self.sheet[index] = entry_data

    def remove_entry(self, index):
        del self.sheet[str(index)]

    def load_sheet(self, timesheet_file='./timesheet.json'):
        with open(timesheet_file, 'r') as f:
            self.sheet = json.load(f)

    def save_sheet(self, timesheet_file='./timesheet.json'):
        with open(timesheet_file, 'w') as f:
            json.dump(self.sheet, f, indent=4, sort_keys=True)


def main():
    x = Entry("2016-02-17", "889870966", "10:45", "13:30")
    t = Timesheet()
    t.add_entry(x)
    t.add_entry(x)
    t.add_entry(x)
    t.add_entry(x)
    t.add_entry(x)
    t.save_sheet()
    print(t.find_entry("10:45"))


if __name__ == '__main__':
    main()
