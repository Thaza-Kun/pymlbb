from urllib.parse import urlsplit
import pathlib
import argparse

# from get_img import res
import json
import requests

from haralyzer import HarParser

from lib.schema import MatchSummary, MatchResponse
from lib.storage import Sqlite

match_detail_url = "https://app.web.moontontech.com/actgateway/battlereport/matches/{match_id}?sid={season}"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser("pymlbb-scraper")
    parser.add_argument(
        "--http-header",
        type=pathlib.Path,
        default=pathlib.Path("static/header.txt"),
    )
    parser.add_argument(
        "--har-file",
        type=pathlib.Path,
        default=pathlib.Path("static/mlbb-academy.har"),
    )
    parser.add_argument(
        "--sqlite",
        type=pathlib.Path,
        default=pathlib.Path("static/mlbb.sqlite"),
    )
    return parser.parse_args()


def main(argument: argparse.Namespace):
    with open(argument.http_header, "r") as f:
        headers_txt = f.readlines()

    headers = {
        L.split(":", 1)[0]: L.split(":", 1)[1].strip() for L in headers_txt if ":" in L
    }
    har_parser = HarParser.from_file(argument.har_file)
    driver = Sqlite(path=argument.sqlite, create=True)

    t = 0
    for page in har_parser.pages:
        print(page)
        assert (
            urlsplit(page.url).hostname
            == urlsplit("https://app.web.moontontech.com").hostname
        ), (
            "Page not recognized. Please filter network domain by 'app.web.moontontech.com' "
            " before saving as HAR as it only works if only page_2 is in the HAR file"
        )
        for entry in page.entries:
            if entry.response.text == "":
                continue
            content = json.loads(entry.response.text)
            if content.get("data").get("sids") is not None:
                continue
            for i, d in enumerate(content.get("data").get("result")):
                s = MatchSummary(**d)
                match_id = s.bid
                response: requests.Response = requests.get(
                    match_detail_url.format(match_id=s.bid_s, season=s.sid),
                    headers=headers,
                )
                if response.status_code != 200:
                    print(f"{t}{i}", s.bid, response.status_code, response.reason)
                    continue
                print(f"{t}{i}", s.bid, response.status_code)
                data = MatchResponse(**json.loads(response.text)).data.result
                driver.cursor.execute(
                    "INSERT OR IGNORE INTO matches (match_id, match_id_str, season) VALUES (?, ?, ?);",
                    (match_id, str(match_id), s.sid),
                )
                driver.conn.commit()

                for r in data:
                    stmts = r.prepare_sqls_with_match_id(match_id)
                    for s in stmts:
                        driver.cursor.execute(*s)
                driver.conn.commit()
            t += 1


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
