import threading
import time
import tkinter
from timebook import timebook
from tkinter import ttk, N, S, E, W


class TimebookUI():
    """Simple Tkinter GUI for timebook:
            - Entry for user id input
            - Button to sign in or out
            - List of currently signed in users
    """

    def __init__(self, timesheet):
        self.t = timesheet

        root = tkinter.Tk()
        root.title("STEM Sign In")
        self.content = ttk.Frame(root, padding=(5, 5, 10, 10))

        # variables
        self.signed_in = tkinter.StringVar()
        self.user_id = tkinter.StringVar()
        self.feedback = tkinter.StringVar()

        # widgets
        self.frm_signedin = ttk.Frame(
            self.content,
            borderwidth=5,
            relief="sunken",
            width=200,
            height=100
        )
        self.lbl_signedin = ttk.Label(
            self.content,
            text="Currently Signed In:"
        )
        self.lbl_signedin_list = ttk.Label(
            self.frm_signedin,
            textvariable=self.signed_in
        )
        self.lbl_welcome = ttk.Label(
            self.content,
            text="Welcome to the STEM Learning Center!"
        )
        self.lbl_id = ttk.Label(self.content, text="Enter Student ID")
        self.ent_id = ttk.Entry(
            self.content,
            textvariable=self.user_id)
        self.lbl_feedback = ttk.Label(self.content, textvar=self.feedback)
        self.btn_sign = ttk.Button(
            self.content,
            text="Sign In/Out",
            command=self.sign_in_out
        )

        # assemble grid
        self.content.grid(column=0, row=0, sticky=(N, S, E, W))
        self.lbl_signedin.grid(column=0, row=0, pady=0, sticky=(W))
        self.frm_signedin.grid(
            column=0, row=1, columnspan=1, rowspan=3, sticky=(N, S, E, W)
        )
        self.lbl_signedin_list.grid(column=0, row=0, columnspan=1, rowspan=3)
        self.lbl_welcome.grid(column=2, row=1, columnspan=1)
        # TODO(amin): figure out why lbl_id and btn_sign wiggle
        # when lbl_signedin_list updates
        self.lbl_id.grid(column=2, row=2, columnspan=1, sticky=(N))
        # TODO(amin): add select all shortcuts to this entry
        self.ent_id.grid(column=2, row=2, columnspan=1, sticky=(E, W))
        self.lbl_feedback.grid(column=2, row=2, sticky=(S))
        self.btn_sign.grid(column=2, row=3, columnspan=1, sticky=(N))

        # resize weights
        root.columnconfigure(0, minsize=400, weight=1)
        root.rowconfigure(0, minsize=200, weight=1)
        self.content.columnconfigure(0, weight=1)
        self.content.columnconfigure(1, weight=3)
        self.content.columnconfigure(2, weight=3)
        self.content.columnconfigure(3, weight=3)
        self.content.rowconfigure(0, weight=0)
        self.content.rowconfigure(1, weight=3)
        self.content.rowconfigure(2, minsize=100, weight=1)
        self.content.rowconfigure(3, weight=3)

        root.bind('<Return>', self.sign_in_out)
        root.bind('<KP_Enter>', self.sign_in_out)
        self.ent_id.focus()

        self.signed_in.set('\n'.join(sorted(
            [self.t.sheet[i]['User ID'] for i in self.t.signed_in])))
        root.mainloop()

    def show_feedback(self, message, seconds):
        """Use a thread to display a message in lbl_feedback that times out
        after some number of seconds. 
        """

        def feedback_timeout(message, seconds):
            self.feedback.set(message)
            time.sleep(seconds)
            self.feedback.set("")

        t = threading.Thread(target=feedback_timeout, args=(message, seconds))
        t.start()

    def sign_in_out(self, *args):
        """Validate input from ent_id, then sign in to the Timesheet."""
        user_id = self.ent_id.get()

        try:
            timebook.sign(self.t, user_id)
        except ValueError:
            self.show_feedback("Invalid Input", 3)
        else:
            self.show_feedback("Welcome", 3)
            self.t.save_sheet()
            self.signed_in.set('\n'.join(sorted(
                [self.t.sheet[i]['User ID'] for i in self.t.signed_in])))

        self.ent_id.delete(0, 'end')
        self.ent_id.focus()


if __name__ == '__main__':
    # Usage example
    t = timebook.Timesheet()
    ui = TimebookUI(t)
