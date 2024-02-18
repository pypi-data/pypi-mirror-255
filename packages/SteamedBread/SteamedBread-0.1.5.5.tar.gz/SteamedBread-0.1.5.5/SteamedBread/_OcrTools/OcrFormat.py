"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: OcrFormat.py
@Time: 2024/2/2 21:36
"""

from PIL import Image

from ddddocr import DdddOcr


class OcrFormat:

    @staticmethod
    def show_word(filename: str = "", img: Image = None, show=True):
        """
        识别动态变化的验证码(前端登录), 非GIF文件(准确度会稍微低一些)

        img: 如果使用该参数, 则这样传递 show_word(img=Image.open("file.png"))
        filename: 如果使用该参数, 则这样传递 show_word(filename="file.png")
        """
        if img:
            img_file = img
        elif filename:
            img_file = Image.open(filename)
        else:
            raise AttributeError("Please Use The Picture That Needs To Be Recognized.")
        ocr = DdddOcr(show_ad=False)
        if show:
            print(f"识别到的字符: {ocr}")
        res = ocr.classification(img_file)
        return res
