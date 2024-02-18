"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: FileOperateFormat.py
@Time: 2023/12/9 18:00
"""

import json
from typing import Union

import pandas
import yaml


class FileOperate:

    @staticmethod
    def _is_json_serializable(data: str):
        """
        判断一个对象 是否能够json格式化
        :param data: 字符串
        :return: bool
        """
        try:
            json.loads(data)
            return True
        except Exception as e:
            return False and e

    @staticmethod
    def _is_yaml_serializable(data: str):
        """
        判断一个对象 是否能够yaml格式化
        :param data: 字符串
        :return: bool
        """
        try:
            yaml.safe_load(data)
            return True
        except Exception as e:
            return False and e

    @staticmethod
    def read_excel(filename, sheet_name='sheet1'):
        """
            读取Excel文件内容
        :param filename: filename: Excel文件名称
        :param sheet_name: Excel文件sheet表名
        :return: excel.to_dict(orient="list") or excel.to_dict(orient="dict")
        """
        excel = pandas.read_excel(filename, sheet_name=sheet_name, engine='openpyxl')
        return excel

    @staticmethod
    def write_excel(data: dict, filename, sheet_name='sheet1'):
        """
            写入Excel文件内容
        :param data: {"a": [1, 2, 3], "b": [4, 5, 6]}
        :param filename: Excel文件名称
        :param sheet_name: Excel文件sheet表名
        :return: None
        """
        df1 = pandas.DataFrame(data)
        df1.to_excel(filename, sheet_name=sheet_name, index=False, engine='openpyxl')
        print(f"✅ excel: {filename} 写入完成")

    @staticmethod
    def read_file(filename: str = '', key: str = None, encoding: str = "utf-8", jsonify=False, yamlify=False):
        """
        读取文件, 若文件内容可以json格式化、yaml格式化 则返回dict, 反之返回字符串
        :param filename: 文件名称
        :param key: 键值
        :param encoding: 编码
        :param jsonify: json格式化开关
        :param yamlify: yaml格式化开关
        :return: dict or str
        """
        with open(file=filename, mode='r', encoding=encoding) as f:
            _data = f.read()

        if len(_data) >= 1:
            if FileOperate._is_json_serializable(data=_data) and jsonify:
                js = json.loads(_data)
                return js[key] if key else js
        if FileOperate._is_yaml_serializable(data=_data) and yamlify:
            y = yaml.safe_load(_data)
            return y[key] if key else y

        return _data

    @staticmethod
    def write_file(filename: str, data: Union[list, dict, str], encoding: str = "utf-8"):
        """
        写入文件
        :param filename: 文件名称
        :param data: 内容
        :param encoding: 编码格式
        :return: None
        """
        if filename.endswith('json'):
            data = json.dumps(data, ensure_ascii=False)
        if filename.endswith('yaml'):
            data = yaml.dump(data)
        if isinstance(data, (list, dict)):
            data = json.dumps(data, ensure_ascii=False, indent=4)
        with open(file=filename, mode='w', encoding=encoding) as f:
            f.write(data)
        print(f"✅ 文件: {filename} 写入完成!")
