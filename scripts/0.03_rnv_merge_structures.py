from pathlib import Path
import pandas as pd
from tqdm import tqdm
from datetime import datetime


input_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/003_individual_flattened_structures_unique'
output_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/005_merged_structures'



def merge_csv(input_dir, output_dir):
    input_dir = Path(input_dir)
    #output_dir = Path(output_dir)

    for platform_dir in input_dir.iterdir():
    
        csv_files = list(platform_dir.glob("*.csv"))
        combined_df = pd.DataFrame()
        existing_ids = set()
        output_file = f'{output_dir}/{platform_dir.name}_merged_structures.csv'

        for file in csv_files:
            df = pd.read_csv(file)

            # Keep only IDs that don't already exist
            df_new = df[~df["final_path"].isin(existing_ids)]

            if not df_new.empty:
                combined_df = pd.concat([combined_df, df_new], ignore_index=True)
                existing_ids.update(df_new["final_path"])

        combined_df.to_csv(output_file, index=False)


print('START ', datetime.now())

def main():
   #create_unique_paths(input_dir, output_dir)
   merge_csv(input_dir, output_dir)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())