
import pandas as pd
from pathlib import Path
from datetime import datetime, date
import ast
import re
import shutil
import os
from tqdm import tqdm




input_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/003_individual_flattened_structures_unique'
output_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/004_largest_donation' 




def largest_donation(input_dir, output_dir):

    input_dir = Path(input_dir)
    for platform_dir in input_dir.iterdir():

        csv_files = list(platform_dir.glob("*.csv"))
        max_rows = -1
        largest_file = None

        platform = platform_dir.name
        print('CSV', csv_files)
               
        for file in tqdm(csv_files, desc=f"Processing {platform}"):
            print(file)
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
   #create_unique_paths(input_dir, output_dir)
   largest_donation(input_dir, output_dir)



if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())



#create_unique_paths(input_dir, output_dir)