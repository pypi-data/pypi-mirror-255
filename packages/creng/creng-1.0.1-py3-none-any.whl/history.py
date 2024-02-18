#!/usr/bin/python3
import webbrowser
import plotly.graph_objects as go
import subprocess
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from libs.common import json_open, path
from libs.newdate import HistoryWrite

# パス
def main():
    filename = path("history.json")

    # 今日までのデータに更新
    history_write = HistoryWrite()
    history_write.history_renewal()

    # グラフのデータ用の配列の初期化
    date = []
    total = []

    # jsonファイルを開く
    json_data = json_open(filename)

    # jsonファイルのデータを配列に入れる、最終更新日の取得
    for key, value in json_data.items():
        date.append(key)
        total.append(value["total"])

    # グラフを描画
    fig = make_subplots(rows=1, cols=1)

    fig.add_trace(go.Scatter(x=date, y=total, mode='lines', name='単語学習グラフ'))

    # レイアウトの設定
    fig.update_layout(title='学んだ単語の数',
                    xaxis_title='日付',
                    yaxis_title='単語数')
    
    fig.update_yaxes(range=(0, value["total"]+10))

    # グラフをhtml化
    fig_path = path("fig.html", "fig")
    fig.write_html(fig_path)
    try:
        subprocess.call(["open", fig_path])
    except:
        webbrowser.open_new_tab(fig_path)