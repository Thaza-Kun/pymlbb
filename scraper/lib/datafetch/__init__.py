from collections import defaultdict
from dataclasses import dataclass


@dataclass
class FetchResult:
    columns: list[str]
    values: list[tuple]

    def get(self, column: str) -> list:
        if column not in self.columns:
            return []
        return [v[self.columns.index(column)] for v in self.values]

    def asdict(self) -> dict:
        ret = defaultdict()
        for i, c in enumerate(self.columns):
            ret[c] = [v[i] for v in self.values]
        return ret
