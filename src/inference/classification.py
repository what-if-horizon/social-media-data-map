
from  src.inference import generateInference as gI
from src.inference import prompts as p

import pandas as pd



def run_classification(input_file, platform):
    df = pd.read_csv(input_file)
    df = df[df['platform'] == platform]
    cats = df['keepID']

    output_list = []
    for ix, row in df.iterrows():

        output = gI.generate_output(data_1 = row['final_path'], data_2=cats, template = p.prompt_classification )
        node = {"path": row['final_path']}
        node.update(output)
        output_list.append(node)
    



    

