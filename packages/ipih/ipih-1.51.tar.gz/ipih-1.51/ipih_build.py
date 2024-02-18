import ipih

from ipih import NAME, VERSION
from build_tools import build
from pih import A

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

build(
    NAME,
    "Smart import for PIH module",
    VERSION,
    None,
    [
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
