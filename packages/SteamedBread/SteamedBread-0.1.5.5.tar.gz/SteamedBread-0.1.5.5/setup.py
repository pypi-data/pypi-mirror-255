"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: setup.py
@Time: 2023/12/9 18:00
"""

from setuptools import setup, find_packages

setup(
    name="SteamedBread",
    author="馒头",
    author_email="neihanshenshou@163.com",
    long_description=open(file="README.md", encoding="utf-8", mode="r").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    version="0.1.5.5",
    description="馒头的第三方库",
    install_requires=[
        "allure-pytest==2.13.2",
        "colorama==0.4.6",
        "ddddocr==1.4.11",
        "func_timeout==4.3.5",
        "NumPy==1.23.5",
        "openpyxl==3.1.0",
        "pandas==2.2.0",
        "Pillow==9.5.0",
        "python-dateutil==2.8.2",
        "pytest==7.3.2",
        "pytest-ordering==0.6",
        "PyYAML==6.0",
        "requests==2.30.0",
        "retry==0.9.2",
        "selenium==4.4.3",
        "urllib3==1.26.12",
    ],
    license="MIT",
    platforms=["MacOS、Window"],
    fullname="馒头大人",
    url="https://github.com/neihanshenshou/SteamedBread"
)
