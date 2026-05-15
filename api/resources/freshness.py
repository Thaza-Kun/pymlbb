from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass
from driver.sqlite import Sqlite


@dataclass
class DbFreshness:
    first_datetime: datetime
    last_datetime: datetime


async def fetch_db_freshness(driver: Sqlite) -> DbFreshness:
    res = defaultdict(int)
    cursor = await driver.conn.execute(
        " SELECT"
        "     min(ts) as first_timestamp,"
        "     max(ts) as last_timestamp"
        " FROM heroes_in_matches "
        " LIMIT 1"
    )
    if res := await cursor.fetchone():
        first_timestamp, last_timestamp = res
        first_datetime = datetime.fromtimestamp(first_timestamp)
        last_datetime = datetime.fromtimestamp(last_timestamp)
        return DbFreshness(first_datetime=first_datetime, last_datetime=last_datetime)
    raise ValueError()
