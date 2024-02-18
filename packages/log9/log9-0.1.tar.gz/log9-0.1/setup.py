from setuptools import setup, find_packages
import os


setup(
    name='log9',
    version='0.1',
    packages=find_packages(),
    py_modules=['log9'],
    install_requires=[
        'colorlog',  # 依赖项
    ],
    author='Tim-Saijun',
    author_email='c@zair.top',
    description='简单封装的彩色日志模块',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
