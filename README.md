Timebook
========
Timebook is a simple time-tracking program. It keeps track of users' hours as they sign in and out. Data is stored in a human-readable json file. 

This project was started to help keep track of students signing in and out at a tutoring program in a community college, but should be adaptable to other use cases.


To Do
-----
- [x] Write to and read from a json file
- [x] Format json output with nested keys
- [x] Generate uuid indices for entries
- [x] Keep track of which users are signed in
- [x] Logging
- [ ] Student registry json file
- [ ] Validate user input
    - [ ] Check whether student is registered 
- [ ] Organize data files in date-based hierarchy
- [ ] Startup tasks
    - [ ] Load or create data file based on current date
    - [ ] Check for bad entries from previous days
    - [ ] Flag students that forgot to sign out
- [ ] Separate thread to periodically auto save
- [x] Tkinter gui
- [ ] Admin page
    - [ ] Generate reports from data, e.g. "total time person x has been signed in"
- [ ] Configuration file
- [ ] Improve security
    - [ ] Access database over local wireless network
    - [ ] Encrypt/decrypt database
- [ ] Package to be a portable windows executable
- [ ] Come up with a name no one else is using


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
