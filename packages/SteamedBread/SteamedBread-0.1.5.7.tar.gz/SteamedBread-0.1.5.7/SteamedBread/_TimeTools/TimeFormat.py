"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: TimeFormat.py
@Time: 2023/12/9 18:00
"""

import calendar
import time
from datetime import datetime

from dateutil import parser


class TimeFormat:
    def __init__(self, dt=None):
        dt = dt or time.time()
        if isinstance(dt, datetime):
            self.date = datetime
        elif isinstance(dt, float):
            self.date = datetime.fromtimestamp(dt)
        elif isinstance(dt, str):
            self.date = parser.parse(timestr=dt)

    @staticmethod
    def flash_back(days=1, month=0, weeks=0, years=0) -> datetime:
        """
        时间回溯器、时光穿越机
        :param days: 回溯 < 0, 穿越 > 0
        :param month: 回溯 < 0, 穿越 > 0
        :param weeks: 回溯 < 0, 穿越 > 0
        :param years: 回溯 < 0, 穿越 > 0
        :return: datetime
        """
        future = 0
        if days:
            future += days * 86400
        if month:
            today = datetime.today()
            month_range = calendar.monthrange(today.year, today.month)[1]
            future += month * month_range * 86400
        if weeks:
            future += weeks * 7 * 86400
        if years:
            future += years * 365 * 86400
        return datetime.fromtimestamp(int(str(int(future + time.time()))[:10]))
