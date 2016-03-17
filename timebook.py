import json
import os

# TODO:
# - format json output with nested keys
# - input validation
# - auto-completion
# - search to see if user is already signed in
# - validate file
# - figure out whether or not to load whole file into memory (iteration?)
# - make separate timesheet class that is responsible for writing
#   and formatting the json

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

    def _make_dict(self):
        self.data['Date'] = self.date
        self.data['Student ID'] = self.user_id
        self.data['In'] = self.time_in
        self.data['Out'] = self.time_out

    def print_entry(entry):
        for key in entry.data.keys():
            print("{}: {}".format(key, entry.data[key]))

    def save_entry(self, timesheet_file='./timesheet.json'):
        self.new_index(timesheet_file)
        self.make_dict()
        with open(timesheet_file, 'a') as f:
            entry = "{}\n".format(
                json.dumps(self.data, indent=4, sort_keys=True))
            f.write(entry)

    def load_entry(self, timesheet_file='./timesheet.json'):
        with open(timesheet_file, 'r') as f:
            self.data = json.load(f)
            
    def new_index(self, timesheet_file='./timesheet.json'):
        if os.stat(timesheet_file).st_size == 0:
            self.index = 0
        else:
            with open(timesheet_file, 'r') as f:
                entries = json.load(f)
                biggest = entries["Index"]
                self.index = biggest + 1

class Timesheet():
    def __init__(self):
        self.sheet = {}

    def add_entry(self, entry):
        index = self._make_index()
        entry_data = self._make_dict(entry)
        self.sheet[index]= entry_data

    def _make_dict(self, entry):
        data = {}
        data['Date'] = entry.date
        data['Student ID'] = entry.user_id
        data['In'] = entry.time_in
        data['Out'] = entry.time_out

        return data

    def _make_index(self):
        if len(self.sheet.keys()) == 0:
            index = 0

        else:
            biggest = max(key for key in self.sheet.keys())
            index = int(biggest) + 1

        return str(index)


def main():
    x = Entry("2016-02-17", "889870966", "10:45", "13:30")
    t = Timesheet()
    t.add_entry(x)
    print(json.dumps(t.sheet))

if __name__ == '__main__':
    main()
