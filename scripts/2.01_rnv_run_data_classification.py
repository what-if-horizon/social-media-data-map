
import pandas as pd
from src.inference import dataClassification as dC
from datetime import datetime
from pathlib import Path
import os
import re

#input_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/005_merged_structures'
input_file = Path(os.environ["INPUT_FILE"])
output_dir = '/projects/prjs2007/data_donation/ddd_processed/02_path_classification/021_classified_paths'
#output_dir = '/projects/prjs2007/data_donation/ddd_development_2files/02_path_classification/021_classified_paths'


country_list =  ['ES', 'NL']
data_tax_1 = 'schneider2010'
data_tax_2 = 'wu2010'
data_tax_3 = 'verduyn2020'

model = os.environ["MODEL_CONFIG"]
model = re.sub(r'\.yaml', '', model)
num_agents = re.search(r'_(\d+)agent', model).group(1)
#model = 'gpt-oss-20b'
#model = 'Qwen3.8-27B'
#model = 'gpt-oss-120b'

print('START ', datetime.now())

def main():
    dC.run_classification(input_file, output_dir, data_tax_3, country_list, model, num_agents)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())