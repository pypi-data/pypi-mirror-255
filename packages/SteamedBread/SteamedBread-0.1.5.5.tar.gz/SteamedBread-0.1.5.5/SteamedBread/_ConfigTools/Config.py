"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: Config.py
@Time: 2023/12/9 18:00
"""

import os
from configparser import ConfigParser
from pathlib import Path

from SteamedBread._FileTools.FileOperateFormat import FileOperate
from SteamedBread._LoggerTools.Logger import logger


class MyConfig:

    def __init__(self, config_path: str = ""):
        self.cfg = ConfigParser()
        self.cfg.read(filenames=config_path, encoding="utf-8")

    def get_section(self, key):
        return dict(self.cfg.items(key))


def _get_env():
    return os.environ.get("env")


def _set_env(env: str):
    return os.environ.setdefault("env", env)


def _read_ini(ini_path=None) -> dict:
    ph = os.path.join(os.path.dirname(__file__), "config.ini")
    if not ini_path and not os.path.exists(ph):
        return {
            "current_env": "test",
            "enable_envs": [
                "test",
                "tce",
                "online"
            ]
        }
    else:
        cp = MyConfig(ini_path or ph)
        return cp.get_section(key="environments")


class Environment:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, env_path=None):
        cur_path = None
        if isinstance(env_path, (str, Path)) and env_path:
            env_path = os.path.join(env_path)
            if not (env_path.endswith(".ini") or env_path.endswith(".config")):
                raise FileExistsError(f"i hope accept .ini or .config instead of {env_path.split('.')[-1]}")
            else:
                cur_path = os.path.join(os.path.dirname(__file__), "config.ini")
                if not os.path.exists(cur_path):
                    FileOperate.write_file(filename=cur_path, data=FileOperate.read_file(filename=env_path))
                    logger.info("相关环境配置写入默认配置当中, config.ini自此生效")
                if FileOperate.read_file(filename=cur_path) != FileOperate.read_file(filename=env_path):
                    FileOperate.write_file(filename=cur_path, data=FileOperate.read_file(filename=env_path))
                    logger.info("配置文件有所改动, 已将改动点写入默认配置当中, config.ini自此生效")
        final_ini = _read_ini(ini_path=cur_path)
        self.current_env = final_ini["current_env"]
        self.enable_envs = final_ini["enable_envs"]
        if not _get_env():
            _set_env(self.current_env)
        if _get_env() not in self.enable_envs:
            raise EnvironmentError(f"当前运行环境不在可执行环境内: {self.enable_envs}")
        elif _get_env() != self.current_env:
            self.current_env = _get_env()
