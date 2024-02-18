"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: Singleton.py
@Time: 2023/12/9 18:00
"""


def singleton(cls):
    instance = dict()

    def inner(*args, **kwargs):
        if not instance.get(cls):
            obj = cls(*args, **kwargs)
            instance[cls] = obj
        else:
            obj = instance[cls]
        return obj

    return inner


class Singleton:
    def __init__(self, cls):
        self.cls = cls
        self.instance = {}

    def __call__(self, *args, **kwargs):
        if self.cls not in self.instance:
            self.instance[self.cls] = self.cls(*args, **kwargs)
        print(f"{self.cls.__name__} is instantiation")
        return self.instance[self.cls]
