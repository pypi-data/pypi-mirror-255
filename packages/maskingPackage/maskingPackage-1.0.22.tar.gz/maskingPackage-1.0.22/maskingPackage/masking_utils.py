import json
import pandas as pd


def mask_column_with_function(pd_column, function):
    exec(function, globals())
    masked_column = pd_column.apply(maskInfo)
    return masked_column

def masking_all_column(encrypted_dataset,json_path):    
    with open(json_path, 'r') as json_file:
        init_result =  json.load(json_file)
    maskeddata = pd.read_csv(encrypted_dataset, low_memory=False)
    for col_info in init_result['content']:
            col_name = col_info['columnName']
            if col_info.get('sensitivity') == 1:
                # masked_df[col_name] = makeddata[col_name]
                print(f"Applying masking to sensitive column: {col_name}...")
                maskeddata[col_name] = mask_column_with_function(maskeddata[col_name], col_info['function'])            
            else:
                print(f"Skipping non-sensitive column: {col_name}")
                maskeddata[col_name]
    return maskeddata    

