from matplotlib.axes import Axes


def arrow(
    ax: Axes,
    x: tuple[float, float],
    y: tuple[float, float],
    text: str = "",
    color: str = "k",
    width: float = 3,
):
    # 矢印
    ax.annotate(
        "",
        xy=(x[1], y[1]),
        xytext=(x[0], y[1]),
        xycoords="axes fraction",
        arrowprops=dict(color=color, width=width),
    )

    # テキスト
    ax.text(
        (x[0] + x[1]) / 2,
        y[1],
        text,
        fontsize=20,
        horizontalalignment="center",
        verticalalignment="bottom",
        transform=ax.transAxes,
    )


def get_colors(
    start: tuple[float, float, float, float],
    end: tuple[float, float, float, float],
    number: int,
) -> list[tuple[float, float, float, float]]:
    """色を線形補間で生成する

    Args:
        start (tuple[float, float, float, float]): 最初の色
        end (tuple[float, float, float, float]): 最後の色
        number (int): 分割数

    Returns:
        list[tuple[float, float, float, float]]: 色のリスト。RGBAの順
    """

    if number == 1:
        return [start]

    maps = [
        (
            start[0] + (end[0] - start[0]) * i / (number - 1),
            start[1] + (end[1] - start[1]) * i / (number - 1),
            start[2] + (end[2] - start[2]) * i / (number - 1),
            start[3] + (end[3] - start[3]) * i / (number - 1),
        )
        for i in range(number)
    ]

    return maps
