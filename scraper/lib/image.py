from PIL import Image
import hashlib

import numpy as np


def url_to_hash(url) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def read(file) -> np.ndarray:
    return np.array(Image.open(file))


if __name__ == "__main__":
    import matplotlib

    matplotlib.use("QtAgg")

    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    plt.imshow(Image.open("asset/93347fe77ad927bf39aaaef74af80e64.png"))
    plt.show()
