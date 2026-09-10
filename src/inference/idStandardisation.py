

import pandas as pd
import json
import random
from difflib import SequenceMatcher
from tqdm import tqdm
import os
import re
from pathlib import Path
import random
import numpy as np
from multiprocessing import get_context
from datetime import datetime

###############################################################
# TESTING
###############################################################
def run_id_std_for_testing(input_file, output_dir, country_list):

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
            if output["estimated_id"] not in cats:
                output = gI.generate_output(data_1 = row['final_path'], template = p.prompt_std_ids_retry(), data_2=cats, data_3=output["estimated_id"])


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

###############################################################
# PRODUCTION
###############################################################
#-------------------------------------------------------------
# Run inference not distributed
#-------------------------------------------------------------
def run_id_std_solo(input_dir, output_dir, id_dir, country_list):

    from src.inference import generateInference as gI
    from src.inference import prompts as p
    input_dir = Path(input_dir)
    id_dir = Path(id_dir)

    country_str = '_'.join(country_list)
    for platform_dir in id_dir.iterdir(): 
        platform = platform_dir.name
        output_file = f'{platform}_std_ids_{country_str}'

        all_paths = next(input_dir.glob(f"{platform}*"))
        reference_paths = next(platform_dir.iterdir())

        df_all_paths = pd.read_csv(all_paths)
        df_reference_paths = pd.read_csv(reference_paths)
        refs= str(df_reference_paths['final_path'].values.tolist())

        output_list = []
        print('PROCESSING PLATFORM:', platform)
        ################################################
        #JUST FOR TESTING!!!!!!!
        ###############################################
        random.seed(100)
        df_all_paths = df_all_paths.sample(n=5)
        ################################################
        for _, row in tqdm(df_all_paths.iterrows(), total=len(df_all_paths), desc=f"Processing {platform}"):

            output = gI.generate_output(data_1 = row['final_path'], template = p.prompt_std_ids(), data_2=refs)
            print('OUTPUT', output)
            output = json.loads(output)
            #output = output[0]
            node = {"path": row['final_path']}
            
            node.update(output)
            output_list.append(node)
            #print(node)

        json_str = json.dumps(output_list, indent=2)
        with open(f'{output_dir}/{output_file}.json', "w") as f:
            f.write(json_str)


#-------------------------------------------------------------
# Run inference distributed
#-------------------------------------------------------------
def process_chunk(chunk, refs, agent, platform, output_dir, output_file):

    from src.inference import generateInference as gI
    from src.inference import prompts as p

    output_list = []

    for _, row in tqdm(
        chunk.iterrows(),
        total=len(chunk),
        desc=f"{platform} - AGENT {agent} - TIME {datetime.now()}"):

        output = gI.generate_output(
            data_1=row["final_path"],
            template=p.prompt_std_ids(),
            data_2=refs,
            agent_no=agent)

        print(f"AGENT {agent} OUTPUT:", output)

        try:
            output = json.loads(output)
        except Exception as e:
            print(f"JSON error on AGENT {agent}: {e}")
            continue

        node = {"path": row["final_path"]}

        node.update(output)
        output_list.append(node)

    return output_list


def run_id_std(input_dir, output_dir, id_dir, country_list, model, num_agents):

    input_dir = Path(input_dir)
    id_dir = Path(id_dir)
    output_dir = Path(output_dir)

    from src.inference import prompts as p

    country_str = "_".join(country_list)

    for platform_dir in id_dir.iterdir():

        platform = platform_dir.name

        output_file = f"{platform}_std_ids_{country_str}_{model}.json"

        all_paths = next(
            input_dir.glob(f"{platform}*"))

        reference_paths = next(platform_dir.iterdir())

        df_all_paths = pd.read_csv(all_paths)
        df_reference_paths = pd.read_csv(reference_paths)

        print(f'LENGTH DF BEFORE EXCLUSION: {len(df_all_paths)}')
        df_all_paths = df_all_paths[~df_all_paths["final_path"].isin(df_reference_paths["final_path"])]
        print(f'LENGTH DF AFTER EXCLUSION: {len(df_all_paths)}')

        refs = str(df_reference_paths["final_path"].values.tolist())

        print(f"PROCESSING PLATFORM: {platform}")

        # JUST FOR TESTING
        random.seed(100)
        df_all_paths = df_all_paths.sample(n=10)

        # Split dataframe into 4 equal chunks
        chunks = np.array_split(df_all_paths, num_agents)

        jobs = []

        for agent, chunk in enumerate(chunks):

            jobs.append((chunk,
                        refs,
                        agent,
                        platform,
                        output_dir,
                        output_file))

        # Spawn 4 processes
        ctx = get_context("spawn")

        with ctx.Pool(processes=num_agents) as pool:

            results = pool.starmap(process_chunk, jobs)

        # Combine results from all GPUs
        output_list = []

        for result in results:
            output_list.extend(result)

        # Save combined output
        with open(
            output_dir / platform / output_file,"w") as f:

            json.dump(output_list, f, indent=2)

        print(
            f"Finished {platform}: "
            f"{len(output_list)} results")


