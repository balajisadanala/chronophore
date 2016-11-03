# TODO(amin):
# - [x] display all widgets in main window
# - [x] make a proper layout
# - [ ] enable sign in
# - [ ] display currently signed in
# - [ ] display feedback label
# - [ ] display confirmation windows
# - [ ] use fonts from config
# - [ ] keybindings

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

__title__ = 'Chronophore'
__version__ = '0.5.1'



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


        lbl_welcome = QLabel('Welcome to the Stem Center', self)
        #lbl_welcome.setFont(QFont('SansSerif', CONFIG['LARGE_FONT_SIZE']))
        lbl_id = QLabel('Enter Student ID:', self)
        self.ent_id = QLineEdit(self)
        lbl_feedback = QLabel('(Feedback goes here)', self)
        btn_sign = QPushButton('Sign In/Out', self)
        btn_sign.setToolTip('Sign in or out from the tutoring center')
        btn_sign.resize(btn_sign.sizeHint())
        btn_sign.clicked.connect(self._show_user_type_dialogue)

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



if __name__ == '__main__':
    app = QApplication(sys.argv)
    chrono_ui = ChronophoreUI()
    sys.exit(app.exec_())
