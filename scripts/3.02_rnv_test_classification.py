
import json
from difflib import SequenceMatcher

project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'
input_file = f'{project_root}data/processed/classification_ids.json'



with open(input_file, "r") as file:
    data = json.load(file)


for d in data:
    estimated_id = d['estimated_id']
    true_id = d['true_id']
    if estimated_id != true_id:
        # Calculating similarity ratio
        d['result'] = 'INCORRECT'
        d['sim_ratio'] = SequenceMatcher(None, true_id, estimated_id).ratio()
    else:
      d['result'] = 'CORRECT' 

 
        