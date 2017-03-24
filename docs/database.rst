Chronophore's Database
======================


Working with the Database
-------------------------

Chronophore's database lives in a single SQLite file (`chronophore.sqlite` by
default). It can be opened, browsed, and edited with a number of different
programs.

`DB Browser for SQLite`_, aka *SQLiteBrowser*, is one such program. It offers
an intuitive graphical interface that is somewhat similar to Microsoft Excel or
Access. It can be installed on Windows, Mac, or Linux.


Browse the Database
^^^^^^^^^^^^^^^^^^^

1. Run *SQLiteBrowser*.
2. Click the "Open Database" button.
3. Find and select Chronophore's database, then click open.
4. Click the "Browse Data" tab.
5. Use the drop-down menu to select a table to browse.
6. Data can be sorted and filtered by clicking on the column headers.


Add New Users
^^^^^^^^^^^^^

1. Switch to the "Browse Data" tab.
2. In the "Table" drop-down menu, select the "users" table.
3. Click "New Record". A new row will be created.
4. Fill in at least the required fields: `user_id`, `first_name`, `last_name`,
   `is_student`, and `is_tutor`.
5. Repeat to add a new record for each student.
6. Once all new records have been added, click the "Write Changes" button. This
   will commit your changes to the database.

.. important::
    Empty cells should say "`NULL`". If an empty cell doesn't have the word
    "`NULL`" in it:

    1. Double click the cell.
    2. Click the "Clear" or "Set As NULL" button.
    3. Click "Write Changes" button.


Delete Users
^^^^^^^^^^^^

This should almost never be necessary. If a user is no longer a part of the
program, simply fill in the `date_left` cell in their record. If a user truly
needs to be removed from the database, their Timesheet entries must be removed
first:

1. Use the drop-down menu in the "Browse Data" tab to switch to the "timesheet"
   table.
2. Filter the `user_id` column by the user's user id.
3. Select each row to be removed, then click the "Delete Record" button.
4. Use the drop-down menu in the "Browse Data" tab to switch to the "users"
   table.
5. Select the row for the user you want to delete, then click the "Delete
   Record" button.
6. If you are sure the correct records have been deleted, click the "Write
   Changes" button.

.. warning::
    Once changes have been written, they are permanent. Unwritten changes can
    be reverted with the "Revert Changes" button.


Export Data
^^^^^^^^^^^

*SQLiteBrowser* can export tables from the database as CSV files. The CSV files
can then be imported into, for example, spreadsheet software.

1. Click "File" -> "Export" -> "Table(s) as CSV File".
2. Select which tables to export, then click the "Ok" button.


View the Database Structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Information about the schema and structure of the database is available in the
"Database Structure" tab.


The Schema
----------

Chronophore's database has a relatively simple schema with only two tables.

Timesheet
^^^^^^^^^

This is the table that Chronophore writes to. It stores an entry for every time
someone signs in, then updates it when they sign out. It should generally not
be edited by hand.

It contains the following fields:

================= =======================================================
Field Name        Significance
================= =======================================================
`uuid`            A unique ID for each entry (*Primary Key*).
`date`            The date the user signed in.
`forgot_sign_out` `1` if the user never signed out, `0` otherwise.
`time_in`         Sign in time.
`time_out`        Sign out time.
`user_id`         The user's unique ID (*Foreign Key*).
`user_type`       Whether the user signed in as a `student` or a `tutor`.
================= =======================================================


Users
^^^^^

This table stores information about the registered users. A user will not be
able to sign in unless they have a record in this table. Chronophore itself
doesn't ever write to this database. It must be edited with another application
such as `DB Browser for SQLite`_.

It contains the following fields:

================ ===============================================================
Field Name       Significance
================ ===============================================================
`user_id`        The user's unique ID (*Primary Key*).
`date_joined`    The date on which the user was registered.
`date_left`      The date on which the user was no longer registered.
`education_plan` `1` if the user has submitted an education plan, `0` otherwise.
`school_email`   The user's school email.
`personal_email` The user's personal email.
`first_name`     The user's first name.
`last_name`      The user's last name.
`major`          The user's declared major.
`is_student`     `1` if the user is a student, `0` otherwise.
`is_tutor`       `1` if the user is a tutor, `0` otherwise.
================ ===============================================================


.. _DB Browser for SQLite: http://sqlitebrowser.org/
