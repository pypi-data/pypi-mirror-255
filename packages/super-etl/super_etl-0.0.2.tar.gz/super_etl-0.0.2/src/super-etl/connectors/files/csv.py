# -*- coding: UTF-8 -*-
#######################################
# CSV File
#######################################
#
# Principle: https://en.wikipedia.org/wiki/Comma-separated_values
# Library: pandas (https://github.com/pandas-dev/pandas)
# Author: Rik Heijmann
#

from logger import log
import modin.pandas as pandas


####################
# Extract
####################
def get_data(file, header="0", delimiter=";"):
    return pandas.read_csv(file, header=header, delimiter=delimiter, engine="c")

