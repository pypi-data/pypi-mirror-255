from pathlib import Path

import pandas as pd
from graph_nitta import (
    AxConfig,
    Scale,
    SpineConfig,
    apply_ax_config,
    arrow,
    make_graph,
)
from matplotlib.axes import Axes
from matplotlib.testing.decorators import image_comparison


@image_comparison(baseline_images=["dma"], extensions=["png"], style="mpl20")
def test_dma():
    base_path = Path(__file__).parent.parent
    df = pd.read_csv(f"{base_path}/sample_data/dma.csv", index_col=0)

    # グラフ作成
    fig, axes = make_graph()
    ax2: Axes = axes[0].twinx()  # type: ignore
    axes.append(ax2)
    del ax2

    # グラフにデータを追加
    axes[0].scatter(
        df[df.columns[0]], df[df.columns[1]], label=df.columns[1], color="black"
    )
    axes[0].scatter(
        df[df.columns[0]], df[df.columns[2]], label=df.columns[2], color="red"
    )

    axes[1].scatter(  # type: ignore
        df[df.columns[0]], df[df.columns[3]], label=df.columns[3], color="blue"
    )

    # Configurations

    x_config = SpineConfig(label=df.columns[0], lim=(-150, 150), step=50)

    config_left = AxConfig(
        x=x_config,
        y=SpineConfig(
            label=df.columns[1][:-4] + " and " + df.columns[2],
            lim=(1e2, 1e10),
            scale=Scale.LOG,
        ),
        is_visible_legend=False,
    )

    apply_ax_config(axes[0], config_left)

    config_right = AxConfig(
        x=x_config,
        y=SpineConfig(label=df.columns[3], lim=(0, 4), step=1),
        is_visible_legend=False,
    )

    apply_ax_config(axes[1], config_right)  # type: ignore

    # アノテーション
    arrow(axes[0], x=(0.6, 0.4), y=(0.9, 0.9), color="black")
    arrow(axes[0], x=(0.6, 0.4), y=(0.8, 0.8), color="red")
    arrow(axes[1], x=(0.4, 0.6), y=(0.4, 0.4), color="blue")

    fig.legend(bbox_to_anchor=(1, 1), loc="upper left")