#-------------------------------------------------------------
# Find disagreements between LLMs
#-------------------------------------------------------------
def get_disagreements(input_files, agreements_dir, disagreements_dir, platform, country_str):
    dataframes = []

    for results in input_files:
        results = Path(results)
        model = results.stem

        with open(results) as f:
            data = json.load(f)

        df = pd.DataFrame(data).rename(
            columns={"estimated_path": f"estimated_path_{model}"}
        )

        dataframes.append(df)

    # Merge all JSONs on path
    merged = dataframes[0]

    for df in dataframes[1:]:
        merged = merged.merge(df, on="path", how="inner")

    # Get estimated_path columns
    estimated_cols = [
        col for col in merged.columns
        if col.startswith("estimated_path_")
    ]

    # Keep rows where not all models agree
    disagreements = merged[
        merged[estimated_cols].nunique(axis=1) > 1
    ][["path"] + estimated_cols]

    # Rows where all models agree
    agreements = merged[
        merged[estimated_cols].nunique(axis=1) == 1
    ][["path"] + estimated_cols]

    disagreements_dir = Path(f'{disagreements_dir}/{platform}')
    disagreements_dir.mkdir(parents=True, exist_ok=True)

    agreements_dir = Path(f'{disagreements_dir}/{platform}')
    agreements_dir.mkdir(parents=True, exist_ok=True)

    disagreements.to_json(
        disagreements_dir / f"{platform}_id_std_disagreements_{country_str}.json",
        orient="records",
        indent=4)

    agreements.to_json(
            agreements_dir / f"{platform}_id_std_agreements_{country_str}.json",
            orient="records",
            indent=4)



def resolve_disagreements(disagreements_dir, refs, platform, resolved_dir, country_str):

    import json
    from pathlib import Path
    from tqdm import tqdm

    from src.inference import generateInference as gI
    from src.inference import prompts as p

    output_dir = Path(output_dir) / platform
    disagreements_dir = Path(disagreements_dir) / platform
    disagreement_json = next(disagreements_dir.iterdir())

    # Load JSON
    with open(disagreement_json, "r") as f:
        data = json.load(f)

    output_list = []

    for row in tqdm(data, total=len(data), desc=f"Processing {platform}"):

        output = gI.generate_output(
            data_1=row["path"],
            template=p.prompt_std_ids(),
            data_2=row[list(row.keys())[1]],
            data_3 = row[list(row.keys())[2]],
            data_4 = refs
        )

        print("OUTPUT", output)

        output = json.loads(output)

        node = row.copy()

        node.update(output)
        output_list.append(node)

    json_str = json.dumps(output_list, indent=2)

    output_file = f"{platform}_id_std_disagreements_resolved_{country_str}.json"
    with open(f"{resolved_dir}/{output_file}", "w") as f:
        f.write(json_str)

def final_path(agreements_dir, resolve_dir, final_dir, platform, country_str):
    agreements_dir = Path(agreements_dir) / platform
    resolve_dir = Path(resolve_dir) / platform

    agreements = next(agreements_dir.iterdir())
    resolved = next(resolve_dir.iterdir())

    with open(agreements, "r") as f:
        agreement = json.load(f)

    with open(resolved, "r") as f:
        resolve = json.load(f)

    combined = agreement + resolve

    with open(f"{final_dir}/{platform}/{platform}_final_estimated_paths_{country_str}.json", "w") as f:
        json.dump(combined, f, indent=2)


def process_disagreements(id_dir, input_dir, disagreements_dir, agreements_dir, resolve_dir, final_dir, country_list):
    for platform_dir in id_dir.iterdir(): 

        platform = platform_dir.name
        country_str = "_".join(country_list)
       

    
        input_files = list(Path(f'{input_dir}/{platform}').glob("*.json"))
        reference_paths = next(platform_dir.iterdir())
        df_reference_paths = pd.read_csv(reference_paths)
        refs= str(df_reference_paths['final_path'].values.tolist())


        get_disagreements(input_files, agreements_dir, disagreements_dir, platform, country_str)
        resolve_disagreements(disagreements_dir, refs, platform, resolve_dir, country_str)
        final_path(agreements_dir, resolve_dir, final_dir, platform, country_str)
        
