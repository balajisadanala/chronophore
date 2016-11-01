#!/usr/bin/python3

import argparse
import logging
import pathlib
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from chronophore.models import Base, Entry

__description__ = """
Update Chronophore database to be compatible with a new version.
"""


def migrate_050_to_051(session):
    """Set time_out field of all flagged
    timesheet entries to Null.
    """
    entries_to_update = session.query(Entry).filter(
            Entry.forgot_sign_out.is_(True)).filter(
            Entry.time_out.isnot(None))

    for entry in entries_to_update:
        entry.time_out = None
        logging.info('Entry updated {}'.format(entry.uuid))
        logging.debug(entry.uuid)
        session.add(entry)


def get_args():
    parser = argparse.ArgumentParser(
        description=__description__
    )
    parser.add_argument(
        'database',
        help='Chronophore database to update in-place',
    )
    parser.add_argument(
        '-n', '--dry-run', action='store_true',
        help='perform a trial run with no changes made'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='print a detailed log'
    )

    return parser.parse_args()


def main():
    args = get_args()

    DRY_RUN = args.dry_run

    if args.verbose:
        LOGGING_LEVEL = logging.DEBUG
    else:
        LOGGING_LEVEL = logging.INFO

    logging.basicConfig(
        level=LOGGING_LEVEL,
        format='%(levelname)s:%(asctime)s: %(message)s'
    )

    if DRY_RUN:
        logging.info('Starting test run...')

    DATABASE_FILE = pathlib.Path(args.database)

    engine = create_engine('sqlite:///{}'.format(DATABASE_FILE))
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    session = Session()

    migrate_050_to_051(session)

    try:
        if not DRY_RUN:
            session.commit()

    except sqlalchemy.exc.IntegrityError as e:
        bad_items = '\n\t'.join(str(p) for p in e.params)
        logging.error('{}:\n\t{}'.format(e.orig, bad_items))
        logging.debug(e)
        logging.info('No data commited to database.')

    else:
        if not DRY_RUN:
            logging.info('Data successfully commited to database.')
        else:
            logging.info('Finishing test run.\nNo data commited to database.')

    finally:
        session.close()


if __name__ == '__main__':
    main()
