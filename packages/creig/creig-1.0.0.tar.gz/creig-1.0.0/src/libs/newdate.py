from .common import json_open, json_write, path
import re
import datetime

class HistoryWrite:
    def __init__(self):
        self.filename = path("history.json")
        self.history_data = json_open(self.filename)
        self.today = datetime.date.today()

    def history_init(self):
        for i in range(-1, 1):
            recode_day = self.today - datetime.timedelta(days=-i)
            self.history_data[str(recode_day)] = {
                "total": 0
            }
        json_write(self.filename, self.history_data)

    # history.jsonを今日までのデータに更新し、今日の日付を返す
    def history_renewal(self):
        for key, value in self.history_data.items():
            pass
        
        ptn_year = '(\d+)-\d+-\d+'
        ptn_month = '\d+-(\d+)-\d+'
        ptn_day = '\d+-\d+-(\d+)'

        year = int(re.match(ptn_year, key).group(1))
        month = int(re.match(ptn_month, key).group(1))
        day = int(re.match(ptn_day, key).group(1))

        # 最終更新日を取得
        last_date = datetime.date(year, month, day)

        # 最終更新日と今日の日付の差を取得
        days_difference = abs((self.today - last_date).days)

        # 最終更新日から今日までのデータを入力
        for i in range(-days_difference+1, 1):
            record_day = self.today - datetime.timedelta(days=-i)
            self.history_data[str(record_day)] = {
                "total": value["total"]
            }

        # 更新内容をjsonファイルに書き込む
        json_write(self.filename, self.history_data)

    def return_today(self):
        return str(self.today)