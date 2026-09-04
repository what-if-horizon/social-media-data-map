
import pandas as pd
from src.inference import idStandardisation as iS
from datetime import datetime
import os

#project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'
project_root =  os.environ["PWD"]

input_file = f'{project_root}/data/processed/inference_sample.csv'
output_dir = f'{project_root}/data/processed/01_id_standardisation/'
#output_dir = f'{project_root}/data/test/01_id_standardisation/'

input_test_file = f'{project_root}data/processed/01_id_standardisation/std_ids_ES_NL_LT_RO.json'
output_dir_data = f'{project_root}data/processed/01_id_standardisation/'
output_dir_results = f'{project_root}results/01_id_standardisation/'
df_cats = f'{project_root}data/processed/inference_sample.csv'


country_list =  ['ES', 'NL', 'LT', 'RO']
print('START ', datetime.now())

def main():
    iS.run_id_std_for_testing(input_file, output_dir, country_list)
    iS.test_id_standardisation(input_test_file, output_dir_data, output_dir_results, df_cats, country_list)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())









