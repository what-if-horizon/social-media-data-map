
import json
from difflib import SequenceMatcher
import pandas as pd


project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'
input_file = f'{project_root}results/01_id_standardisation/standardised_ids.json'
output_file = f'{project_root}results/01_id_standardisation/standardised_ids_test.json'
df_cats = f'{project_root}data/processed/inference_sample.csv'





def test_classification(input_file, output_file, df_cats):
    df = pd.read_csv(df_cats)
    cats = str(df['keepID'].values.tolist())            

    with open(input_file, "r") as file:
        data = json.load(file)

    in_correct = 0
    correct = 0
    total = len(data)

    for d in data:
        estimated_id = d['estimated_id']
        true_id = d['true_id']
        if estimated_id != true_id:
            in_correct = in_correct +1
            # Calculating similarity ratio
            d['result'] = 'INCORRECT'
            d['sim_ratio'] = SequenceMatcher(None, true_id, estimated_id).ratio()

            if estimated_id in cats:
                d['present_in_list'] = 'True'
            else:
                d['present_in_list'] = 'False'

        else:
            correct = correct + 1
            d['result'] = 'CORRECT' 
    data = json.dumps(data, indent = 2)
    print(f'{correct}/{total} ({(100/total)*correct}%) CORRECT CASES')
    print(f'{in_correct}/{total} ({(100/total)*in_correct}%) INCORRECT CASES')
    with open(output_file, "w") as f:
        f.write(data)



def main():
    test_classification(input_file, output_file, df_cats)

if __name__ == "__main__":
    main()

 
        