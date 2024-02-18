# -*- coding: UTF-8 -*-
#######################################
# CBS Service
#######################################
#
# Principle: https://www.cbs.nl/
# Library: cbsodata (https://github.com/J535D165/cbsodata)
# Author: Rik Heijmann
#

from logger import log
import modin.pandas as pandas
import cbsodata

####################
# General
####################
def list_tables():
    print(pandas.DataFrame(cbsodata.get_table_list()))

####################
# Extract
####################
def get_data(identifier):
    return pandas.DataFrame(cbsodata.get_data(identifier))

####################
# Transform
####################
def translate_datetime_ym(df, column):
    # In some cases date-times are being stored using the a Dutch date notation (2022 April). This function translates the dutch notation to a simple: Y-M notation. Wich will be interpreted by Pandas as a datetime notation.
    replace_with = {' (J|j)anuar(y|i)': '-1', ' (F|f)ebruar(y|i)': '-2', ' (M|m)a(rch|art)': '-3', ' (A|a)pril': '-4', ' (M|m)(ay|ei)': '-5', ' (J|j)un(e|i)': '-6', ' (J|j)ul(y|i)': '-7', ' (A|a)ugustus': '-8', ' (S|s)eptember': '-9', ' (O|o)(c|k)tober': '-10', ' (N|n)ovember': '-11', ' (D|d)ecember': '-12', '*': ''}
    for key in replace_with:
        df[column] = df[column].str.replace(key, replace_with[key], regex=True).astype(str)

    df[column] = pandas.to_datetime(df[column], format='%Y-%m')
    df = df.rename(columns=column: 'Date'})
