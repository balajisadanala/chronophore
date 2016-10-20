#!/usr/bin/python3

# TODO(amin): remove or update this script

import argparse
import datetime as dt
import pathlib
import random
import uuid

from chronophore import model, utils


def gen_random_times(start, end):
    """Generate a series of datetime.time objects
    between a given start and end time, randomly
    incrementing between 0.5 and 10 minutes.
    """
    time = start

    while time < end:
        wait_seconds = random.randint(30, 600)
        delta = dt.timedelta(seconds=wait_seconds)
        yield time
        time += delta


def random_user_id(users):
    """A closure that returns unique random user ids
    from a set of Chronophore user data. It keeps track
    of which ids it's already chosen.
    """
    used_ids = []

    user_ids = [user_id for user_id in users.keys()]

    def unique_id():
        while True:
            user_id = random.choice(user_ids)
            if user_id not in used_ids:
                break
        used_ids.append(user_id)
        return user_id

    return unique_id


def generate_data(output_file, users_file):
    users = utils.get_users(users_file)
    rand_user = random_user_id(users)

    timesheet = model.Timesheet(data_file=output_file)

    start_time = dt.datetime.combine(dt.date.today(), dt.time(hour=13))
    end_time = start_time + dt.timedelta(hours=6)

    for sign_in_time in gen_random_times(start_time, end_time):
        duration = random.randint(30, 300)
        sign_out_time = sign_in_time + dt.timedelta(minutes=duration)
        if sign_out_time > end_time:
            sign_out_time = end_time
        user_id = rand_user()

        e = model.Entry(
            date=dt.datetime.strftime(sign_in_time, "%Y-%m-%d"),
            name=' '.join(utils.user_name(user_id, users)),
            time_in=dt.datetime.strftime(sign_in_time, "%H:%M:%S"),
            time_out=dt.datetime.strftime(sign_out_time, "%H:%M:%S"),
            user_id=user_id,
        )
        timesheet[str(uuid.uuid4())] = e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate simulated Chronophore json data."
    )
    parser.add_argument(
        'users',
        help="path of users.json"
    )
    parser.add_argument(
        '-o', '--output',
        help="path of json file to generate (default: $(date)_sample.json)"
    )
    args = parser.parse_args()

    if args.output:
        OUTPUT_FILE = pathlib.Path(args.output)
    else:
        today = dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d")
        OUTPUT_FILE = pathlib.Path('.', (today + '_sample.json'))

    USERS_FILE = pathlib.Path(args.users)

    generate_data(OUTPUT_FILE, USERS_FILE)
