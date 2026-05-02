from PIL.Image import Image
from typing import Iterable
import matplotlib.pyplot as plt

from graphs.ax import plot_image_on_axes


def plot_win_pick(
    x: Iterable[float],
    y: Iterable[float],
    images: Iterable[Image],
    *,
    title: str,
    games: int | None = None,
    y_line: float = 40.0,
    x_line: float = 15.0,
    xlims: tuple[float, float] = (0.0, 80.0),
    ylims: tuple[float, float] = (0.0, 100.0),
    quadrants: tuple[str, str, str, str] = ("-X+Y", "+X+Y", "-X-Y", "+X-Y"),
) -> plt.Figure:
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

    plt.xlim(*xlims)
    plt.ylim(*ylims)
    # ax.scatter(x, y)
    plot_image_on_axes(ax, x, y, images, image_ratio=0.05)

    xmin, xmax, ymin, ymax = ax.axis()
    UNDERUSED = (x_line - abs(xmin)) / 2
    OVERUSED = ((xmax - x_line) / 2) + x_line
    MEH = (y_line - abs(ymin)) / 2
    GOOD = ((ymax - y_line) / 2) + y_line

    for text, x_, y_ in [
        (quadrants[0], UNDERUSED, GOOD),
        (quadrants[1], OVERUSED, GOOD),
        (quadrants[2], UNDERUSED, MEH),
        (quadrants[3], OVERUSED, MEH),
    ]:
        ax.text(
            x_,
            y_,
            text,
            va="center",
            ha="center",
            fontweight="bold",
            alpha=0.2,
        )
    fig.suptitle(title)
    fig.tight_layout()
    plt.axvline(x_line)
    plt.axhline(y_line)
    return fig
