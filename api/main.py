from fastapi.responses import StreamingResponse
import io
from pathlib import Path
from typing import List, Annotated

from PIL import Image
from fastapi import FastAPI, Depends


from driver.sqlite import Sqlite

from resources.enums import fetch_heroes, Hero
from resources.matchups import fetch_matchup_winrate_for, Matchup
from resources.matchups import fetch_teamup_winrate_for, Teamup
from resources.normalizer import image_url_to_filename
from graphs.winrate_vs_x import plot_win_pick
from resources.infobox import fetch_info_for_hero_with_users, Infobox

app = FastAPI()


async def get_sqlite():
    engine = Sqlite(path=Path("/static/mlbb.sqlite"))
    async with engine as db:
        yield db


SqliteSession = Annotated[Sqlite, Depends(get_sqlite)]


@app.get("/list/heroes")
async def list_heroes(db: SqliteSession) -> List[Hero]:
    return await fetch_heroes(db, order_by="name")


@app.get("/user/{user}/{hero}")
async def get_user_hero_info(db: SqliteSession, user: str, hero: str) -> Infobox:
    return await fetch_info_for_hero_with_users(db, hero, [user])


HeroList = Annotated[List[Hero], Depends(list_heroes)]


@app.get("/matchup/{hero}")
async def get_matchup_for(
    driver: SqliteSession, heroes: HeroList, hero, min_matchup: int = 3
):
    hero_name_to_heroes = {h.name: h for h in heroes}
    matchup: list[Matchup] = await fetch_matchup_winrate_for(
        driver, hero, min_matchup=min_matchup
    )
    x = [m.matchup_rate for m in matchup]
    y = [m.win_delta for m in matchup]
    images = [
        Image.open(
            Path("/asset")
            / (image_url_to_filename(hero_name_to_heroes[m.against].image) + ".png")
        )
        for m in matchup
    ]
    fig = plot_win_pick(
        x,
        y,
        images,
        title="Win rate increase vs Matchup rate",
        ylims=(-100.0, 100.0),
        xlims=(0, 60.0),
        y_line=0,
    )
    fig.gca().set_xlabel(f"Matchup rate (%) (at least {min_matchup} matchups)")
    fig.gca().set_ylabel("Win rate increase from base win rate (%)")
    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png")
    buffer.seek(0)  # Reset pointer to the start

    return StreamingResponse(buffer, media_type="image/png")


@app.get("/teamup/{hero}")
async def get_teamups_for(
    driver: SqliteSession, heroes: HeroList, hero, min_matchup: int = 3
):
    hero_name_to_heroes = {h.name: h for h in heroes}
    matchup: list[Teamup] = await fetch_teamup_winrate_for(
        driver, hero, min_matchup=min_matchup
    )
    x = [m.teamup_rate for m in matchup]
    y = [m.win_delta for m in matchup]
    images = [
        Image.open(
            Path("/asset")
            / (image_url_to_filename(hero_name_to_heroes[m.teamup].image) + ".png")
        )
        for m in matchup
    ]
    fig = plot_win_pick(
        x,
        y,
        images,
        title="Win rate increase vs Teamup rate",
        ylims=(-100.0, 100.0),
        xlims=(0, 60.0),
        y_line=0,
    )
    fig.gca().set_xlabel(f"Teamup rate (%) (at least {min_matchup} matchups)")
    fig.gca().set_ylabel("Win rate increase from base win rate (%)")

    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png")
    buffer.seek(0)  # Reset pointer to the start

    return StreamingResponse(buffer, media_type="image/png")


@app.get("/")
async def root():
    return {"message": "Hello World"}
