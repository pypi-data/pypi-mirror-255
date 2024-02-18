#!/usr/bin/python3
import wx
import platform
from libs.common import json_open, json_write, path, set_font, add_word

class MyFrame(wx.Frame):
    def __init__(self, parent, ID, title):
        system = platform.system()
        if system == "Windows":
            self.x = 600
            self.y = 300
            self.fontsize_small = 12
            self.fontsize_big = 18
        else:
            self.x = 800
            self.y = 400
            self.fontsize_small = 20
            self.fontsize_big = 25
        wx.Frame.__init__(self, parent, title=title, pos=(100, 100), size=(self.x, self.y))
        # words.jsonのパス
        self.filename = path("words.json")
        # 変数の初期化
        self.select_word = ""
        self.tmpword = " " # 空白1つ
        self.flag = False
        # おまじない
        #self.Bind(wx.EVT_CLOSE, self.onExit)
        self.__create_widget()
        self.__do_layout()
        self.__set_word()
        #self.__set_combo()
        self.Show()

    def __create_widget(self):
        self.SetBackgroundColour((224, 224, 224))
        # コンボボックス
        self.combobox = wx.ComboBox(self, style=wx.CB_DROPDOWN | wx.CB_SORT)

        # 選択した英単語の意味を表示するボタン
        self.btn_show = wx.Button(self, -1, "show")
        self.btn_show.SetForegroundColour('#000000')
        self.btn_show.Bind(wx.EVT_BUTTON, self.push_show)

        # 選択した英単語を削除するボタン
        self.btn_delete = wx.Button(self, -1, "delete")
        self.btn_delete.SetForegroundColour('#000000')
        self.btn_delete.Bind(wx.EVT_BUTTON, self.push_delete)
        self.btn_delete.Disable()

        # 英単語の意味を表示するテキスト
        self.txt_meaning = wx.StaticText(self, -1, "", style=wx.TE_CENTER)
        self.txt_meaning.SetForegroundColour('#000000')
        self.txt_meaning.SetFont(set_font(self.fontsize_small))

        # 単語検索と単語入力を区切る線
        line = "─────────────────────────────────────────────────────────────"
        self.txt_line = wx.StaticText(self, -1, line, style=wx.TE_CENTER)
        self.txt_line.SetForegroundColour('#000000')

        # word入力の案内
        self.word = wx.StaticText(self, -1, "word", style=wx.TE_CENTER)
        self.word.SetForegroundColour('#000000')

        # wordを入力するためのテキストボックス
        self.txtCtrl_word = wx.TextCtrl(self, -1, size=(430, 25) )
        self.txtCtrl_word.SetForegroundColour('#000000')
        
        # meaning入力の案内
        self.meaning = wx.StaticText(self, -1, "meaning", style=wx.TE_CENTER)
        self.meaning.SetForegroundColour('#000000')

        # meaningを入力するためのテキストボックス
        self.txtCtrl_meaning = wx.TextCtrl(self, -1, size=(430, 25) )
        self.txtCtrl_meaning.SetForegroundColour('#000000')
        
        # 入力したwordとmeaningを追加するボタン
        self.btn_add = wx.Button(self, -1, "add")
        self.btn_add.SetForegroundColour('#000000')
        self.btn_add.Bind(wx.EVT_BUTTON, self.push_add)

        # 追加が成功したことを報告するためのテキスト
        self.txt_success = wx.StaticText(self, -1, "", style=wx.TE_CENTER)
        self.txt_success.SetForegroundColour('#0000FF')
        self.txt_success.SetFont(set_font(15))

    def __do_layout(self):
        # *.Add(部品、位置、余白入れる位置、余白px)
        # VERTICAL:縦, HORIZONTAL:横
        sizer_all = wx.BoxSizer(wx.VERTICAL)

        # コンボボックスとshowボタンの配置
        sizer_wl = wx.BoxSizer(wx.HORIZONTAL)
        sizer_wl.Add(self.combobox, flag=wx.ALIGN_CENTER | wx.TOP, border=10)
        sizer_wl.Add(self.btn_show, flag=wx.ALIGN_CENTER | wx.LEFT | wx.TOP, border=10)
        sizer_wl.Add(self.btn_delete, flag=wx.ALIGN_CENTER | wx.LEFT | wx.TOP, border=10)
        sizer_all.Add(sizer_wl, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=20)
        
        # 意味を表示するテキストの配置
        sizer_all.Add(self.txt_meaning, flag=wx.ALIGN_CENTER)

        # 単語検索と単語入力を区切る線の配置
        sizer_all.Add(self.txt_line, flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        # 単語入力用のテキストボックスの配置
        sizer_wd = wx.BoxSizer(wx.HORIZONTAL)
        sizer_wd.Add(self.word, flag=wx.ALIGN_CENTER)
        sizer_wd.Add(self.txtCtrl_word, flag=wx.ALIGN_CENTER | wx.LEFT, border=35)
        sizer_all.Add(sizer_wd, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        # 意味入力用のテキストボックスの配置
        sizer_mn = wx.BoxSizer(wx.HORIZONTAL)
        sizer_mn.Add(self.meaning, flag=wx.ALIGN_CENTER)
        sizer_mn.Add(self.txtCtrl_meaning, flag=wx.ALIGN_CENTER | wx.LEFT, border=10)
        sizer_all.Add(sizer_mn, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        # 単語追加成功報告テキストの配置
        sizer_all.Add(self.btn_add, flag=wx.ALIGN_CENTER)
        sizer_all.Add(self.txt_success, flag=wx.ALIGN_CENTER | wx.LEFT, border=10)

        # 配置の確定？
        self.SetSizer(sizer_all)

    # 単語リストと辞書型の意味リストを作成
    def __set_word(self):
        self.wordlist = [""]
        self.keylist ={"":""}
        self.meaninglist = {"": "Please enter a word"}
        # jsonファイルの読み込み
        json_data = json_open(self.filename)
        for key, value in json_data.items():
            self.wordlist.append(value["word"])
            self.keylist[key] = value["word"]
            self.meaninglist[key] = value["meaning"]
        self.wordlist = list(set(self.wordlist)) # 重複の削除
        for word in self.wordlist:
            self.combobox.Append(word)

    # showボタン押下時の処理
    def push_show(self, event):
        self.select_word = self.combobox.GetValue().strip()
        # 単語の意味を全てmultilistに格納
        if self.select_word != self.tmpword or self.flag:
            self.flag = False
            self.multilist = []
            for key, value in self.keylist.items():
                if value == self.select_word:
                    self.multilist.append(key)
            self.multi = len(self.multilist)-1
            self.tmpword = self.select_word
        # 存在しない単語が入力された時のエラー表示
        try:
            if len(self.meaninglist[self.multilist[self.multi]]) > 30:
                self.txt_meaning.SetFont(set_font(self.fontsize_small))
            else:
                self.txt_meaning.SetFont(set_font(self.fontsize_big))
            # 意味の表示
            self.txt_meaning.SetLabel(self.meaninglist[self.multilist[self.multi]])
            self.txt_meaning.SetForegroundColour('#000000')
            self.show_key = self.multilist[self.multi]
            # 意味の更新のための番号
            self.multi -= 1
            if self.multi < 0:
                self.multi = len(self.multilist)-1
            if self.show_key != "":
                self.btn_delete.Enable()
            else:
                self.btn_delete.Disable()
        except:
            self.txt_meaning.SetLabel("Unregistered word")
            self.txt_meaning.SetForegroundColour('#FF0000')
        # レイアウト整理
        self.Layout()

    # deleteボタン押下時の処理
    def push_delete(self, event):
        json_data = json_open(self.filename)
        if self.show_key in json_data:
            del json_data[self.show_key]
        json_write(self.filename, json_data)
        self.multilist.remove(self.show_key)
        self.multi = len(self.multilist)-1
        if len(self.multilist) < 1:
            self.combobox.SetStringSelection(self.select_word)
            self.combobox.Delete(self.combobox.GetSelection())
            self.combobox.SetValue('')
        self.txt_meaning.SetLabel("Deleted " + self.select_word + ": " + self.meaninglist[self.show_key])
        del self.keylist[self.show_key]
        del self.meaninglist[self.show_key]
        self.flag = True
        self.txt_meaning.SetFont(set_font(self.fontsize_small))
        self.txt_meaning.SetForegroundColour('#0000FF')
        self.btn_delete.Disable()
        self.Layout()

    # addボタン押下時の処理
    def push_add(self, event):
        json_data = json_open(self.filename)
        word = self.txtCtrl_word.GetValue().strip() #空白とか消す
        meaning = self.txtCtrl_meaning.GetValue().strip()
        key = word
        self.flag = True
        i = 2
        if word != "" and meaning != "": #テキストボックスが空白でなければ
            # 単語の追加
            while key in json_data:
                key = word + str(i)
                i += 1
            add_word(word, meaning, key, self.filename)
            # 配列への追加
            self.wordlist.append(word)
            self.keylist[key] = word
            self.meaninglist[key] = meaning
            # 成功時のメッセージ表示
            self.txt_success.SetForegroundColour('#0000FF')
            self.txt_success.SetLabel( "\"" + word + "\" " + "added.")
            # 単語をコンボボックスに追加、意味を紐づける
            if not word in self.combobox.GetItems():
                self.combobox.Append(word)
            # テキストボックスを空にする
            self.txtCtrl_word.Clear()
            self.txtCtrl_meaning.Clear()
        else: # エラーメッセージの表示
            self.txt_success.SetForegroundColour('#FF0000')
            self.txt_success.SetLabel("Enter a word and meaning.")
        # レイアウト整理
        self.Layout()

    # xボタン押下時の処理
    def onExit(self, event):
        dlg = wx.MessageDialog(self, "プログラムを終了しますか？", "確認", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Destroy()  # ウィンドウを破棄してプログラムを終了
        else:
            dlg.Destroy()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "Wordlist")
        frame.Centre()
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

#if __name__ == '__main__':
def main():
    app = MyApp()
    app.MainLoop()

#main()