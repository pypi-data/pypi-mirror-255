# graph-nitta

matplotlibをラップしたグラフライブラリです。

## Usage

```sh
pip install -U graph-nitta
```

```py
from graph_nitta import make_graph, apply_ax_config, AxConfig, SpineConfig

# グラフ作成
fig, axes = make_graph()

# グラフにデータを追加
axes[0].plot(df[df.columns[1]], df[df.columns[2]], label="sample1")
axes[0].plot(df[df.columns[1]] * 1.1, df[df.columns[2]] * 1.1, label="sample2")

# グラフの設定
config = AxConfig(x=SpineConfig(lim=(0, 5)), y=SpineConfig(lim=(0, 1)))
apply_ax_config(axes[0], config)


fig.show()
```

[example](https://github.com/nitta-lab-polymer/graph-nitta/tree/main/example)に使用例を置いています。
