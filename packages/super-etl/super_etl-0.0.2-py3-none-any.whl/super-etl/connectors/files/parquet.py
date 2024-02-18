# -*- coding: UTF-8 -*-
#######################################
# Parquet File
#######################################
#
# Principle: https://en.wikipedia.org/wiki/Apache_Parquet
# Library: pandas (https://github.com/pandas-dev/pandas)
# Author: Rik Heijmann
#

from logger import log
import modin.pandas as pandas
import pyarrow


####################
# Extract
####################
def get_data(file):
    return pandas.read_parquet(file, engine=pyarrow)