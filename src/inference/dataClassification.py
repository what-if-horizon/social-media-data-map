
from  src.inference import generateInference as gI
from src.inference import prompts as p

import pandas as pd
import json
from datetime import date
import random



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

    templates = {'schneider2010': p.prompt_dt_schneider_2010(),
                 'wu2010': p.prompt_dt_wu_2010()}
    
    template = templates[data_tax]

    country_str = '_'.join(country_list)
    output_file = f'{data_tax}_{country_str}'
    

    for platform in df["platform"].unique():

        df_filtered = df[df["platform"] == platform]
        ################################################
        #JUST FOR TESTING!!!!!!!
        ################################################
        random.seed(100)
        df_filtered = df_filtered.sample(n=5)
        ################################################
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



def test_classification(input_file, output_dir_data, output_dir_results, country_list):

    if 'schneider2010' in input_file:
        template = p.prompt_judge_dt_schneider_2010()
        file_name = 'schneider2010'

    if 'wu2010' in input_file:
        template = p.prompt_judge_dt_wu_2010()
        file_name = 'wu2010'

    country_str = '_'.join(country_list)
    output_file = f'{file_name}_{country_str}'

    with open(input_file, "r") as file:
        data = json.load(file)

    result_list = []
    for platform, results in data.items():
        correct_total = 0
        incorrect_total = 0
        total = len(results)

        for r in results:

            input_result = json.dumps(r)
            output = gI.generate_output(data_1 = input_result, template = template)
            print('OUTPUT:', output)
            print('OUTPUT TYPE:', type(output))
            output = json.loads(output)
            print('OUTPUT TYPE AFTER LOADS', type(output))
            r.update(output)
            

            if output['judgement'] == 'CORRECT':
                correct_total += 1
            else:
                incorrect_total += 1
    
        node = {"platform": platform,
                "total_cases": total,
                "total_correct": correct_total,
                "total_incorrect": incorrect_total,
                "percentage_total_correct": f'{(100/total)*correct_total}%',
                "percentage_total_incorrect": f'{(100/total)*incorrect_total}%'
                }
        
        result_list.append(node)


    json_str = json.dumps(data, indent=2)
    with open(f'{output_dir_data}/{output_file}_llm_judge.json', "w") as f:
        f.write(json_str)

    result_str = json.dumps(result_list, indent=2)
    with open(f'{output_dir_data}/{output_file}_results.json', "w") as f:
        f.write(result_str)
    


    


    
    
    



    

