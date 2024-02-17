# masking_utils.py
import pandas as pd
from cryptography.fernet import Fernet
import os
import csv
import json

def encryption_dataset(csv_file_path,decryption_key_location,encrypted_dataset_location,json_path):
    with open(json_path, 'r') as json_file:
        init_result =  json.load(json_file)
    dataset = pd.read_csv(csv_file_path)
    sensitive_columns = []
    masking_functions = {}
    sensitive_column = None
    masking_function = None
    decryption_key = None


    for column_info in init_result["content"]:
        if column_info["sensitivity"] == 1:
            column_name = column_info["columnName"]
            masking_function = column_info["function"]
            sensitive_columns.append(column_name)
            masking_functions[column_name] = masking_function
   




    if sensitive_columns:
        decryption_keys = {}
        decryption_keys = {column: Fernet.generate_key() for column in sensitive_columns}        
        for column in sensitive_columns:
            cipher_suite = Fernet(decryption_keys[column])
            new_column_name = f"{column}_encrypted"
            dataset[new_column_name] = dataset[column].apply(lambda x: cipher_suite.encrypt(x.encode()).decode())
            
            duplicate_mask = dataset[column_name].notna()
            duplicated_rows = dataset[duplicate_mask]
            duplicated_df = pd.concat([dataset, duplicated_rows], ignore_index=True)
        result_df = pd.concat([dataset, duplicated_df], ignore_index=True)
        #input part 
        decryption_keys_dir = decryption_key_location
        ####
        for column, key in decryption_keys.items():
            key_file_path = os.path.join(decryption_keys_dir, f"{column}_decryption_key.txt")
            with open(key_file_path, "wb") as key_file:
                key_file.write(key)
        decryption_keys_csv_path = os.path.join(decryption_keys_dir, "decryption_keys.csv")
        with open(decryption_keys_csv_path, "w", newline='') as csvfile:
            fieldnames = ['Column', 'DecryptionKey']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for column, key in decryption_keys.items():
                writer.writerow({'Column': column, 'DecryptionKey': key.decode()})
    
    
    #output path
    masked_encrypted_csv_path = encrypted_dataset_location  
    result_df.to_csv(masked_encrypted_csv_path, index=False)
    return masked_encrypted_csv_path






