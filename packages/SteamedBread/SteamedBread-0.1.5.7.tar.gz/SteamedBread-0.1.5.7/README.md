### 已有功能

```angular2html

✅ 提供指定元素组件 截图功能
✅ 提供UI自动化识别动态验证码功能
✅ 提供priority 优先级装饰器
✅ 新增http请求 日志打印开关
✅ UI驱动工具 - 提供持久态可复用的浏览器窗口
✅ 全局配置工具 - 支持读写ini类型文件、初始化运行环境
✅ 装饰器 - 数据驱动装饰、用例描述修饰器
✅ 邮件工具 - 支持企微邮箱、网易、QQ邮箱等
✅ 异常捕获器 - 支持捕获多种任意异常类型
✅ 期望结果判断 - 支持Equals、Contains等机制判断方法
✅ 文件操作工具 - 支持表格、Yaml、Json、文本等格式文件读写
✅ 日志工具 - 终端输出、文件记录等机制
✅ PO模式简易Api - 适用于Web、Wap端等UI元素定位
✅ 服务端请求方法 - 支持请求记录打印机制
✅ 单例模式 - 适用于运行环境初始化
✅ 时间格式化功能 - 时间回溯器、时光穿越机

```

```python
# version: 0.1.4.9 -- 识别图片动态验证码

import allure

from SteamedBread import Browser
from SteamedBread import Element
from SteamedBread import OcrFormat
from SteamedBread import Page
from SteamedBread import case_title


class QuotePage(Page):
    """
    古诗词网站 登录页面元素
    """
    example_url = "https://so.gushiwen.cn/user/login.aspx"
    img_code = Element(id_="imgCode", describe="动态验证码")


@case_title(title="识别动态验证码")
def test_ocr_dynamic_code():
    with allure.step("进入古诗词网站"):
        driver = Browser()
        page = QuotePage(driver=driver)
        page.open(page.example_url)

    with allure.step("截图 指定的组件"):
        img_name = "img_code.png"
        page.img_code.screenshots(filename=img_name)

    with allure.step("ocr 识别 截图中的验证码"):
        code = OcrFormat.show_word(filename=img_name)
        print(f"code: {code}")

```

```python
# version: 0.1.4.7 -- 使用示例

# 提供priority 优先级装饰器

# example 1.0: actual order is test_02 -> test_01
from SteamedBread import priority


@priority(order=2)
def test_01():
    pass


@priority(order=1)
def test_02():
    pass


# 优化http请求, 新增日志打印开关

# example 2.0:
from SteamedBread import get

get("https://www.baidu.com", print_log=False)
```

```python

# UI驱动工具 version: 0.1.3.9 -- 使用示例
from SteamedBread import Browser
from SteamedBread import Element
from SteamedBread import Page


class BaiDuPage(Page):
    example_url = "https://baidu.com"
    input_search = Element(id_="kw")


def test_chrome_browser():
    # browser_type 可以指定浏览器类型, 若不指定 默认就是Chrome
    driver = Browser(browser_type="chrome")
    page = BaiDuPage(driver=driver)
    page.open(page.example_url)
    page.input_search.send_keys("321")

```

