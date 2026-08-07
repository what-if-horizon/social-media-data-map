
import pandas as pd
from src.inference import dataClassification as dC
from datetime import datetime

project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'

input_file = f'{project_root}data/processed/full_paths.csv'
output_dir = f'{project_root}data/processed/02_data_classification/'

country_list =  ['ES', 'NL', 'LT', 'RO']
data_tax_1 = 'schneider2010'
data_tax_2 = 'wu2010'

print('START ', datetime.now())

def main():
    dC.run_classification(input_file, output_dir, data_tax_1, country_list)
    dC.run_classification(input_file, output_dir, data_tax_2, country_list)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())