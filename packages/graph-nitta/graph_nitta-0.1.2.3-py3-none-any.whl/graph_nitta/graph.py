import math
from typing import List, Optional, Tuple

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from graph_nitta.style.apply import apply_basic_style


def calc_grid(number_of_subplots: int) -> int:
    return math.ceil(math.sqrt(number_of_subplots))


def add_alphabet_to_axes(axes: List[Axes]) -> None:
    for i, ax in enumerate(axes):
        ax.text(
            x=0.07,
            y=0.94,
            ha="center",
            va="center",
            s=f"({chr(97 + i)})",
            fontsize=30,
            transform=ax.transAxes,
        )


def make_graph(
    number_of_subplots: int = 1,
    row: Optional[int] = None,
    column: Optional[int] = None,
    wspace: float = 0.7,
    hspace: float = 0.3,
    is_visible_id: bool = True,
) -> Tuple[Figure, List[Axes]]:
    apply_basic_style()
    fig = plt.figure()
    grid = calc_grid(number_of_subplots)
    row = row or grid
    column = column or grid

    width = 8 * column + (wspace * 10) * (column - 1)
    height = 8 * row + (hspace * 10) * (row - 1)

    fig.set_size_inches(width, height)
    fig.subplots_adjust(wspace=wspace, hspace=hspace)
    axes = [fig.add_subplot(row, column, i + 1) for i in range(number_of_subplots)]

    if number_of_subplots > 1 and is_visible_id:
        add_alphabet_to_axes(axes)
    return fig, axes
