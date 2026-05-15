from pathlib import Path
import sqlite3


class Sqlite:
    def __init__(self, path: Path, create: bool = False):
        self.path = path
        uri = path.resolve().as_uri() + f"?mode=rw{'c' if create else ''}"
        self.conn = sqlite3.connect(uri, uri=True)
        self.cursor = self.conn.cursor()
