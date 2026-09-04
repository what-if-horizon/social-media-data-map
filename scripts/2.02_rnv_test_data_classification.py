
import pandas as pd
from src.inference import dataClassification as dC
from datetime import datetime

project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'

input_dir = f'{project_root}data/processed/02_data_classification/'
input_file_1 = f'{input_dir}schneider2010_ES_NL_LT_RO.json'
input_file_2 = f'{input_dir}wu2010_ES_NL_LT_RO.json'
output_dir_results = f'{project_root}results/02_data_classification/'

country_list =  ['ES', 'NL', 'LT', 'RO']


print('START ', datetime.now())

def main():
    dC.test_classification(input_file_1, input_dir, output_dir_results, country_list)
    dC.test_classification(input_file_2, input_dir, output_dir_results, country_list)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())