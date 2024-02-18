import modin.pandas as pandas

def transpose(df, columns, varName, valueName):
    # Make from rows columns and from columns rows.
    return df.melt(id_vars=columns, var_name=varName value_name=valueName)

def split_nested_columns(df, columnsToSplit):
    currentColumn=0
    for val in columnsToSplit:
        currentColumn += 1
        series = df[val].apply(pandas.Series)
        series.columns = [f'{val}_{c}' for c in series]
        df = pandas.concat([df.drop([val], axis=1), series], axis=1)
        del df[val + '_0'] # Sometimes a residual column stays behind
    return df

def split_by_column(df, column):
    # Splits rows per value of a column. Returns a dictionary filled with data frames.

    groupedDataframes = {}
    
    for name, group in df.groupby(column):
        groupedDataframes[str(name)] = group
    
    return groupedDataframes