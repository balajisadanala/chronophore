#!/usr/bin/python3

import argparse
import json
import logging
import pathlib
import sqlalchemy

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from chronophore.models import Base, Entry, User


def get_args():
    parser = argparse.ArgumentParser(
        description='Load Chronophore json files into a sqlite database.'
    )
    parser.add_argument(
        'files',
        help='json file(s) to add to the database',
        type=str,
        nargs='+'
    )
    parser.add_argument(
        '-t', '--type',
        required=True,
        choices=['users', 'timesheet'],
        help='type of data stored in json file(s)'
    )
    parser.add_argument(
        '-o', '--output',
        help='path of sqlite database (default: output.sqlite)'
    )
    parser.add_argument(
        '--date-format',
        default='%Y-%m-%d',
        help='format string for dates in json data'
    )
    parser.add_argument(
        '--time-format',
        default='%H:%M:%S',
        help='format string for dates in json data'
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


def make_entry(json_item, time_format, date_format):
    uuid, entry_info = json_item

    date = datetime.strptime(entry_info['date'], date_format).date()
    time_in = datetime.strptime(entry_info['time_in'], time_format).time()

    if entry_info['time_out'] is not None:
        time_out = datetime.strptime(entry_info['time_out'], time_format).time()
    else:
        time_out = None

    user_id = entry_info['user_id']

    return Entry(
        uuid=uuid,
        date=date,
        time_in=time_in,
        time_out=time_out,
        user_id=user_id,
        user_type='student',
    )


def make_user(json_item, date_format):
    user_id, user_info = json_item

    if user_info['Date Joined'] is not None:
        date_joined = datetime.strptime(
                user_info['Date Joined'],
                date_format).date()
    else:
        date_joined = None

    if user_info['Date Left'] is not None:
        date_left = datetime.strptime(
                user_info['Date Joined'],
                date_format).date()
    else:
        date_left = None

    education_plan = user_info['Education Plan']
    school_email = user_info['School Email']
    personal_email = user_info['Personal Email']
    first_name = user_info['First Name']
    last_name = user_info['Last Name']
    major = user_info['Major']

    return User(
        user_id=user_id,
        date_joined=date_joined,
        date_left=date_left,
        education_plan=education_plan,
        school_email=school_email,
        personal_email=personal_email,
        first_name=first_name,
        last_name=last_name,
        major=major,
    )


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

    JSON_FILES = [pathlib.Path(f) for f in args.files]

    if args.output:
        DATABASE_FILE = args.output
    else:
        DATABASE_FILE = 'output.sqlite'

    engine = create_engine('sqlite:///{}'.format(DATABASE_FILE))
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    TYPE = args.type
    DATE_FORMAT = args.date_format
    TIME_FORMAT = args.time_format

    session = Session()
    for json_file in JSON_FILES:
        try:
            with json_file.open('r') as f:
                data = json.load(f)

                for json_item in data.items():
                    if TYPE == 'timesheet':
                        db_item = make_entry(json_item, TIME_FORMAT, DATE_FORMAT)
                        logging.debug('Adding timesheet entry:\n\t{}'.format(
                            db_item))
                    elif TYPE == 'users':
                        db_item = make_user(json_item, DATE_FORMAT)
                        logging.debug('Adding user:\n\t{}'.format(db_item))

                    session.add(db_item)
                    logging.debug('session.add(db_item)')

        except FileNotFoundError as e:
            logging.error('File not found: {}'.format(json_file))
            logging.debug(e)
            logging.info('Cancelling. No data commited to database.')
            raise SystemExit

        except KeyError as e:
            logging.error("Invalid json data for type '{}' in {}".format(
                TYPE, json_file))
            logging.debug(e)
            logging.info('Cancelling. No data commited to database.')
            raise SystemExit

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
