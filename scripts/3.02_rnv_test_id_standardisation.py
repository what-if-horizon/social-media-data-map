
import json
import pandas as pd
from src.inference import idStandardisation as iS


project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'
input_file = f'{project_root}data/processed/01_id_standardisation/std_ids_ES_NL_LT_RO.json'
output_dir_data = f'{project_root}data/processed/01_id_standardisation/'
output_dir_results = f'{project_root}results/01_id_standardisation/'
df_cats = f'{project_root}data/processed/inference_sample.csv'
country_list =  ['ES', 'NL', 'LT', 'RO']


def main():
    iS.test_id_standardisation(input_file, output_dir_data, output_dir_results, df_cats, country_list)

if __name__ == "__main__":
    main()

 
        