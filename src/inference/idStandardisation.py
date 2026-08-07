
from  src.inference import generateInference as gI
from src.inference import prompts as p

import pandas as pd
import json
from datetime import date



def run_id_std(input_file, output_dir, platform):
    df = pd.read_csv(input_file)
    df = df[df['platform'] == platform]
    cats = str(df['keepID'].values.tolist())
    print('CATS', cats)

    #df = df[:50]
    output_list = []
    for ix, row in df.iterrows():

        output = gI.generate_output(data_1 = row['final_path'], template = p.prompt_std_ids(), data_2=cats)
        print('OUTPUT', output)
        output = json.loads(output)
        #output = output[0]
        node = {"path": row['final_path'],
                "true_id": row['keepID']}
        
        node.update(output)
        output_list.append(node)
        #print(node)

    json_str = json.dumps(output_list, indent=2)
    with open(f'{output_dir}standardised_ids.json', "w") as f:
        f.write(json_str)
    
    
    



    

