#!/usr/bin/python3
import os
import wx
import json
import platform
from os.path import expanduser
from libs.common import json_open, json_write, set_font, path
from libs.newdate import HistoryWrite
import word_list
import word_test
import reading
import history

class SampleFrame(wx.Frame):
    def __init__(self, parent, id, title):
        self.system = platform.system()
        if self.system == "Windows":
            self.x = 450
            self.y = 500
            self.enc = 'cp932'
        else:
            self.x = 450
            self.y = 550
            self.enc = 'utf-8'
        wx.Frame.__init__(self, parent, title=title, pos=(100, 100), size=(self.x, self.y))
        self.home_directory = expanduser("~")
        self.flag = True
        self.Bind(wx.EVT_CLOSE, self.onExit)
        self.__create_widget()
        self.__do_layout()
        self.__data_setup()

    def __create_widget(self):
        self.SetBackgroundColour((224, 224, 224))

        self.txt = wx.StaticText(self, label = "Menu")
        self.txt.SetFont(set_font(40))
        self.txt.SetForegroundColour('#000000')

        self.btn_list = wx.Button(self, label="List")
        self.btn_list.Bind(wx.EVT_BUTTON, self.list)
        self.btn_list.SetForegroundColour('#000000')

        self.btn_test = wx.Button(self, label="Test")
        self.btn_test.Bind(wx.EVT_BUTTON, self.test)
        self.btn_test.SetForegroundColour('#000000')

        self.btn_reading = wx.Button(self, label="Reading")
        self.btn_reading.Bind(wx.EVT_BUTTON, self.reading)
        self.btn_reading.SetForegroundColour('#000000')

        self.btn_history = wx.Button(self, label="History")
        self.btn_history.Bind(wx.EVT_BUTTON, self.history)
        self.btn_history.SetForegroundColour('#000000')

        self.ctrl_apikey = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE, size=(220,100))
        self.ctrl_apikey.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        self.ctrl_apikey.Hide()

        self.btn_apikey = wx.Button(self, label="apikey")
        self.btn_apikey.Bind(wx.EVT_BUTTON, self.apikey)
        self.btn_apikey.SetForegroundColour('#000000')

        self.btn_save = wx.Button(self, label="save")
        self.btn_save.Bind(wx.EVT_BUTTON, self.save)
        self.btn_save.SetForegroundColour('#000000')
        self.btn_save.Hide()

    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_api = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.txt, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer.Add(self.btn_list, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer.Add(self.btn_test, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer.Add(self.btn_reading, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer.Add(self.btn_history, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer.Add(self.btn_apikey, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer_api.Add(self.ctrl_apikey, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer_api.Add(self.btn_save, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer.Add(sizer_api, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        self.SetSizer(sizer)

    def __data_setup(self):
        if not os.path.exists(self.home_directory + "/.creng_data"):
            home_dir = expanduser("~")
            data_dir = home_dir + "/.creng_data/data"
            fig_dir = home_dir + "/.creng_data/fig"
            api_dir = home_dir + "/.creng_data/api"
            res_json = data_dir + "/response.json"
            his_json = data_dir + "/history.json"
            word_json = data_dir + "/words.json"
            api_key = api_dir + "/apikey"
            os.makedirs(data_dir)
            os.makedirs(fig_dir)
            os.makedirs(api_dir)
            with open(res_json, "w", encoding=self.enc, errors='ignore') as file:
                json.dump({}, file, indent=2)
            with open(his_json, "w", encoding=self.enc, errors='ignore') as file:
                json.dump({}, file, indent=2)
            with open(word_json, "w", encoding=self.enc, errors='ignore') as file:
                json.dump({}, file, indent=2)
            with open(api_key, "w", encoding=self.enc, errors='ignore') as file:
                pass
            init = HistoryWrite()
            init.history_init()

    def list(self, event):
        #subprocess.Popen(["python3", "word_list.py"])
        word_list.main()

    def test(self, event):
        #subprocess.Popen(["python3", "word_test.py"])
        json_data = json_open(path("words.json"))
        wordlist = []
        for value in json_data.values():
            wordlist.append(value["word"])
        wordlist = list(set(wordlist))
        if len(wordlist) < 4: # 登録されている単語が4つ未満なら
            error = wx.MessageDialog(self, "単語を4つ以上登録してください.", "エラー", wx.ICON_ERROR | wx.OK)
            error.ShowModal()
        else:
            word_test.main()

    def reading(self, event):
        #subprocess.Popen(["python3", "reading.py"])
        with open(path("apikey", "api"), "r", encoding=self.enc, errors='ignore') as f:
            key = f.read().strip()
        if key == "": # APIキーが入力されていなければ
            error = wx.MessageDialog(self, "APIキーが登録されていません。", "エラー", wx.ICON_ERROR | wx.OK)
            error.ShowModal()
        else:
            reading.main()

    def history(self, event):
        #subprocess.Popen(["python3", "history.py"])
        history.main()

    def apikey(self, event):
        if self.flag:
            self.ctrl_apikey.Show()
            self.btn_save.Show()
            self.flag = False
        else:
            self.ctrl_apikey.Hide()
            self.btn_save.Hide()
            self.flag = True
        self.Layout()

    def save(self, event):
        dlg = wx.MessageDialog(self, "APIキーを更新しますか？", "確認", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            with open(path("apikey", "api"), "w", encoding=self.enc, errors='ignore') as f:
                f.write(self.ctrl_apikey.GetValue().strip())
            self.ctrl_apikey.Clear()
        else:
            dlg.Destroy()
        self.ctrl_apikey.Hide()
        self.btn_save.Hide()
        
    # xボタン押下時の処理
    def onExit(self, event):
        self.Destroy()
        exit()
        '''
        dlg = wx.MessageDialog(self, "プログラムを終了しますか？", "確認", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Destroy()  # ウィンドウを破棄してプログラムを終了
        else:
            dlg.Destroy()
        '''

# アプリケーションクラス
class SampleApp(wx.App):
    def OnInit(self):
        frame = SampleFrame(None, -1, "Title")
        frame.Centre()
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

def main():
    app = SampleApp()
    app.MainLoop()

#main()

# メイン
'''
if __name__ == "__main__":
    app = SampleApp()
    app.MainLoop()
'''