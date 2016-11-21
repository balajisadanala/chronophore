import contextlib
import logging
import tkinter
from tkinter import font, messagebox, ttk, N, S, E, W
from tkinter.simpledialog import Dialog

from chronophore import __title__, __version__, controller
from chronophore.config import CONFIG

logger = logging.getLogger(__name__)


class TkChronophoreUI:
    """Simple Tkinter GUI for chronophore :
            - Entry for user id input
            - Button to sign in or out
            - List of currently signed in users
    """

    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('{} {}'.format(__title__, __version__))
        self.content = ttk.Frame(self.root, padding=(5, 5, 10, 10))

        # custom fonts
        self.large_font = font.Font(family='Helvetica', size=CONFIG['LARGE_FONT_SIZE'])
        self.medium_font = font.Font(family='Helvetica', size=CONFIG['MEDIUM_FONT_SIZE'])
        self.small_font = font.Font(family='Helvetica', size=CONFIG['SMALL_FONT_SIZE'])
        self.tiny_font = font.Font(family='Helvetica', size=CONFIG['TINY_FONT_SIZE'])

        self.large_header = self.large_font.copy()
        self.large_header.configure(weight='bold')

        self.tiny_header = self.tiny_font.copy()
        self.tiny_header.configure(weight='bold')

        # default widget fonts
        ttk.Style().configure('TLabel', font=self.medium_font)
        ttk.Style().configure('TButton', font=self.medium_font)
        # NOTE(amin): The following won't work for mysterious
        # reasons internal to tk:
        # ttk.Style().configure('TEntry', font=self.medium_font)

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
            text="Currently Signed In:",
            font=self.tiny_header
        )
        self.lbl_signedin_list = ttk.Label(
            self.frm_signedin,
            textvariable=self.signed_in,
            font=self.tiny_font
        )
        self.lbl_welcome = ttk.Label(
            self.content,
            text=CONFIG['GUI_WELCOME_LABLE'],
            font=self.large_header
        )
        self.lbl_id = ttk.Label(
            self.content,
            text="Enter Student ID:",
        )
        self.ent_id = ttk.Entry(
            self.content,
            textvariable=self.user_id,
            font=self.small_font
        )
        self.lbl_feedback = ttk.Label(
            self.content,
            textvar=self.feedback,
        )
        self.btn_sign = ttk.Button(
            self.content,
            text="Sign In/Out",
            command=self._sign_button_press,
        )

        # assemble grid
        self.content.grid(column=0, row=0, sticky=(N, S, E, W))
        self.lbl_signedin.grid(column=0, row=0, pady=0)
        self.frm_signedin.grid(
            column=0, row=1, columnspan=1, rowspan=4, sticky=(N, S, E, W)
        )
        self.lbl_signedin_list.grid(column=0, row=0, columnspan=1, rowspan=4)
        self.lbl_welcome.grid(column=2, row=1, columnspan=1)
        self.lbl_id.grid(column=2, row=2, columnspan=1, sticky=(N))
        self.ent_id.grid(column=2, row=2, columnspan=1)
        self.lbl_feedback.grid(column=2, row=3)
        self.btn_sign.grid(column=2, row=4, columnspan=1, sticky=(N))

        # resize weights
        self.root.columnconfigure(0, weight=1, minsize=400)
        self.root.rowconfigure(0, weight=1, minsize=200)
        self.content.columnconfigure(0, weight=1, minsize=150)
        self.content.columnconfigure(1, weight=3)
        self.content.columnconfigure(2, weight=3)
        self.content.columnconfigure(3, weight=3)
        self.content.rowconfigure(0, weight=0)
        self.content.rowconfigure(1, weight=3, minsize=50)
        self.content.rowconfigure(2, weight=1, minsize=100)
        self.content.rowconfigure(3, weight=1)
        self.content.rowconfigure(4, weight=3)

        # key bindings
        self.root.bind('<Return>', self._sign_button_press)
        self.root.bind('<KP_Enter>', self._sign_button_press)

        self.ent_id.focus()
        self._set_signed_in()
        self.root.mainloop()

    def _set_signed_in(self):
        """Populate the signed_in list with the names of
        currently signed in users.
        """
        names = [
            controller.get_user_name(user, full_name=CONFIG['FULL_USER_NAMES'])
            for user in controller.signed_in_users()
        ]
        self.signed_in.set('\n'.join(sorted(names)))

    def _show_feedback_label(self, message, seconds=None):
        """Display a message in lbl_feedback, which then times out
        after some number of seconds. Use after() to schedule a callback
        to hide the feedback message. This works better than using threads,
        which can cause problems in Tk.
        """
        if seconds is None:
            seconds = CONFIG['MESSAGE_DURATION']

        # cancel any existing callback to clear the feedback
        # label. this prevents flickering and inconsistent
        # timing during rapid input.
        with contextlib.suppress(AttributeError):
            self.root.after_cancel(self.clear_feedback)

        logger.debug('Label feedback: "{}"'.format(message))
        self.feedback.set(message)
        self.clear_feedback = self.root.after(
            1000 * seconds, lambda: self.feedback.set("")
        )

    def _show_confirm_window(self, message, title):
        logger.debug('Window feedback: "{}"'.format(message))
        yes_pressed = messagebox.askyesno(
            message=message,
            title=title,
            icon='question',
            default='yes',
            parent=self.root,
        )
        # TODO(amin): Bind KP_Enter in all dialogs
        return yes_pressed

    def _sign_button_press(self, *args):
        """Validate input from ent_id, then sign in to the Timesheet."""
        user_id = self.ent_id.get().strip()

        try:
            status = controller.sign(user_id)

        # ERROR: User type is unknown (!student and !tutor)
        except ValueError as e:
            logger.error(e, exc_info=True)
            messagebox.showerror(message=e)

        # ERROR: User is unregistered
        except controller.UnregisteredUser as e:
            logger.debug(e)
            messagebox.showwarning(message=e)

        # User needs to select type
        except controller.AmbiguousUserType as e:
            logger.debug(e)
            u = TkUserTypeSelectionDialog(
                    parent=self.root,
                    title='User Type Selection',
                    entry_to_clear=self.ent_id)
            if u.result:
                logger.debug('User type selected: {}'.format(u.result))
                status = controller.sign(user_id, user_type=u.result)
                self._show_feedback_label(
                    'Signed {}: {} ({})'.format(
                        status.in_or_out, status.user_name, status.user_type
                    )
                )

        # User has signed in or out normally
        else:
            sign_choice_confirmed = self._show_confirm_window(
                'Sign {}: {}?'.format(status.in_or_out, status.user_name),
                'Confirm Sign-{}'.format(status.in_or_out)
            )

            logger.debug('Sign {} confirmed: {}'.format(
                status.in_or_out, sign_choice_confirmed
            ))

            if not sign_choice_confirmed:
                # Undo sign-in or sign-out
                if status.in_or_out == 'in':
                    controller.undo_sign_in(status.entry)
                elif status.in_or_out == 'out':
                    controller.undo_sign_out(status.entry)
            else:
                self._show_feedback_label(
                    'Signed {}: {}'.format(status.in_or_out, status.user_name)
                )

        finally:
            self._set_signed_in()
            self.ent_id.delete(0, 'end')
            self.ent_id.focus()


