
import pandas as pd
from src.inference import dataClassification as dC
from datetime import datetime

project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'

input_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/005_merged_structures'
output_dir = '/projects/prjs2007/data_donation/ddd_development_20rows/02_path_classification'

country_list =  ['ES', 'NL']
data_tax_1 = 'schneider2010'
data_tax_2 = 'wu2010'
data_tax_3 = 'verduyn2020'

model = 'gpt-oss-20b'
#model = 'Qwen3.8-27B'
#model = 'gpt-oss-120b'

print('START ', datetime.now())

def main():
    dC.run_classification(input_dir, output_dir, data_tax_3, country_list, model, sample = 20)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())