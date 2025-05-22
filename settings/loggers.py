import logging
from datetime import datetime

from pytz import timezone


# Class for formatter
class MoscowTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # formating datetime for moscow time
        record_time = datetime.fromtimestamp(record.created, tz=timezone("Europe/Moscow"))
        if datefmt:
            return record_time.strftime(datefmt)
        return record_time.isoformat()


# Логгер для APScheduler
scheduler_logger = logging.getLogger("apscheduler")
scheduler_logger.setLevel(logging.WARNING)
scheduler_file_handler = logging.FileHandler("logs/scheduler_logs.log", encoding="utf-8")
scheduler_file_handler.setFormatter(MoscowTimeFormatter(
    fmt="%(asctime)s - [%(levelname)s] %(message)s",
    datefmt='%H:%M:%S'
))
scheduler_logger.addHandler(scheduler_file_handler) 


# bot_logger = logging.getLogger("aiogram")
# bot_logger.setLevel(logging.INFO)
# bot_file_handler = logging.FileHandler("logs/bot.log", encoding="utf-8")
# bot_file_handler.setFormatter(MoscowTimeFormatter(
#     fmt="%(asctime)s - [%(levelname)s] %(message)s",
#     datefmt='%H:%M:%S'
# ))
# bot_logger.addHandler(bot_file_handler) 
