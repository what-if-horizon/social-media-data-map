import pandas as pd
from pathlib import Path
from datetime import datetime, date
import ast
import re
import shutil
import os
from tqdm import tqdm

input_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/002_individual_flattened_structures'
output_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/003_individual_flattened_structures_unique'


  
###################################################################
# CREATE DF WITH UNIQUE PATHS
###################################################################

def ensure_columns(df, fill_value=pd.NA):

    required_columns = ['json_name', 'path', 'file_path']
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = fill_value

    return df


def combine_list(df, platform):

    df['final_path'] = None

    for ix, row in df.iterrows():
        if platform == 'tiktok':
            final_path =  row['path']
            
            if isinstance(final_path, str):
                final_path = ast.literal_eval(final_path)

            final_path = '/'.join(final_path)

           
            
        else:
            file_list = row['file_path'].split('/')
            path_list = row['path']
        
            if pd.isna(path_list):
                final_path = row['file_path']
               
            else:
                if isinstance(path_list, str):
                    path_list = ast.literal_eval(path_list)

                if isinstance(path_list, list):
                    final_path = file_list + path_list
                    path = '/'.join(path_list)
                    df.at[ix, 'path'] = path

                final_path = '/'.join(final_path)
        df.at[ix, 'final_path'] = final_path 
              
    
    return df


def clean_paths(df, platform):
    df["final_path"] = df["final_path"].str.replace(r'/\d{5,}(?=/)', '/$NUMBER', regex=True)

    if platform == 'facebook':
       df["final_path"] = df["final_path"].str.replace(r'(?<=/group_badges_v2/).*','$GROUPNAME',regex=True)

    if platform == 'tiktok':
        df["final_path"] = df["final_path"].str.replace(
                r'(?<=ChatHistory/Chat History with ).*?(?=:)',
                '$USERNAME',
                regex=True)
        
    if platform == 'youtube':
        #df = df[~df["final_path"].str.contains("/Google Photos/", case=False, na=False)]
        #df = df[~df["final_path"].str.contains("/Google Foto_s/", case=False, na=False)]
        df = df[df["final_path"].str.contains("Takeout/YouTube", case=False, na=False)]
        df["final_path"] = df["final_path"].str.replace(r'(?<=/kids/)[^/]+','$USERNAME',case=False, regex=True)

    return df


           
    

def unique_paths(df):
    df = df['final_path'].drop_duplicates()
    return df


def get_unique_ids(input_dir, output_dir):

    input_dir = Path(input_dir)
    for platform_dir in input_dir.iterdir():

        csv_files = list(platform_dir.glob("*.csv"))

        platform = platform_dir.name
        
        for file in tqdm(csv_files, desc=f"Processing {platform}"): 
            try:
                #print(file)
        
                path = os.path.join(platform_dir, file)
                df = pd.read_csv(path)

                df = combine_list(df, platform)
                #print(f'{datetime.now()} FINISH COMBINE LIST')

                
                df = ensure_columns(df)
                #print(f'{datetime.now()} FINISH ENSURE COLUMNS')
                
                df = clean_paths(df, platform)

                df = unique_paths(df)
                #print(f'{datetime.now()} FINISH UNIQUE PATHS')
            
                df.to_csv(f'{output_dir}/{platform}/{file.stem}.csv')

            except Exception as e:
                print(f"Failed to process {file}: {e}")


def main():
   #create_unique_paths(input_dir, output_dir)
   get_unique_ids(input_dir, output_dir)

if __name__ == "__main__":
    main()

           
