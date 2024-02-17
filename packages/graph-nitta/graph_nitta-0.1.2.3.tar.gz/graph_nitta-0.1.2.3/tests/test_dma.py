from pathlib import Path

import pandas as pd
from graph_nitta import (
    AxConfig,
    Scale,
    SpineConfig,
    apply_ax_config,
    apply_y_config,
    make_graph,
)
from matplotlib.testing.decorators import image_comparison


@image_comparison(baseline_images=["dma"], extensions=["png"], style="mpl20")
def test_dma():
    base_path = Path(__file__).parent.parent
    df = pd.read_csv(f"{base_path}/sample_data/dma_result.csv")
    # グラフ作成
    fig, axes = make_graph()

    # グラフにデータを追加
    axes[0].scatter(df[df.columns[1]], df[df.columns[2]], label=df.columns[2])
    axes[0].scatter(df[df.columns[1]], df[df.columns[3]], label=df.columns[3])

    # 2軸目の設定
    ax2 = axes[0].twinx()
    ax2.scatter(df[df.columns[1]], df[df.columns[4]], label=df.columns[4], color="red")  # type: ignore

    config = AxConfig(
        x=SpineConfig(label=df.columns[1], lim=(-150, 150), step=50),
        y=SpineConfig(label=df.columns[2], lim=(1e3, 1e10), scale=Scale.LOG),
        is_visible_legend=False,
    )
    apply_ax_config(axes[0], config)

    apply_y_config(
        ax2,  # type: ignore
        SpineConfig(label=df.columns[2], lim=(1e-2, 1e3), scale=Scale.LOG),
    )
