# 
from setuptools import setup, find_packages

def readme():
    with open("./README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
    return long_description

setup(
    name='xlsx2xlsm',
    version='1.6',
    packages=find_packages(),
    install_requires=[
        # 
    ],
    author='Zhui Cao',
    author_email='857330385@qq.com',
    description='This package is used to convert xlsx files to xlsm files and supports custom macros',
    long_description = readme(),
    long_description_content_type='text/markdown',
    license='',
    keywords = ["xlsx", "xlsx2xlsm", "xlsm", "xlsxtoxlsm", "xlsx-to-xlsm", "xlsx-xlsm"],
    url='https://github.com/caozhui/xlsx2xlsm'
)