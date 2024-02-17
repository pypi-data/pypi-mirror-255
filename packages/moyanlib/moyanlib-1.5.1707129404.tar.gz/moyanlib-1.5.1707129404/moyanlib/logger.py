import datetime as _dt
import os as _os
from . import Error as _Error


class Logger:
    # 日志类

    def __init__(self, log_dir="./", level="INFO"):
        # 初始化
        # log_dir:日志目录
        # level：日志级别
        self.log_dir = log_dir
        self.level = level

    def _write(self, msg):
        # 写入日志
        current_time = _dt.datetime.now()
        file_name = _os.path.join(
            self.log_dir, f'{current_time.strftime("%Y-%m-%d")}.log'
        )
        log_msg = f'[{current_time.strftime("%Y-%m-%d %H:%M:%S.%f")}] {msg}\n'
        try:
            with open(file_name, "a") as f:
                f.write(log_msg)
        except:
            raise _Error.PathError()
        print(log_msg.strip())

    def debug(self, msg):
        if self.level in ["DEBUG", "INFO"]:
            self._write(f"DEBUG - {msg}")

    def info(self, msg):
        if self.level in ["DEBUG", "INFO", "WARNING"]:
            self._write(f"INFO - {msg}")

    def warning(self, msg):
        if self.level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            self._write(f"WARNING - {msg}")

    def error(self, msg):
        if self.level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            self._write(f"ERROR - {msg}")

    def critical(self, msg):
        if self.level == "CRITICAL":
            self._write(f"CRITICAL - {msg}")
