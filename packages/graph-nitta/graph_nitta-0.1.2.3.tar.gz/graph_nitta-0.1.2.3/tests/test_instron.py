from pathlib import Path

import pandas as pd
from graph_nitta import AxConfig, SpineConfig, apply_ax_config, make_graph
from matplotlib.testing.decorators import image_comparison


@image_comparison(baseline_images=["instron"], extensions=["png"], style="mpl20")
def test_instron():
    base_path = Path(__file__).parent.parent
    df = pd.read_csv(f"{base_path}/sample_data/instron_stress_strain.csv")

    # グラフ作成
    fig, axes = make_graph()

    # グラフにデータを追加
    axes[0].plot(df[df.columns[1]], df[df.columns[2]], label="sample1")
    axes[0].plot(df[df.columns[1]] * 1.1, df[df.columns[2]] * 1.1, label="sample2")

    # グラフの設定
    config = AxConfig(
        x=SpineConfig(lim=(0, 15), step=3),
        y=SpineConfig(lim=(0, 4), step=1),
        is_visible_legend=False,
    )
    apply_ax_config(axes[0], config)
