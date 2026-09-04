import pandas as pd
from src.inference import idStandardisation as iS
from datetime import datetime
import os

#project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'
project_root =  os.environ["PWD"]

input_file = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/002_merged_structures'
output_dir = '/projects/prjs2007/data_donation/ddd_processed/01_id_standardisation/012_classified_ids'



df_cats = f'{project_root}data/processed/inference_sample.csv'


country_list =  ['ES', 'NL', 'LT', 'RO']


print('START ', datetime.now())

def main():
    iS.run_id_std(input_file, output_dir, country_list)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())




 
        