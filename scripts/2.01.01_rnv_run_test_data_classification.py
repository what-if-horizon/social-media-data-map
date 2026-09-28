
import pandas as pd
from src.inference import dataClassification as dC
from datetime import datetime
from pathlib import Path
import os
import re


input_dir = Path('/projects/prjs2007/data_donation/ddd_annotation/sample/test')
output_dir = '/projects/prjs2007/data_donation/ddd_development_2files/02_path_classification/021_classified_paths'
output_dir = '/projects/prjs2007/data_donation/ddd_annotation/inference/02_path_classification/test'


country_list =  ['ES', 'NL']
data_tax_1 = 'schneider2010'
data_tax_2 = 'wu2010'
data_tax_3 = 'verduyn2020'


model = 'gpt-oss-20b'
#model = 'Qwen3.8-27B'
#model = 'gpt-oss-120b'

print('START ', datetime.now())

def main():
    dC.run_classification_seq(input_dir, output_dir, data_tax_3, country_list, model)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())