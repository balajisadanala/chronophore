Timebook
========
Timebook is a simple time-tracking program. It keeps track of users' hours as they sign in and out. Data is stored in a human-readable json file. 

This project was started to help keep track of students signing in and out at a tutoring program in a community college, but should be adaptable to other use cases.


To Do
-----
- [ ] come up with a name no one else is using
- [ ] command line mvp
    - [x] write to and read from a json file
    - [x] format json output with nested keys
    - [x] generate uuid indices for entries
    - [x] keep track of which users are signed in
    - [ ] logging
    - [ ] validate user input
    - [ ] validate json file
    - [ ] load timesheet file partially into memory if possible ([ijson](https://pypi.python.org/pypi/ijson/))
- [ ] automatically sign-out any signed in users at the end of the day
- [ ] use configuration file(s)
- [ ] make seperate json database for user information
- [ ] simple gui frontend
    - [ ] auto-completion
- [ ] access database over local wireless network
    - [ ] improve security (encrypt/decrypt database, securely handle passwords...)
- [ ] package to be a portable windows executable
- [ ] generate reports from data, e.g. "total time person x has been signed in"


Lessons Learned
---------------
- Premature abstraction is inefficient.
    - First make the straight-line code that does what you want it to do.
    - Understand the problem space.
    - Then consider which parts of the code are useful to abstract into functions or classes.
- Premature optimization is inefficient.
    - Always keep performance in mind, but write the basic version of the code first.
    - Understand the performance constraints before optimizing.
- When creating an API, [write the usage code first](https://mollyrocket.com/casey/stream_0029.html).
