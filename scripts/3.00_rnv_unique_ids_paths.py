import pandas as pd
from pathlib import Path
from datetime import datetime, date
import ast
import re
import shutil
import os


input_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/002_merged_structures'
output_dir = '/projects/prjs2007/data_donation/ddd_processed/01_id_standardisation/010_unique_paths'

input_dir_unique_ids = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/002_individual_flattened_structures'
output_dir_unique_ids = '/projects/prjs2007/data_donation/ddd_processed/01_id_standardisation/011_unique_ids'

  
###################################################################
# CREATE DF WITH UNIQUE PATHS
###################################################################

def ensure_columns(df, fill_value=pd.NA):

    required_columns = ['json_name', 'path', 'file_path']
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = fill_value

    return df


def combine_list(df):

    df['final_path'] = None

    for ix, row in df.iterrows():
        if row['platform'] == 'Tiktok':
            final_path =  row['path']
            
            if isinstance(final_path, str):
                final_path = ast.literal_eval(final_path)
               
            
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

        #print(final_path)
        final_path = '/'.join(final_path)
        df.at[ix, 'final_path'] = final_path 
              
    
    return df

def unique_paths(df):
    df = df['final_path'].drop_duplicates()
    

def create_unique_paths(input_dir, output_dir):

    for csv_file in input_dir.glob("*.csv"):

        try:
            file_name =  csv_file.stem
            print(f'{datetime.now()} PROCESSING : {file_name}')


            match = re.match(r"^([^_]+)", file_name)
            platform = match.group(1)
            
            df = pd.read_csv(csv_file)
            print(f'{datetime.now()} READ CSV : {file_name}')
            

            df = combine_list(df)
            print(f'{datetime.now()} FINISH COMBINE LIST : {file_name}')

            
            df = ensure_columns(df)
            print(f'{datetime.now()} FINISH ENSURE COLUMNS: {file_name}')

            df = unique_paths(df)
            print(f'{datetime.now()} FINISH UNIQUE PATHS: {file_name}')

            df.to_csv(f'{output_dir}/{platform}_unique_paths.csv')

            print(f'DATASET CREATED for {platform} at {datetime.now()}')
          
            
        except Exception as e:
            print(f"Failed to load {csv_file}: {e}")



def get_unique_ids(input_dir, output_dir):

    for platform_dir in input_dir.iterdir():

        csv_files = [f for f in os.listdir(platform_dir) if f.endswith(".csv")]

        max_rows = -1
        largest_file = None

        for file in csv_files:
            path = os.path.join(platform_dir, file)
            df = pd.read_csv(path)

            if len(df) > max_rows:
                max_rows = len(df)
                largest_file = file

        print(f"Largest CSV: {largest_file}")
        print(f"Number of rows: {max_rows}")

        # Copy largest file
        source = os.path.join(platform_dir, largest_file)
        destination = output_dir / platform_dir.name

        destination.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source, destination / largest_file)




print('START ', datetime.now())

def main():
   create_unique_paths(input_dir, output_dir)
   get_unique_ids(input_dir_unique_ids, output_dir_unique_ids)



if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())



create_unique_paths(input_dir, output_dir)