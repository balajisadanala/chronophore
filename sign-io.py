import json

# TODO:
# - format json output with nested keys
# - input validation
# - auto-completion

class Entry():
    """Contains all data for a single entry"""
    def __init__(self, date, student_id, time_in, time_out):
        self.date = date
        self.student_id = student_id
        self.time_in = time_in
        self.time_out = time_out
        self.timesheet = {'Date' : date,
                          'Student ID' : student_id,
                          'In' : time_in,
                          'Out' : time_out}
    
    def print_entry(self):
        for key in self.timesheet.keys():
            print("{}: {}".format(key, self.timesheet[key]))

x = Entry("2016-02-17", "889870966", "10:45", "13:30")

x.print_entry()

with open('./timesheet.json', 'a') as f:
    entry = "{}\n".format(json.dumps(x.timesheet,
                                     indent=4, sort_keys=True))
    f.write(entry)
    
