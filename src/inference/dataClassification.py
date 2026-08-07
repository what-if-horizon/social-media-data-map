
from  src.inference import generateInference as gI
from src.inference import prompts as p

import pandas as pd
import json
from datetime import date



def run_classification(input_file, output_dir, data_tax, country_list):

    """
    data_tax: The data can be classified according to different data taxonomies
    - 'schneider2010': Schneier, B. (2010). A taxonomy of social networking data. IEEE Security & Privacy, 8(4), 88-88.
    - 'wu2010' : Wu, L., Majedi, M., Ghazinour, K., & Barker, K. (2010, March). Analysis of social networking privacy policies. In Proceedings of the 2010 EDBT/ICDT Workshops (pp. 1-5).
    

    country_list: list of countries included in the analysis (eg ['ES', 'NL']
        - 'ES' = Spain
        - 'NL' = Netherlands
        - 'LT' = Lituania
        - 'RO' = Romania
    
    """


    df = pd.read_csv(input_file)
    df = df[['final_path', 'platform']]
    df = df.drop_duplicates()
    
    results_dict = {}

    templates = {'schneider2010', p.prompt_dt_schneider_2010(),
                 'wu2010', p.prompt_dt_wu_2010()}
    
    template = templates[data_tax]

    country_str = '_'.join(country_list)
    output_file = f'{data_tax}_{country_str}'
    

    for platform in df["platform"].unique():

        df_filtered = df[df["platform"] == platform]
        output_list = []

        for _, row in df_filtered.iterrows():
    
            output = gI.generate_output(data_1 = row['final_path'], template = template)
            print('OUTPUT', output)
            output = json.loads(output)
            #output = output[0]
            node = {"path": row['final_path']}
            node.update(output)
            output_list.append(node)

        results_dict[platform] = output_list

        

    json_str = json.dumps(results_dict, indent=2)
    with open(f'{output_dir}/{output_file}.json', "w") as f:
        f.write(json_str)
    
    
    



    

