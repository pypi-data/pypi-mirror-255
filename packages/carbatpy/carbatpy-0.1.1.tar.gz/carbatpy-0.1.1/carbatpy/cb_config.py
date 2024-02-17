# -*- coding: utf-8 -*-
"""
Some constants for carbatpy usage

Created on Sun Nov  5 16:01:02 2023

@author: atakan
"""

import os

_T_SURROUNDING = 288.15 # K
_P_SURROUNDING =1.013e5  # Pa
try:
    _RESULTS_DIR = os.environ['CARBATPY_RES_DIR']
except:
    try:
        _RESULTS_DIR = os.environ['TEMP']
    except:
        try:
            directory = os.getcwd()
            _RESULTS_DIR = directory + r"\\tests\\test_files"
        except Exception as no_file:
            print("Please set the envirionment variable: CARBATPY_RES_DIR !", no_file)