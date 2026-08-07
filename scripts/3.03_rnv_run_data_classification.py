
import pandas as pd
from src.inference import dataClassification as dC
from datetime import datetime

project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'

input_file = f'{project_root}data/processed/full_paths.csv'
output_dir = f'{project_root}results/02_data_classification/'

country_list =  ['ES', 'NL', 'LT', 'RO']
data_tax = 'schneider2010'

print('START ', datetime.now())

def main():
    dC.run_classification(input_file, output_dir, data_tax, country_list)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())