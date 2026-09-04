from pathlib import Path
import pandas as pd
from tqdm import tqdm
import os

input_directory = Path("path/to/csvs")
output_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/003_individual_flattened_structures_unique'



def merge_csv(input_dir):
    input_dir = Path(input_dir)
    for platform_dir in input_dir.iterdir():
    
        csv_files = [f for f in os.listdir(platform_dir) if f.endswith(".csv")]
        combined_df = pd.DataFrame()
        existing_ids = set()
        output_file = f'{platform_dir.name}_merged_structures'

        for file in csv_files:
            df = pd.read_csv(file)

            # Keep only IDs that don't already exist
            df_new = df[~df["final_path"].isin(existing_ids)]

            if not df_new.empty:
                combined_df = pd.concat([combined_df, df_new], ignore_index=True)
                existing_ids.update(df_new["final_path"])

        combined_df.to_csv(output_file, index=False)