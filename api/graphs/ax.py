from PIL.Image import Image
from typing import Iterable
import matplotlib.pyplot as plt


def plot_image_on_axes(
    ax: plt.axes,
    x: Iterable[float],
    y: Iterable[float],
    image: Iterable[Image],
    *,
    image_ratio: float = 0.03,
):
    xmin, xmax, ymin, ymax = ax.axis()
    xmin = 0 if xmin >= 0 else xmin
    ymin = 0 if ymin >= 0 else ymin

    for x_, y_, img in zip(x, y, image):
        ax_inset = ax.inset_axes(
            [
                (x_ / (xmax - xmin)) - (image_ratio / 2),
                (((y_ + (ymax - ymin) * 0.5) if ymin < 0 else y_) / (ymax - ymin))
                - (image_ratio / 2),
                image_ratio,
                image_ratio,
            ]
        )
        ax_inset.imshow(img)
        ax_inset.axis("off")
