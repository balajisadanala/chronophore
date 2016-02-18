timesheet = {}

date = "2016-02-17"
student_id = "881260166"
time_in = "10:45"
time_out = "13:30"

timesheet.update({'Date' : date, 'Student ID' : student_id, 'In' : time_in, 'Out' : time_out})

for key in timesheet.keys():
    print("{}: {}".format(key, timesheet[key]))
