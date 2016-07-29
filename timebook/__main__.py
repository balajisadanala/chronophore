import logging
from timebook.controller import Interface
from timebook.gui import TimebookUI
from timebook.models import Entry, Timesheet

logger = logging.getLogger(__name__)

logger.debug("Program initialized")

t = Timesheet()
i = Interface()
ui = TimebookUI(timesheet=t, interface=i)

logger.debug("Program stopping")
