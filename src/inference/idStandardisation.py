

import pandas as pd
import json
from datetime import date
import random
from difflib import SequenceMatcher
from tqdm import tqdm



def run_id_std(input_file, output_dir, country_list):

    from src.inference import generateInference as gI
    from src.inference import prompts as p

    df = pd.read_csv(input_file)
    results_dict = {}

    country_str = '_'.join(country_list)
    output_file = f'std_ids_{country_str}'

    for platform in df["platform"].unique():

        df_filtered = df[df['platform'] == platform]
        cats = str(df_filtered['keepID'].values.tolist())
        print('CATS', cats)

        ################################################
        #JUST FOR TESTING!!!!!!!
        ###############################################
        #random.seed(100)
        #df_filtered = df_filtered.sample(n=5)
        ################################################

        #df = df[:50]
        output_list = []
        print('PROCESSING PLATFORM:', platform)
        for _, row in tqdm(df_filtered.iterrows(), total=len(df_filtered)):

            output = gI.generate_output(data_1 = row['final_path'], template = p.prompt_std_ids(), data_2=cats)
            print('OUTPUT', output)
            output = json.loads(output)
            #output = output[0]
            node = {"path": row['final_path'],
                    "true_id": row['keepID']}
            
            node.update(output)
            output_list.append(node)
            #print(node)


        results_dict[platform] = output_list

            

    json_str = json.dumps(results_dict, indent=2)
    with open(f'{output_dir}/{output_file}.json', "w") as f:
        f.write(json_str)
        


def test_id_standardisation(input_file, output_dir_data, output_dir_results, df_cats, country_list):
    df = pd.read_csv(df_cats)
    cats = str(df['keepID'].values.tolist())   

    country_str = '_'.join(country_list)
    output_file_data = f'std_ids_test_{country_str}'
    output_file_results = f'std_ids_test_results_{country_str}'       

    with open(input_file, "r") as file:
        data = json.load(file)

    
    results_dict = {}

    for platform, results in data.items():
        
        incorrect = 0
        correct = 0
        total = len(results)
        #result_list = []

        for d in results:
            estimated_id = d['estimated_id']
            true_id = d['true_id']
            if estimated_id != true_id:
                incorrect +=1
                # Calculating similarity ratio
                d['result'] = 'INCORRECT'
                d['sim_ratio'] = SequenceMatcher(None, true_id, estimated_id).ratio()

                if estimated_id in cats:
                    d['present_in_list'] = 'True'
                else:
                    d['present_in_list'] = 'False'

            else:
                correct += 1
                d['result'] = 'CORRECT' 

        node = {"platform": platform,
                "total_cases": total,
                "total_correct": correct,
                "total_incorrect": incorrect,
                "percentage_total_correct": f'{(100/total)*correct}%',
                "percentage_total_incorrect": f'{(100/total)*incorrect}%'
                }

        #result_list.append(node)
        results_dict[platform] = node

    data = json.dumps(data, indent = 2)
    with open(f'{output_dir_data}/{output_file_data}.json', "w") as f:
        f.write(data)


    print(f'{correct}/{total} ({(100/total)*correct}%) CORRECT CASES')
    print(f'{incorrect}/{total} ({(100/total)*incorrect}%) INCORRECT CASES')

    results_dict = json.dumps(results_dict, indent = 2)

    print(results_dict)
    with open(f'{output_dir_results}/{output_file_results}.json', "w") as f:
        f.write(results_dict)

    



    

