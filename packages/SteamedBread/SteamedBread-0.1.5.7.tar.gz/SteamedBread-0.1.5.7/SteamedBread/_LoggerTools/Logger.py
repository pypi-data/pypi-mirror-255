"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: Logger.py
@Time: 2023/12/9 18:00
"""

import logging
import sys
from typing import Callable

from colorama import Fore, Style

__logger = logging.getLogger(__name__)


def _set_filename(filename=None) -> None:
    """
    设置日志存储目录
    :param filename: 日志存储目录
    :return: None
    """
    # 文件日志中打印 debug 级别的日志
    file_handler = logging.FileHandler(filename=filename)
    file_handler.setLevel(level=__Style.file_level)
    file_handler.setFormatter(fmt=logging.Formatter(fmt=__Style.file_format))
    # 拒绝添加重复句柄
    __logger.addHandler(hdlr=file_handler)


def _stream_setting():
    __logger.setLevel(logging.DEBUG)
    # 终端只打印 info 级别的日志
    __stream_handler = logging.StreamHandler(stream=sys.stdout)
    __stream_handler.setLevel(level=__Style.stream_level)
    __stream_handler.setFormatter(fmt=logging.Formatter(fmt=__Style.stream_format))
    # 拒绝添加重复句柄
    __logger.addHandler(hdlr=__stream_handler)
    __logger.setFilename = _set_filename


class __Style:
    _GREEN = Fore.GREEN
    _BLACK = Fore.BLACK
    _RED = Fore.RED
    _ORIGIN = Style.RESET_ALL
    _BOLD = Style.BRIGHT

    stream_format = (
        f'{_GREEN}%(asctime)s{_RED} %(filename)s{_BLACK} {_BOLD} | %(lineno)s | %(levelname)s | %(message)s {_ORIGIN}')
    stream_level = 'INFO'
    file_format = '%(asctime)s - %(funcName)s - %(lineno)s - %(message)s'
    file_level = 'DEBUG'


class Logger:
    _stream_setting()

    def __init__(self):
        self.setFilename: Callable[..., None] = _set_filename
        self.info: Callable[..., None] = logging.info
        self.debug: Callable[..., None] = logging.debug
        self.warning: Callable[..., None] = logging.warning
        self.error: Callable[..., None] = logging.error
        self.log: Callable[..., None] = logging.log
        self.add_handler: Callable[..., None] = ...
        self.setLevel: Callable[..., None] = logging.StreamHandler().setLevel


logger: Logger = __logger
