from pathlib import Path

from matplotlib import pyplot


def apply_basic_style() -> None:
    pyplot.style.use(f"{Path(__file__).parent}/basic.mplstyle")
