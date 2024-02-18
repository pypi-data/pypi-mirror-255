import os
import shutil
from setuptools import setup

import ipih

from ipih import NAME, VERSION

# for facade
# setuptools
# prettytable
# colorama
# protobuf
# grpcio (six)
# pyperclip
# win32com -> pywin32 (!!!)

# MC
# pywhatkit

# for orion
# myssql

# for log
# telegram_send

# for dc2
# docs:
# mailmerge (pip install docx-mailmerge)
# xlsxwriter
# xlrd
# python-barcode
# Pillow
# ad:
# pyad
# pywin32 (!!!)
# wmi
# transliterate

# for data storage
# pysos
# lmdbm

# for printer (dc2)
# pysnmp

# for polibase
# cx_Oracle

# for mobile helper
# paramiko

#########################################################################################################

folder: str = f"//pih/facade/dist/{NAME}"
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as error:
        print("Failed to delete %s. Reason: %s" % (file_path, error))

setup(
    name=NAME,
    version=VERSION,
    description="Smart import for PIH module",
    long_description_content_type="text/markdown",
    url="https://pacifichosp.com/",
    author="Nikita Karachentsev",
    author_email="it@pacifichosp.com",
    license="MIT",
    classifiers=[],
    packages=[NAME],
    include_package_data=True,
    install_requires=[
        "prettytable",
        "colorama",
        "grpcio",
        "protobuf",
        "requests",
        "transliterate",
        "psutil",
        "setuptools",
    ],
)
