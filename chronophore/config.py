from pathlib import Path

# Files
DATA_DIR = Path.home() / '.local' / 'share' / 'chronophore'
USERS_FILE = DATA_DIR.joinpath('users.json')

# GUI Settings
USER_ID_LENGTH = 9
MESSAGE_DURATION = 5
GUI_WELCOME_LABLE = "Welcome to the STEM Learning Center!"
