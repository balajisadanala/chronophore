Notes
=====

Sign-in Dialogue
----------------
- When a user sign's in, a dialogue box appears with options
depending on the user's type(s):
    - For all users:
        - Cancel
    - For students:
        - "I'm here to study"
        - "I'm here to see an academic counsellor"
    - For tutors:
        - "I'm here to tutor"


Some new considerations
-----------------------
- Remove some responsibilities from Timesheet into other classes
    - Persistence calls (loading, saving)
    - Tracking signed in users
- UI
    - Add an undo option in case someone mistakenly signs in as the wrong person
    - Use names rather than ids to sign in? Solve name collisions with unique images?
- Privacy/Security
    - Remove list of names signed in
    - Transfer data securely


Security
--------
- Store data on network enabled external hard drive
- Encrypt data files
- Admin interface is password protected 


Database Fields
---------------
- Student time sheet
    - UUID
        - Date
        - Student id
        - Time in
        - Time out

- Student registry
    - Student id
        - Date joined STEM
        - Date left STEM
        - Education plan (bool)
        - Email
        - Forgot to sign in (bool)
        - Major
        - Name


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
