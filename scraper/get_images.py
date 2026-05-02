import tqdm
import requests

from lib.storage import Sqlite
from lib.image import url_to_hash

driver = Sqlite(path="static/mlbb.example.sqlite")
res = driver.get_resource_links("hero").asdict()

for i in tqdm.tqdm(res["image"]):
    filename = url_to_hash(i)

    with open(f"asset/{filename}.png", "wb") as f:
        f.write(requests.get(i).content)
