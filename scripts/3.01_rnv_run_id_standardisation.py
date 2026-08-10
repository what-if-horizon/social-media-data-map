
import pandas as pd
from src.inference import idStandardisation as iS
from datetime import datetime

project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'

input_file = f'{project_root}data/processed/inference_sample.csv'
output_dir = f'{project_root}data/processed/01_id_standardisation/'

country_list =  ['ES', 'NL', 'LT', 'RO']
print('START ', datetime.now())

def main():
    iS.run_id_std(input_file, output_dir, country_list)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())