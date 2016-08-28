#!/usr/bin/python3

import argparse
import json
import pathlib
import random
from datetime import datetime


FIRST_NAMES = (
    "Alexander", "Angela", "Carol", "Carrie", "Connie", "David", "Deena",
    "Donald", "Dorothy", "Earl", "Edwin", "Eric", "Eva", "Fermin", "Florence",
    "Hazel", "Hildegard", "James", "Jennifer", "Jesse", "Johnnie", "Krystal",
    "Kyra", "Lori", "Mary", "Norma", "Paula", "Robert", "Roland", "Rosa",
    "Ruth", "Virgil"
)

LAST_NAMES = (
    "Baker", "Bowen", "Brown", "Buggs", "Burr", "Cyr", "Dagostino",
    "Daschofsky", "Escamilla", "Faulkner", "Fowler", "Hartzler",
    "Jensen", "King", "Kranz", "Lafayette", "Lott", "Mckenzie",
    "Moskal", "Muraoka", "Reich", "Rodriguez", "Roque", "Santos",
    "Springfield", "Sterling", "Stewart", "Swinney", "Tu", "Weisman",
    "White", "Wright"
)

MAX_UNIQUE_NAMES = len(FIRST_NAMES) * len(LAST_NAMES)

MAJORS = (
    "Biology",
    "Chemistry",
    "Computer Science",
    "Engineering",
    "Mathematics",
    "Physics",
)


def random_date(lower_year_bound, upper_year_bound):
    year = random.randint(lower_year_bound, upper_year_bound)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date = datetime(year, month, day)
    return date


def random_user_id():
    """A closure that returns unique random user ids
    in the format: 88xxxxxxx. It keeps track of which
    ids it's already chosen.
    """
    used_ids = []

    def unique_id():
        while True:
            user_id = random.randint(880000000, 889999999)
            if user_id not in used_ids:
                break
        used_ids.append(user_id)
        return user_id

    return unique_id


def random_name(firsts, lasts):
    """A closure that returns unique random names.
    It keeps track of which names it's already chosen.
    """
    used_names = []

    def unique_name():
        while True:
            first_name = random.choice(firsts)
            last_name = random.choice(lasts)
            name = (first_name, last_name)
            if name not in used_names:
                break
        used_names.append(name)
        return name

    return unique_name


def generate_users(num_users, output_file):
    if num_users > MAX_UNIQUE_NAMES:
        raise ValueError(
            (
                "Number of users to generate ({}) cannot exceed "
                "maximum possible unique user names ({})."
            ).format(num_users, MAX_UNIQUE_NAMES)
        )

    rand_name = random_name(FIRST_NAMES, LAST_NAMES)
    rand_id = random_user_id()

    users = {}

    for _ in range(num_users):
        user_id = rand_id()
        date_joined = random_date(2010, 2015)
        date_left = random_date(date_joined.year + 1, 2020)

        student = {}
        student['First Name'], student['Last Name'] = rand_name()
        student['Major'] = random.choice(MAJORS)
        student['Email'] = (
            student['Last Name']
            + "."
            + student['First Name']
            + "@"
            + random.choice(("hotmail", "gmail", "live", "yahoo"))
            + ".com"
        )
        student['Date Joined'] = datetime.strftime(date_joined, "%Y-%m-%d")
        student['Date Left'] = random.choice(
            (None, datetime.strftime(date_left, "%Y-%m-%d"))
        )
        student['Education Plan'] = random.choice((True, False))
        student['Forgot to sign in'] = random.choice((True, False))

        users[user_id] = student

    with output_file.open('w') as f:
        json.dump(users, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate simulated Chronophore user data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-o', '--output', default=pathlib.Path('.', 'users_sample.json'),
        help="path of json file to generate"
    )
    parser.add_argument(
        '-n', '--number_of_users', default=500,
        help="number of users to generate"
    )
    args = parser.parse_args()

    NUM_USERS = int(args.number_of_users)
    OUTPUT_FILE = pathlib.Path(args.output)

    generate_users(NUM_USERS, OUTPUT_FILE)
