Notes
=====


Requirements
------------
- Gui
    - Panes
        - Currently signed in
        - Sign-in form
        - Current tutors
        - Admin
- Run on windows (.exe)
- Portable (no installation, no unincluded dependencies)
- Human readable data files
- Store data files in hierarchical folders: year, month
- Check student login against student registry, prompt for registration if entry not found
- Admin interface
    - Generate report within date range
    - Add/Remove/Flag students in student registry
- Fail gracefully
    - Auto save
    - Detect corrupt files
- Handle bad data
    - Detect when someone has forgotten to sign out
    - Omit bad entries in final report
    - Flag bad entries in raw data
    - Flag students that forget to sign out
        - Display reminder for student next time they sign in


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


Report
------
- Portable, flexible format (csv?)
- Omit bad entries (incomplete, no sign out time)
- List of dates within range
    - Date
        - Total student hours per date
        - Total bad entries per date


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
