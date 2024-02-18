# -*- coding: UTF-8 -*-
#######################################
# XML File
#######################################
#
# Principle: https://en.wikipedia.org/wiki/XML
# Library: pandas (https://github.com/pandas-dev/pandas)
# Author: Rik Heijmann
#

from logger import log
import modin.pandas as pandas
import lxml


####################
# Extract
####################
def get_data(file, stylesheet=""):
    return pandas.read_xml(file, stylesheer="")