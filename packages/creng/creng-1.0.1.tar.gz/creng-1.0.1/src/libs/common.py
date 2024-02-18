# 複数のファイルに共通する関数の定義
import wx
import json
import platform
from os.path import expanduser

system = platform.system()
if system == "Windows":
    enc = 'cp932'
else:
    enc = 'utf-8'

# jsonファイルの読み込み
def json_open(filename):
    with open(filename, "r", encoding=enc, errors='ignore') as json_file:
        return json.load(json_file)

# jsonファイルに書き込み
def json_write(filename, json_data):
    with open(filename, "w", encoding=enc, errors='ignore') as json_file:
        json.dump(json_data, json_file, indent=2, ensure_ascii=False)

# ファイルのパスを返す
def path(filename, dir="data"):
    home = expanduser("~")
    return home + "/.creng_data/" + dir + "/" + filename
# 指定したサイズのフォントを返す
def set_font(i):
    return wx.Font(i, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

# jsonファイルに単語と意味を追加する
def add_word(word, meaning, key, filename):
    json_data = json_open(filename)
    i = 2
    while key in json_data:
        key = word + str(i)
        i += 1
    new_word = {
                "word": word,
                "meaning": meaning,
                "correct": 0,
                "incorrect": 0
                }
    json_data[key] = new_word
    json_write(filename, json_data)