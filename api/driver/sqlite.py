from pathlib import Path
import aiosqlite


class Sqlite:
    def __init__(self, path: Path):
        self.uri = "file:" + path.resolve().as_uri() + "?mode=rw"
        self.conn = aiosqlite.connect(path)

    async def __aenter__(self):
        await self.conn.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.conn.__aexit__(*args, **kwargs)
