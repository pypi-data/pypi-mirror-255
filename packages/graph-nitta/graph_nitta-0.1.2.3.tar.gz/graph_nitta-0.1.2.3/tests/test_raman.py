from pathlib import Path

import pandas as pd
from graph_nitta import AxConfig, SpineConfig, apply_ax_config, make_graph
from matplotlib.testing.decorators import image_comparison


@image_comparison(baseline_images=["raman"], extensions=["png"], style="mpl20")
def test_raman():
    base_path = Path(__file__).parent.parent
    df = pd.read_csv(f"{base_path}/sample_data/raman.csv")

    # グラフ作成
    fig, axes = make_graph()

    # グラフにデータを追加
    axes[0].plot(df[df.columns[1]], df[df.columns[2]], label="sample1")

    # グラフの設定
    config = AxConfig(
        x=SpineConfig(label=df.columns[1], lim=(400, 1600)),
        y=SpineConfig(label=df.columns[2], visible=False, lim=(-1000, 15000)),
        is_visible_legend=False,
    )
    apply_ax_config(axes[0], config)
