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
