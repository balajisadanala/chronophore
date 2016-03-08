import json

# TODO:
# - format json output with nested keys
# - input validation
# - auto-completion
# - search to see if user is already signed in

class Entry():
    """Contains all data for a single entry"""
    def __init__(self, date, user_id, time_in, time_out):
        self.date = date
        self.user_id = user_id
        self.time_in = time_in
        self.time_out = time_out
        self.timesheet = {'Date' : date,
                          'Student ID' : user_id,
                          'In' : time_in,
                          'Out' : time_out}

def print_entry(entry):
    for key in entry.timesheet.keys():
        print("{}: {}".format(key, entry.timesheet[key]))
            
def save_entry(entry, timesheet_file='./timesheet.json'):
    with open(timesheet_file, 'a') as f:
        entry = "{}\n".format(
            json.dumps(entry.timesheet, indent=4, sort_keys=True))
        f.write(entry)

def load_entry(entry, timesheet_file='./timesheet.json'):
    pass
    #with open(timesheet_file, 'r') as f:
        #json.loads(f, indent
        
def main():
    x = Entry("2016-02-17", "889870966", "10:45", "13:30")
    print_entry(x)
    save_entry(x)

if __name__ == '__main__':
    main()
