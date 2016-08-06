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


def generate_users(num_users):
    data_dir = pathlib.Path('.')
    file_name = 'users.json'
    data_file = data_dir.joinpath(file_name)

    users = {}

    for _ in range(num_users):
        user_id = random.randint(880000000, 889999999)
        date_joined = random_date(2010, 2015)
        date_left = random_date(date_joined.year + 1, 2020)

        student = {}
        student['First Name'] = random.choice(FIRST_NAMES)
        student['Last Name'] = random.choice(LAST_NAMES)
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

    with data_file.open('w') as f:
        json.dump(users, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    generate_users(500)
