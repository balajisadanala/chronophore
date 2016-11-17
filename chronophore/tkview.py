import contextlib
import logging
import tkinter
from tkinter import font, messagebox, ttk, Toplevel, N, S, E, W

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
            command=self._sign_in_button_press,
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
        self.root.bind('<Return>', self._sign_in_button_press)
        self.root.bind('<KP_Enter>', self._sign_in_button_press)

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
        logger.debug('Sign in confirmed: {}'.format(yes_pressed))
        return yes_pressed

    def _sign_in_button_press(self, *args):
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
            u = TkUserTypeSelectionDialog(self.root)
            if u.user_type:
                status = controller.sign(user_id, user_type=u.user_type)
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


class TkUserTypeSelectionDialog(Toplevel):
    """A modal dialog presenting the user with
    options for what kind of user to sign in as.
    """

    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        self.title('User Type Selection')
        self.parent = parent

        # variables
        self.rb_choice = tkinter.StringVar()
        self.user_type = None

        # widgets
        self.frame = ttk.Frame(self, padding=(5, 5, 10, 10))

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
            text='Ok',
            command=self._ok,
        )
        self.btn_cancel = ttk.Button(
            self.frame,
            text='Cancel',
            command=self._cancel,
        )

        # assemble grid
        self.frame.grid(column=0, row=0, sticky=(N, S, E, W))
        self.lbl_message.grid(column=0, row=0, columnspan=2, sticky=(W, E))
        self.rb_student.grid(column=0, row=1, columnspan=2, sticky=W)
        self.rb_tutor.grid(column=0, row=2, columnspan=2, sticky=W)
        self.btn_ok.grid(column=0, row=3)
        self.btn_cancel.grid(column=1, row=3)

        # 'Tutor' is selected by default
        self.rb_tutor.invoke()
        self.btn_ok.focus_set()
        self.grab_set()

        self.protocol('WM_DELETE_WINDOW', self._cancel)

        # key bindings
        self.bind('<Return>', self._ok)
        self.bind('<KP_Enter>', self._ok)
        self.bind('<Escape>', self._cancel)

        self.wait_window(self)

    def _ok(self, event=None):
        self._apply()
        self._cancel()

    def _cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()

    def _apply(self):
        user_type = self.rb_choice.get()
        if user_type == 'student' or user_type == 'tutor':
            self.user_type = user_type

        logger.debug('User type selected: {}'.format(self.user_type))
