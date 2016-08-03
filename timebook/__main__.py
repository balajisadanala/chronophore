import logging
from timebook.controller import Controller
from timebook.view import TimebookUI
from timebook.model import Timesheet

logger = logging.getLogger(__name__)

logger.debug("Program initialized")

t = Timesheet()
c = Controller()
ui = TimebookUI(timesheet=t, controller=c)

logger.debug("Program stopping")
