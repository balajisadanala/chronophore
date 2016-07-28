Timebook
========
Timebook is a simple time-tracking program. It keeps track of users' hours as they sign in and out. Data is stored in a human-readable json file. 

This project was started to help keep track of students signing in and out at a tutoring program in a community college, but should be adaptable to other use cases.


To Do
-----
- Basic Features:
    - [x] Write to and read from a json file
    - [x] Format json output with nested keys
    - [x] Generate uuid indices for entries
    - [x] Keep track of which users are signed in
    - [x] Logging
    - [x] Tkinter gui
    - [x] Organize data files in date-based hierarchy
    - [x] Load or create data file on startup based on current date
    - [ ] Validate user input
        - [x] Basic user id validation
        - [x] Student registry json file
        - [x] Check whether student is registered 
        - [x] Handle invalid json files
        - [ ] Check for bad entries from previous days
        - [ ] Flag students that forgot to sign out
    - [ ] Package to be a portable windows executable

- Further Improvements: 
    - [ ] Basic Documentation
    - [ ] Configuration file
    - [ ] Access database over local wireless network
    - [ ] Separate thread to periodically auto save
    - [ ] Admin UI 
    - [ ] Encrypt/decrypt database
    - [ ] JSON to CSV converter
    - [ ] Change unit tests to use [file-like objects](http://stackoverflow.com/questions/3942820/how-to-do-unit-testing-of-functions-writing-files-using-python-unittest) instead of files
    - [ ] Convert unit tests to pytest syntax
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
