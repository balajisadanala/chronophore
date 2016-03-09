from collections import defaultdict
import json
import os

# TODO:
# - format json output with nested keys
# - input validation
# - auto-completion
# - search to see if user is already signed in
# - validate file
# - figure out whether or not to load whole file into memory (iteration?)

class Entry():
    """Contains all data for a single entry"""
    def __init__(self, date=None, user_id=None, time_in=None, time_out=None):
        if date is None:
            self.date = ""
        else:
            self.date = date
        if user_id is None:
            self.user_id = ""
        else:
            self.user_id = user_id
        if time_in is None:
            self.time_in = ""
        else:
            self.time_in = time_in
        if time_out is None:
            self.time_out = ""
        else:
            self.time_out = time_out
        self.index = 0
        self.data = {}
        
    def make_dict(self):
        self.data = defaultdict()
        self.data['Date'] = self.date
        self.data['Student ID'] = self.user_id
        self.data['In'] = self.time_in
        self.data['Out'] = self.time_out

    def print_entry(entry):
        for key in entry.data.keys():
            print("{}: {}".format(key, entry.data[key]))

    def save_entry(self, timesheet_file='./timesheet.json'):
        with open(timesheet_file, 'a') as f:
            entry = "{}\n".format(
                json.dumps(self.data, indent=4, sort_keys=True))
            f.write(entry)

    def load_entry(self, timesheet_file='./timesheet.json'):
        with open(timesheet_file, 'r') as f:
            self.data = json.loads(f.read())


def main():
    x = Entry("2016-02-17", "889870966", "10:45", "13:30")
    x.print_entry()
    x.save_entry()

if __name__ == '__main__':
    main()
