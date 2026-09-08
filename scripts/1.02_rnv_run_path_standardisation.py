import pandas as pd
from src.inference import idStandardisation as iS
from datetime import datetime
import os

#project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'
#project_root =  os.environ["PWD"]

input_file = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/005_merged_structures'
output_dir = '/projects/prjs2007/data_donation/ddd_processed/01_path_standardisation/011_classified_paths'
id_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/004_largest_donation'

country_list =  ['ES', 'NL']
model = 'gpt-oss-20b'
#model = 'Qwen3.8-27B'
#model = 'gpt-oss-120b'


#print('START ', datetime.now())

def main():
    iS.run_id_std(input_file, output_dir, id_dir, country_list, model,  num_agents = 4)

if __name__ == "__main__":
    main()

#print('FINISH ', datetime.now())




 
        