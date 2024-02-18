# -*- coding: UTF-8 -*-
#######################################
# JSON File
#######################################
#
# Principle: https://en.wikipedia.org/wiki/JSON
# Library: pandas (https://github.com/pandas-dev/pandas)
# Author: Rik Heijmann
#

from logger import log
import modin.pandas as pandas


####################
# Extract
####################
def get_data(file):
    return pandas.read_json(file)

# TODO: Does currently not support extracting nested fields.
