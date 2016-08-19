import logging
from timebook.view import TimebookUI
from timebook.model import Timesheet

logger = logging.getLogger(__name__)

logger.debug("Program initialized")

t = Timesheet()
ui = TimebookUI(timesheet=t)

logger.debug("Program stopping")