class TkUserTypeSelectionDialog(Dialog):
    """A modal dialog presenting the user with
    options for what kind of user to sign in as.
    """

    def __init__(self, parent, title=None, entry_to_clear=None):
        self.rb_choice = tkinter.StringVar()
        self.entry_to_clear = entry_to_clear
        tkinter.simpledialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        """Create dialog body. Return widget that
        should have initial focus.

        Inherited from tkinter.simpledialog.Dialog
        """
        self.frame = ttk.Frame(master, padding=(5, 5, 10, 10))

        self.lbl_message = ttk.Label(
            self.frame,
            text='Select User Type: ',
        )
        self.rb_student = ttk.Radiobutton(
            self.frame,
            text='Student',
            variable=self.rb_choice,
            value='student',
        )
        self.rb_tutor = ttk.Radiobutton(
            self.frame,
            text='Tutor',
            variable=self.rb_choice,
            value='tutor',
        )
        self.btn_ok = ttk.Button(
            self.frame,
            text='OK',
            command=self.ok,
        )
        self.btn_cancel = ttk.Button(
            self.frame,
            text='Cancel',
            command=self.cancel,
        )
        # assemble grid
        self.frame.grid(column=0, row=0, sticky=(N, S, E, W))
        self.lbl_message.grid(column=0, row=0, columnspan=2, sticky=(W, E))
        self.rb_student.grid(column=0, row=1, columnspan=2, sticky=W)
        self.rb_tutor.grid(column=0, row=2, columnspan=2, sticky=W)
        self.btn_ok.grid(column=0, row=3)
        self.btn_cancel.grid(column=1, row=3)

        # key bindings
        self.bind('<Return>', self.ok)
        self.bind('<KP_Enter>', self.ok)
        self.bind('<Escape>', self.cancel)

        self.rb_tutor.invoke()

        return self.btn_ok

    def buttonbox(self):
        """Inherited from tkinter.simpledialog.Dialog"""
        pass

    def ok(self, event=None):
        """This method is identical to
        tkinter.simpledialog.Dialog.ok(),
        but with 'self.withdraw()' commented out.
        """
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        # NOTE(amin): Using self.withdraw() here causes the
        # ui to hang until the window loses and regains
        # focus. There must be some blocking operation going
        # on, but after some digging, I haven't been able to
        # get any leads.

        # NOTE(amin): We must clear the main window's entry
        # before returning focus to it. Otherwise, rapid
        # pressing of the enter key will open multiple dialogs.
        self.entry_to_clear.delete(0, 'end')

        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()

    def apply(self):
        """Inherited from tkinter.simpledialog.Dialog"""
        user_type = self.rb_choice.get()
        if user_type == 'student' or user_type == 'tutor':
            self.result = user_type
