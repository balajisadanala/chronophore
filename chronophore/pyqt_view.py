# TODO(amin):
# - [x] display all widgets in main window
# - [x] make a proper layout
# - [x] enable sign in
# - [x] display currently signed in
# - [x] display feedback label
# - [x] display confirmation windows
# - [x] keybindings
# - [ ] use fonts from config

import logging
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDesktopWidget,
    QDialog,
    QFrame,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from chronophore import __title__, __version__, controller
from chronophore.config import CONFIG

logger = logging.getLogger(__name__)


class ChronophoreUI(QWidget):

    def __init__(self):
        super().__init__()
        self.signed_in = ''
        self.feedback_label_timer = QTimer()

        QToolTip.setFont(QFont('SansSerif', 10))

        lbl_signedin = QLabel('Currently Signed In:', self)
        frm_signed_in = QFrame(self)
        frm_signed_in.setFrameShape(QFrame.StyledPanel)
        self.lbl_signedin_list = QLabel(self.signed_in, frm_signed_in)

        lbl_welcome = QLabel(CONFIG['GUI_WELCOME_LABLE'], self)
        # lbl_welcome.setFont(QFont('SansSerif', CONFIG['LARGE_FONT_SIZE']))
        lbl_id = QLabel('Enter Student ID:', self)
        self.ent_id = QLineEdit(self)
        # TODO(amin): use an input mask or validator to constrain input:
        # http://doc.qt.io/qt-5/qlineedit.html#inputMask-prop
        # http://doc.qt.io/qt-5/qvalidator.html
        # TODO(amin): set cursor to 0 upon focus or use a validator instead
        self.ent_id.setInputMask('999999999')
        self.lbl_feedback = QLabel(self)
        btn_sign = QPushButton('Sign In/Out', self)
        btn_sign.setToolTip('Sign in or out from the tutoring center')
        btn_sign.resize(btn_sign.sizeHint())
        btn_sign.clicked.connect(self._sign_button_press)
        btn_sign.setAutoDefault(True)

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
        grid.addWidget(self.lbl_feedback, 4, 3, Qt.AlignTop | Qt.AlignCenter)
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
        self.ent_id.setFocus()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            self._sign_button_press()

    def _center(self):
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

    def _show_feedback_label(self, message, seconds=None):
        """Display a message in lbl_feedback, which times out
        after some number of seconds.
        """
        if seconds is None:
            seconds = CONFIG['MESSAGE_DURATION']

        logger.debug('Label feedback: "{}"'.format(message))

        self.feedback_label_timer.timeout.connect(self._hide_feedback_label)
        self.lbl_feedback.setText(str(message))
        self.lbl_feedback.show()
        self.feedback_label_timer.start(1000 * seconds)

    def _hide_feedback_label(self):
        # TODO(amin): Figure out how to either limit the size of the label,
        # to reset the layout to a normal size upon its disappearance, or
        # both. The whole layout currently gets messed up if this label is
        # assigned a long string.
        self.lbl_feedback.setText('')

    def _sign_button_press(self):
        """Validate input from ent_id, then sign in to the Timesheet."""
        user_id = self.ent_id.text().strip()

        try:
            status = controller.sign(user_id)

        # ERROR: User type is unknown (!student and !tutor)
        except ValueError as e:
            logger.error(e, exc_info=True)
            QMessageBox.critical(
                self,
                __title__ + ' Error',
                str(e),
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok,
            )

        # ERROR: User is unregistered
        except controller.UnregisteredUser as e:
            logger.debug(e)
            QMessageBox.warning(
                self,
                'Unregistered User',
                str(e),
                buttons=QMessageBox.Ok,
                defaultButton=QMessageBox.Ok,
            )

        # User needs to select type
        except controller.AmbiguousUserType as e:
            logger.debug(e)
            u = UserTypeSelectionDialog('Select User Type: ', self)
            if u.exec_() == QDialog.Accepted:
                status = controller.sign(user_id, user_type=u.user_type)
                self._show_feedback_label(
                    'Signed {}: {} ({})'.format(
                        status.in_or_out, status.user_name, status.user_type
                    )
                )

        # User has signed in or out normally
        else:
            sign_choice_confirmed = QMessageBox.question(
                self,
                'Confirm Sign-{}'.format(status.in_or_out),
                'Sign {}: {}?'.format(status.in_or_out, status.user_name),
                buttons=QMessageBox.Yes | QMessageBox.No,
                defaultButton=QMessageBox.Yes,
            )

            if sign_choice_confirmed == QMessageBox.No:
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
            self.ent_id.clear()
            self.ent_id.setFocus()


class UserTypeSelectionDialog(QDialog):

    def __init__(self, message, parent=None):
        super(UserTypeSelectionDialog, self).__init__(parent)

        lbl_message = QLabel(message, self)

        self.rb_tutor = QRadioButton('Tutor', self)
        self.rb_student = QRadioButton('Student', self)
        self.rb_tutor.setFocusPolicy(Qt.StrongFocus)
        self.rb_student.setFocusPolicy(Qt.StrongFocus)

        radio_vbox = QVBoxLayout()
        radio_vbox.addWidget(self.rb_tutor)
        radio_vbox.addWidget(self.rb_student)

        radios = QGroupBox(self)
        radios.setLayout(radio_vbox)

        btn_sign_in = QPushButton('Sign In', self)
        btn_sign_in.setDefault(True)
        btn_sign_in.setAutoDefault(True)
        btn_cancel = QPushButton('Cancel', self)
        btn_cancel.setAutoDefault(True)

        btn_sign_in.clicked.connect(self.update_user_type)
        btn_cancel.clicked.connect(self.reject)

        self.rb_tutor.setChecked(True)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn_sign_in)
        hbox.addWidget(btn_cancel)

        vbox = QVBoxLayout()
        vbox.addWidget(lbl_message)
        vbox.addWidget(radios)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle('User Type Selection')
        self.show()

    def update_user_type(self):
        if self.rb_tutor.isChecked():
            self.user_type = 'tutor'
        elif self.rb_student.isChecked():
            self.user_type = 'student'
        self.accept()
