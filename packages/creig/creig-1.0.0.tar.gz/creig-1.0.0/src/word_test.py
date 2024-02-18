#!/usr/bin/python3
import random
import wx
import textwrap
import platform
from libs.common import json_open, json_write, path, set_font
from libs.newdate import HistoryWrite

# メインフレームクラス
class SampleFrame(wx.Frame):
    def __init__(self, parent, ID, title):
        system = platform.system()
        if system == "Windows":
            self.x = 600
            self.y = 400
            self.fontsize_ques = 30
            self.fontsize_ans = 12
        else:
            self.x = 800
            self.y = 600
            self.fontsize_ques = 40
            self.fontsize_ans = 20
        wx.Frame.__init__(self, parent, title=title, pos=(100, 100), size=(self.x, self.y))
        # jsonファイルのパス
        self.words_file = path("words.json")
        self.history_file = path("history.json")
        # hisotory.jsonの更新、今日の日付の取得
        history_write = HistoryWrite()
        history_write.history_renewal()
        self.today = history_write.return_today()
        # jsonファイルの読み込み
        self.words_data = json_open(self.words_file)
        self.history_data = json_open(self.history_file)
        # 出題された問題数
        self.count = 1
        # 正解の選択肢の番号
        self.correct = -1
        # xボタン押して終わったときの処理
        self.Bind(wx.EVT_CLOSE, self.xExit)
        self.__create_widget()
        self.__do_layout()
        self.__set_word()

    # Widgetを作成するメソッド
    def __create_widget(self):
        self.SetBackgroundColour((224, 224, 224))

        # 問題文テキスト
        self.ques = wx.StaticText(self, label="Push the Start Button", style=wx.TE_CENTER)
        self.ques.SetForegroundColour('#000000')
        self.ques.SetFont(set_font(self.fontsize_ques))

        # 開始ボタン
        self.advance = wx.Button(self, label="Start")
        self.advance.SetForegroundColour('#000000')
        self.advance.Bind(wx.EVT_BUTTON, self.advance_push)
        
        # 回答ボタン1
        self.ans1 = wx.Button(self, label="1")
        self.ans1.Bind(wx.EVT_BUTTON, self.judge)
        self.ans1.SetFont(set_font(self.fontsize_ans))
        self.ans1.SetForegroundColour('#000000')
        self.ans1.SetBackgroundColour('#FFFFFF')
        self.ans1.Disable()

        # 回答ボタン2
        self.ans2 = wx.Button(self, label="2")
        self.ans2.Bind(wx.EVT_BUTTON, self.judge)
        self.ans2.SetFont(set_font(self.fontsize_ans))
        self.ans2.SetForegroundColour('#000000')
        self.ans2.SetBackgroundColour('#FFFFFF')
        self.ans2.Disable()

        # 回答ボタン3
        self.ans3 = wx.Button(self, label="3")
        self.ans3.Bind(wx.EVT_BUTTON, self.judge)
        self.ans3.SetFont(set_font(self.fontsize_ans))
        self.ans3.SetForegroundColour('#000000')
        self.ans3.SetBackgroundColour('#FFFFFF')
        self.ans3.Disable()

        # 回答ボタン4
        self.ans4 = wx.Button(self, label="4")
        self.ans4.Bind(wx.EVT_BUTTON, self.judge)
        self.ans4.SetFont(set_font(self.fontsize_ans))
        self.ans4.SetForegroundColour('#000000')
        self.ans4.SetBackgroundColour('#FFFFFF')
        self.ans4.Disable()

    # レイアウトを設定するメソッド
    def __do_layout(self):
        # 全体のレイアウト
        layout_all = wx.FlexGridSizer(rows=3, cols=1, gap=(0, 0))
        layout_all.Add(self.ques, flag=wx.ALIGN_CENTER | wx.ALL, border=0)

        # 開始ボタンのレイアウト
        layout_all.Add(self.advance, flag=wx.ALIGN_CENTER | wx.ALL, border=0)

        # 回答ボタンのレイアウト
        layout = wx.GridSizer(rows=2, cols=2, gap=(5, 5))
        layout.Add(self.ans1, flag=wx.EXPAND | wx.ALL,   border=4)
        layout.Add(self.ans2, flag=wx.EXPAND | wx.ALL,  border=4)
        layout.Add(self.ans3, flag=wx.EXPAND | wx.ALL, border=4)
        layout.Add(self.ans4, flag=wx.EXPAND | wx.ALL,   border=4)
        layout_all.Add(layout, flag=wx.EXPAND | wx.ALL, border=0)

        # 位置調整
        layout_all.AddGrowableRow(0, 5)
        layout_all.AddGrowableRow(1, 1)
        layout_all.AddGrowableRow(2, 12)
        layout_all.AddGrowableCol(0, 1)

        # セット
        self.SetSizer(layout_all)

    # 単語の用意と出題確率の操作
    def __set_word(self):
        self.key_list = [] # keyを入れる配列
        self.word_list = {} # key:単語
        self.meaning_list = {} # key:意味
        #number = 0
        for key, value in self.words_data.items():
            # (間違えた回数/出題回数)*100 -> 間違えた割合(%)毎に出題回数を増やす
            # 0で割らないように+1
            # 正解数が0の場合は間違いの数に関わらず出題確率は一定
            # 正解数-誤答数が5以上の場合は出題確率を大幅に下げる
            prob = int( ( (value["incorrect"] + 1) / (value["correct"] + value["incorrect"] + 1) ) * 100)
            if value["correct"] - value["incorrect"] < 5:
                for i in range(0, prob):
                    self.key_list.append(key)
            else:
                self.key_list.append(key)
            self.word_list[key] = value["word"]
            self.meaning_list[key] = value["meaning"]
        '''
            number += 1
        if number < 4: # 登録済みの単語が4つ未満ならエラー
            self.errorExit("単語を4つ以上登録してください.")
        '''

    # advanceボタンを押したときの動作
    def advance_push(self, event):
        if event.GetEventObject().GetLabel() == "Start": # 出題開始
            self.advance.Disable()
            self.advance.SetLabel("Next")
            self.ans_available_check()
        elif event.GetEventObject().GetLabel() == "Next": # 次の出題
            self.advance.Disable()
            self.ans_available_check()
            if self.count >= 10: # 規定の問題数に達したらプログラム終了準備
                self.advance.SetLabel("Finish")
        else: # プログラム終了
            self.onExit()

        self.renewal()
        self.Layout()

    # 問題と選択肢の更新
    def renewal(self):
        self.key = random.choice(self.key_list)
        meaning = self.meaning_list[self.key]
        option = [meaning]
        i = 0
        while i < 3:
            word_dummy = random.choice(self.key_list)
            while self.word_list[self.key] == self.word_list[word_dummy]:
                word_dummy = random.choice(self.key_list)
            if self.meaning_list[word_dummy] != meaning:
                option.append(self.meaning_list[word_dummy])
                option = list(set(option))
                if i == len(option)-1:
                    i -= 1
                i += 1
        random.shuffle(option)
        for i in range(0, len(option)):
            if option[i] == meaning:
                self.correct = i
        self.ques.SetLabel(str(self.count) + ". " + self.word_list[self.key])
        self.ans1.SetLabel('\n'.join(textwrap.wrap(option[0], 13)))
        self.ans2.SetLabel('\n'.join(textwrap.wrap(option[1], 13)))
        self.ans3.SetLabel('\n'.join(textwrap.wrap(option[2], 13)))
        self.ans4.SetLabel('\n'.join(textwrap.wrap(option[3], 13)))
        option.clear()

    # 正否判定と終了判定を行う
    def judge(self, event):
        btn = event.GetEventObject()
        self.advance.Enable()
        self.ans_available_check(False)
        self.count += 1
        # meaningの最後尾に空白がある場合正しく判定されない
        if self.meaning_list[self.key] == btn.GetLabel().replace("\n", "").strip():
            btn.SetBackgroundColour('#1AFFFC')
            self.words_data[self.key]["correct"] += 1
            self.history_data[self.today]["total"] += 1
        else:
            btn.SetBackgroundColour('#FF9999')
            self.words_data[self.key]["incorrect"] += 1
            # 正解の選択肢のボタンの色を変更
            exec("self.ans{}.SetBackgroundColour('#1AFFFC')".format(self.correct+1))

    # 回答ボタンの操作可否
    def ans_available_check(self, check=True):
        if check:
            self.ans1.Enable()
            self.ans1.SetBackgroundColour('#FFFFFF')
            self.ans2.Enable()
            self.ans2.SetBackgroundColour('#FFFFFF')
            self.ans3.Enable()
            self.ans3.SetBackgroundColour('#FFFFFF')
            self.ans4.Enable()
            self.ans4.SetBackgroundColour('#FFFFFF')
        else:
            self.ans1.Disable()
            self.ans2.Disable()
            self.ans3.Disable()
            self.ans4.Disable()

    # プログラム中断
    def xExit(self, event):
        dlg = wx.MessageDialog(self, "解答データは保存されません。\nプログラムを終了しますか？", "確認", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Destroy()
        else:
            dlg.Destroy()

    # プログラム終了
    def onExit(self):
        json_write(self.words_file, self.words_data)
        json_write(self.history_file, self.history_data)
        finish = wx.MessageDialog(self, "Good!", "終了", wx.OK)
        finish.ShowModal()
        self.Destroy()

'''
    # エラーによる強制終了
    def errorExit(self, txt):
        error = wx.MessageDialog(self, txt, "エラー", wx.ICON_ERROR | wx.OK)
        error.ShowModal()
        self.Destroy()
'''
        

# アプリケーションクラス
class SampleApp(wx.App):
    def OnInit(self):
        frame = SampleFrame(None, -1, "Test")
        frame.Centre()
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

# メイン
#if __name__ == "__main__":
def main():
    app = SampleApp()
    app.MainLoop()

#main()