#!/usr/bin/env python
# coding:utf-8
import os
import sys
import ctypes
import tempfile
from setuptools import find_packages, setup
from setuptools.command.install import install

# readme.md
# with open(r"T:\New_PC\Import_Project\uploads\pyipcore_upload\readme.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setup(
    name='pyipcore',
    version='0.4.3',
    description='(PyQt5 based) Create "Ipcore" from verilog(Need iverilog). Provide "Param Value" and "Port Control" function. This kind of IpCore is not safe, only for convenience',
    # long_description=long_description,
    author_email='2229066748@qq.com',
    maintainer="Eagle'sBaby",
    maintainer_email='2229066748@qq.com',
    # homepage="
    packages=find_packages(),
    license='Apache Licence 2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
    ],
    keywords=['verilog', 'ipcore', "pyqt5"],
    python_requires='>=3',
    install_requires=[
        "PyQt5",
        "reft==0.1.0",
        "pyverilog==1.3.0",
        "rbpop==0.1.2",
        "files3>=0.6",
    ],
    # CMD: ipc_ui -> cmd_ipc_ui
    entry_points={
        'console_scripts': [
            'ipc_ui=pyipcore:cmd_ipc_ui',
        ]
    },
)
