from typing import Literal
from dataclasses import dataclass


from driver.sqlite import Sqlite


@dataclass
class Hero:
    hero_id: int
    name: str
    image: str
    image2: str


async def fetch_heroes(
    driver: Sqlite, *, order_by: Literal["hero_id"] | Literal["name"] | None = None
) -> list[Hero]:
    cursor = await driver.conn.execute(
        "SELECT hero_id, name, image, image2 from heroes"
        + (f" ORDER by {order_by}" if order_by is not None else "")
    )
    res = list()
    for hero_id, name, image, image2 in await cursor.fetchall():
        res.append(Hero(hero_id=hero_id, name=name, image=image, image2=image2))
    return res
