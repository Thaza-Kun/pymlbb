import pathlib
import argparse

from lib.storage import Sqlite


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser("pymlbb-scraper")
    parser.add_argument(
        "--sqlite",
        type=pathlib.Path,
        default=pathlib.Path("static/mlbb.sqlite"),
    )
    return parser.parse_args()


def main(argument: argparse.Namespace):
    driver = Sqlite(argument.sqlite)
    print("Reading `scraper/crud/init.sql`")
    with open("scraper/crud/init.sql", "r") as f:
        sqlstrs = f.read().split(";")

    for sqlstr in sqlstrs:
        driver.cursor.execute(sqlstr)
    driver.conn.commit()


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
