"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: __init__.py
@Time: 2023/12/9 18:00
"""

import os
import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from SteamedBread import logger

current_path = os.path.abspath(__file__)
BASE_DIR = os.path.abspath(os.path.dirname(current_path) + os.path.sep)


class Cfg:
    # 报告截图路径
    report_snapshot = "."


def compress_image(infile):
    """
    不改变图片尺寸压缩到指定大小
    """
    im = Image.open(infile)
    im.save(infile, quality=100)


def screenshots_name(describe=None):
    """
    生成截图的名称
    """
    case_path = os.environ.get('PYTEST_CURRENT_TEST')[:-7]
    this_case_name = case_path.split("/")[-1]
    now_time = int(round(time.time() * 1000))
    tmp_file_name = this_case_name + "::" + str(now_time) + ".jpg"
    print("\n")
    describe = "" if not describe else " => " + describe
    logger.info("截图 📷" + describe + " => " + tmp_file_name)
    snapshot_dir = Cfg.report_snapshot + "/"
    snapshot_name = "{path}{name}".format(path=snapshot_dir, name=tmp_file_name)
    return snapshot_name


def processing(image, text: str = "⊙", color: str = 'lightcyan', w=None, h=None, font_size=13):
    """
    点击截图增加水印
    """
    font_dir = os.path.join(BASE_DIR, "font/Songti.ttc")
    font = ImageFont.truetype(font_dir, font_size)
    if w is not None and h is not None:
        im1 = Image.open(image)
        w = w - font_size / 2
        h = h - font_size / 2 - 40
        draw = ImageDraw.Draw(im1)
        draw.text(xy=(w, h), text=text, fill=color, font=font)  # 设置文字位置/内容/颜色/字体
        ImageDraw.Draw(im1)  # Just draw it!
        im1.save(image)

    compress_image(image)
