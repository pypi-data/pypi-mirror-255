"""
author: wang ying
created time: 
intro:  python38
file:
"""
import json,os,datetime


class DailyLogFileHandler:
    def __init__(self, base_path="logs/"):
        self.base_path = base_path
        self.current_date = None
        self.file_path = self.get_current_log_file()

    def get_current_log_file(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        if current_date != self.current_date:
            self.current_date = current_date
            file_path = os.path.join(self.base_path, f"{current_date}.log")
            return file_path
        return self.file_path

    def write(self, message):
        file_path = self.get_current_log_file()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(message)

    def close(self):
        pass  #