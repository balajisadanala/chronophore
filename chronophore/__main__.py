import logging

from chronophore.view import ChronophoreUI
from chronophore.model import Timesheet


def main():
    logger = logging.getLogger(__name__)

    logger.debug("Program initialized")

    ChronophoreUI(timesheet=Timesheet())

    logger.debug("Program stopping")

if __name__ == '__main__':
    main()
