import logging
from chronophore.view import ChronophoreUI
from chronophore.model import Timesheet

logger = logging.getLogger(__name__)

logger.debug("Program initialized")

t = Timesheet()
ui = ChronophoreUI(timesheet=t)

logger.debug("Program stopping")
