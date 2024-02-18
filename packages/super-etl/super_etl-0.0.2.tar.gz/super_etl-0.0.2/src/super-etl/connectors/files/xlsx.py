# -*- coding: UTF-8 -*-
#######################################
# Microsoft XLSX File
#######################################
#
# Principle: https://docs.microsoft.com/en-us/openspecs/office_standards/ms-xlsx/2c5dee00-eff2-4b22-92b6-0738acd4475e
# Library: pandas (https://github.com/pandas-dev/pandas)
# Author: Rik Heijmann
#

from logger import log
import modin.pandas as pandas
import openpyxl


####################
# Extract
####################
def get_data(file):
    return pandas.read_excel(file, engine=openpyxl)

