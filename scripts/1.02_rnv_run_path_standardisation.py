
from src.inference import idStandardisation as iS
from pathlib import Path
import os
import re

#project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'
#project_root =  os.environ["PWD"]

input_file = input_file = Path(os.environ["INPUT_FILE"])
#output_dir = '/projects/prjs2007/data_donation/ddd_processed/01_path_standardisation/011_classified_paths'
#output_dir = '/projects/prjs2007/data_donation/ddd_development/01_path_standardisation/011_classified_paths'
output_dir = '/projects/prjs2007/data_donation/ddd_development_2files/01_path_standardisation/011_classified_paths'
id_dir = '/projects/prjs2007/data_donation/ddd_processed/00_ingest/004_largest_donation'


country_list =  ['ES', 'NL']

model = os.environ["MODEL_CONFIG"]
model = re.sub(r'\.yaml', '', model)
num_agents = re.search(r'_(\d+)agent', model).group(1)
#model = 'gpt-oss-20b'
#model = 'Qwen3.8-27B'
#model = 'gpt-oss-120b'


#print('START ', datetime.now())

def main():
    iS.run_id_std(input_file, output_dir, id_dir, country_list, model, num_agents)

if __name__ == "__main__":
    main()

#print('FINISH ', datetime.now())




 
        