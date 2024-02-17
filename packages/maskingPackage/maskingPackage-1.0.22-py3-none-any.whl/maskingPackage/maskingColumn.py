def mask_column_with_function(pd_column, function):
    exec(function, globals())
    masked_column = pd_column.apply(maskInfo)
    return masked_column