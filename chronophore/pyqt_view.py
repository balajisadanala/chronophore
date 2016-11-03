# TODO(amin):
# - [x] display all widgets in main window
# - [x] make a proper layout
# - [x] enable sign in
# - [x] display currently signed in
# - [ ] display feedback label
# - [ ] display confirmation windows
# - [ ] use fonts from config
# - [ ] keybindings

import contextlib
import logging
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    qApp,
    QApplication,
    QDesktopWidget,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolTip,
    QWidget,
)

from chronophore import __title__, __version__, controller
from chronophore.config import CONFIG

logger = logging.getLogger(__name__)


class ChronophoreUI(QWidget):

    def __init__(self):
        super().__init__()

        # variables
        self.signed_in = 'Frodo\nSam\nGandalf\nPippin'
        self.user_id = ''
        self.feedback = ''
        self._init_ui()


    def _init_ui(self):
        QToolTip.setFont(QFont('SansSerif', 10))

        lbl_signedin = QLabel('Currently Signed In:', self)
        frm_signed_in = QFrame(self)
        frm_signed_in.setFrameShape(QFrame.StyledPanel)
        self.lbl_signedin_list = QLabel(self.signed_in, frm_signed_in)


        lbl_welcome = QLabel(CONFIG['GUI_WELCOME_LABLE'], self)
        #lbl_welcome.setFont(QFont('SansSerif', CONFIG['LARGE_FONT_SIZE']))
        lbl_id = QLabel('Enter Student ID:', self)
        self.ent_id = QLineEdit(self)
        lbl_feedback = QLabel('(Feedback goes here)', self)
        btn_sign = QPushButton('Sign In/Out', self)
        btn_sign.setToolTip('Sign in or out from the tutoring center')
        btn_sign.resize(btn_sign.sizeHint())
        #btn_sign.clicked.connect(self._show_user_type_dialogue)
        btn_sign.clicked.connect(self._sign_button_press)

        grid = QGridLayout()
        grid.setSpacing(10)

        # assemble grid
        # TODO(amin): Make everything bigger.
        grid.addWidget(lbl_signedin, 0, 0, Qt.AlignTop)
        grid.addWidget(frm_signed_in, 1, 0, 6, 1)
        grid.addWidget(self.lbl_signedin_list, 1, 0, 6, 1, Qt.AlignTop)

        grid.addWidget(lbl_welcome, 1, 1, 1, -1, Qt.AlignTop | Qt.AlignCenter)
        grid.addWidget(lbl_id, 2, 3, Qt.AlignBottom | Qt.AlignCenter)
        grid.addWidget(self.ent_id, 3, 3, Qt.AlignCenter)
        grid.addWidget(lbl_feedback, 4, 3, Qt.AlignTop | Qt.AlignCenter)
        grid.addWidget(btn_sign, 5, 3, Qt.AlignTop | Qt.AlignCenter)

        # resize weights
        grid.setColumnStretch(0, 10)
        grid.setColumnStretch(1, 10)
        grid.setColumnStretch(2, 10)
        grid.setColumnStretch(3, 30)
        grid.setColumnStretch(4, 10)
        grid.setColumnStretch(5, 10)
        grid.setRowStretch(0, 0)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 0)
        grid.setRowStretch(3, 0)
        grid.setRowStretch(4, 0)
        grid.setRowStretch(5, 1)
        grid.setRowStretch(6, 1)

        self.setLayout(grid)
        self._center()
        self.setWindowTitle('{} {}'.format(__title__, __version__))
        self._set_signed_in()
        self.show()

    def _show_user_type_dialogue(self, event):

        reply = QMessageBox.question(
            self,
            'Sign-in Options',
            'Are you tutoring today?',
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.Yes,
        )

        reply.center()

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def _center(self):
        # TODO(amin): remove this?
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _set_signed_in(self):
        """Populate the signed_in list with the names of
        currently signed in users.
        """
        names = [
            controller.get_user_name(user, full_name=CONFIG['FULL_USER_NAMES'])
            for user in controller.signed_in_users()
        ]
        self.lbl_signedin_list.setText('\n'.join(sorted(names)))


    def _sign_button_press(self):
        """Validate input from ent_id, then sign in to the Timesheet."""
        user_id = self.ent_id.text().strip()

        try:
            status = controller.sign(user_id)

        # ERROR: User type is unknown
        except ValueError as e:
            logger.error(e, exc_info=True)
            #messagebox.showerror(message=e)

        # ERROR: User is unregistered
        except controller.UnregisteredUser as e:
            logger.debug(e)
            #messagebox.showerror(message=e)

        # User needs to select type
        except controller.AmbiguousUserType as e:
            logger.debug(e)
            #user_type = UserTypeSelectionDialog(self).show()
            #if user_type:
            #    status = controller.sign(user_id, user_type=user_type)
            #    self._show_feedback_label(
            #        'Signed {}: {}'.format(status.in_or_out, status.user_name)
            #    )

        # User has signed in or out normally
        #else:
            # TODO(amin): bind KP_Enter here
            # self.root.bind('<KP_Enter>', self._sign_in_button_press)
            # http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
            #sign_choice_is_confirmed = self._show_confirm_window(
            #    'Sign {}: {}?'.format(status.in_or_out, status.user_name)
            #)

            #if not sign_choice_is_confirmed:
            #    # Undo sign-in or sign-out
            #    if status.in_or_out == 'in':
            #        controller.undo_sign_in(status.entry)
            #    elif status.in_or_out == 'out':
            #        controller.undo_sign_out(status.entry)
            #else:
            #    self._show_feedback_label(
            #        'Signed {}: {}'.format(status.in_or_out, status.user_name)
            #    )

        finally:
            self._set_signed_in()
            # TODO(amin): Clear entry and reset focus.
            #self.ent_id.delete(0, 'end')
            #self.ent_id.focus()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chrono_ui = ChronophoreUI()
    sys.exit(app.exec_())
