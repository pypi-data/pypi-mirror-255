from pathlib import Path

import pandas as pd
from graph_nitta import AxConfig, SpineConfig, apply_ax_config, make_graph
from matplotlib.testing.decorators import image_comparison


@image_comparison(baseline_images=["ir"], extensions=["png"], style="mpl20")
def test_ir():
    base_path = Path(__file__).parent.parent
    df = pd.read_csv(f"{base_path}/sample_data/ir_nicolet_waves.csv")

    # グラフ作成
    fig, axes = make_graph()

    # グラフにデータを追加
    axes[0].plot(df[df.columns[1]], df[df.columns[2]], label="sample1")

    # グラフの設定
    config = AxConfig(
        x=SpineConfig(label=df.columns[1], lim=(400, 4000)),
        y=SpineConfig(label=df.columns[2], visible=False),
    )
    apply_ax_config(axes[0], config)

    fig.show()
