
from  src.inference import generateInference as gI
from src.inference import prompts as p

import pandas as pd
import json
from datetime import date
import random
from tqdm import tqdm
from pathlib import Path
from datetime import datetime



def run_classification_dev(input_file, output_dir, data_tax, country_list):

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
                 'wu2010': p.prompt_dt_wu_2010(),
                 'verduyn2020':p.prompt_dt_verduyn_2020()}
    
    template = templates[data_tax]

    country_str = '_'.join(country_list)
    output_file = f'{data_tax}_{country_str}'
    

    for platform in df["platform"].unique():

        df_filtered = df[df["platform"] == platform]
        ################################################
        #JUST FOR TESTING!!!!!!!
        ################################################
        #random.seed(100)
        #df_filtered = df_filtered.sample(n=5)
        ################################################
        output_list = []

        print('PROCESSING PLATFORM:', platform)
        for _, row in tqdm(df_filtered.iterrows(), total=len(df_filtered)):
    
            output = gI.generate_output(data_1 = row['final_path'], template = template)
            #print('OUTPUT', output)
            output = json.loads(output)
            #output = output[0]
            node = {"path": row['final_path']}
            node.update(output)
            output_list.append(node)

        results_dict[platform] = output_list

        

    json_str = json.dumps(results_dict, indent=2)
    with open(f'{output_dir}/{output_file}.json', "w") as f:
        f.write(json_str)



def test_classification_dev(input_file, output_dir_data, output_dir_results, country_list):

    if 'schneider2010' in input_file:
        template = p.prompt_judge_dt_schneider_2010()
        file_name = 'schneider2010'

    if 'wu2010' in input_file:
        template = p.prompt_judge_dt_wu_2010()
        file_name = 'wu2010'

    if 'verduyn2020' in input_file:
        template = p.prompt_dt_verduyn_2020()
        file_name = 'verduyn2020'

    country_str = '_'.join(country_list)
    output_file = f'{file_name}_{country_str}'

    with open(input_file, "r") as file:
        data = json.load(file)

    result_list = []
    for platform, results in data.items():
        correct_total = 0
        incorrect_total = 0
        total = len(results)

        print('PROCESSING PLATFORM:', platform)
        for r in tqdm(results, desc=f"Processing results for platform: {platform}"):

            input_result = json.dumps(r)
            output = gI.generate_output(data_1 = input_result, template = template)
            #print('OUTPUT TYPE:', type(output))
            output = json.loads(output)
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
        print(json.dumps(node, indent=2))


    json_str = json.dumps(data, indent=2)
    with open(f'{output_dir_data}/{output_file}_llm_judge.json', "w") as f:
        f.write(json_str)

    result_str = json.dumps(result_list, indent=2)
    with open(f'{output_dir_results}/{output_file}_results.json', "w") as f:
        f.write(result_str)
    



def run_classification_seq(platform_file, output_dir, data_tax, country_list, model, sample = None):

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


    templates = {
        "schneider2010": p.prompt_dt_schneider_2010(),
        "wu2010": p.prompt_dt_wu_2010(),
        "verduyn2020": p.prompt_dt_verduyn_2020(),
    }

    template = templates[data_tax]
    country_str = "_".join(country_list)

   
    output_dir = Path(output_dir)

   

    platform_file_name = platform_file.stem
    platform = platform_file_name.split("_")[0]
    file_number = platform_file_name.split("_")[-1]

    print(
        f"\n{'='*80}\n"
        f"[{datetime.now()}] START PLATFORM: {platform}\n"
        f"{'='*80}",
        flush=True
    )

    output_file = (
        output_dir / platform / f"{platform}_{file_number}_class_ids_{data_tax}_{country_str}_{model}.json"
    )

    # Find input file
    #all_paths = next(input_dir.glob(f"{platform}*"))
    df = pd.read_csv(platform_file)

    if sample is not None:
        df = df.sample(n=sample, random_state=42)

    # --------------------------------------------------
    # Load existing results if the job is being resumed
    # --------------------------------------------------

    if output_file.exists():
        with open(output_file) as f:
            output_list = json.load(f)

        processed_paths = {
            item["path"]
            for item in output_list
        }

        print(
            f"[{datetime.now()}] Resuming  {platform} no. {file_number}: "
            f"{len(output_list)} rows already processed",
            flush=True
        )

    else:
        output_list = []
        processed_paths = set()

    # --------------------------------------------------
    # Process rows
    # --------------------------------------------------

    df_to_process = df[
        ~df["final_path"].isin(processed_paths)
    ]

    print(
        f"[{datetime.now()}] Processing "
        f"{len(df_to_process)} remaining rows for {platform} no. {file_number}",
        flush=True
    )

    try:
        for _, row in tqdm(
        df_to_process.iterrows(),
        total=len(df_to_process)):

            path = row["final_path"]

            for attempt in range(3):
                try:
                    print(
                        f"[{datetime.now()}] WORKING: {path} "
                        f"(attempt {attempt + 1}/3)",
                        flush=True
                    )

                    output = gI.generate_output(
                        data_1=path,
                        template=template
                    )

                    output = json.loads(output)

                    node = {
                        "path": path
                    }
                    node.update(output)

                    output_list.append(node)

                    # Save immediately after successful row
                    with open(output_file, "w") as f:
                        json.dump(
                            output_list,
                            f,
                            indent=2
                        )

                    print(
                        f"[{datetime.now()}] SAVED: {path}",
                        flush=True
                    )

                    # Success -> move to next row
                    break

                except Exception as e:

                    print(
                        f"[{datetime.now()}] FAILED: {path} "
                        f"(attempt {attempt + 1}/3): "
                        f"{type(e).__name__}: {e}",
                        flush=True
                    )

                    if attempt == 2:
                        print(
                            f"[{datetime.now()}] GIVING UP: {path}",
                            flush=True
                        )
                        raise

    except Exception:

        print(
            f"\n[{datetime.now()}] PLATFORM FAILED:  {platform} no. {file_number}",
            flush=True
        )
        print(
            f"[{datetime.now()}] Partial results available at: "
            f" {platform} no. {file_number}",
            flush=True
        )

        raise

    print(
        f"\n[{datetime.now()}] COMPLETED PLATFORM: {platform}\n"
        f"Results: {output_file}",
        flush=True
    )


def process_chunk(
    chunk,
    template,
    agent,
    platform,
    file_number,
    tmp_file,
):
    from src.inference import generateInference as gI

    results = []

    with open(tmp_file, "a", encoding="utf-8") as f:

        for _, row in tqdm(
            chunk.iterrows(),
            total=len(chunk),
            desc=f"{platform} {file_number} agent {agent}",
            position=agent,
        ):
            path = row["final_path"]

            for attempt in range(3):
                try:
                    print(
                        f"[{datetime.now()}] WORKING: {path} "
                        f"(agent {agent}, attempt {attempt + 1}/3)",
                        flush=True,
                    )

                    output = gI.generate_output(
                        data_1=path,
                        template=template,
                        agent_no=agent,
                    )

                    output = json.loads(output)

                    node = {
                        "path": path,
                    }
                    node.update(output)

                    results.append(node)

                    # Checkpoint immediately
                    f.write(
                        json.dumps(node, ensure_ascii=False) + "\n"
                    )
                    f.flush()

                    print(
                        f"[{datetime.now()}] SAVED: {path}",
                        flush=True,
                    )

                    break

                except Exception as e:
                    print(
                        f"[{datetime.now()}] FAILED: {path} "
                        f"(agent {agent}, attempt {attempt + 1}/3): "
                        f"{type(e).__name__}: {e}",
                        flush=True,
                    )

                    if attempt == 2:
                        print(
                            f"[{datetime.now()}] GIVING UP: {path}",
                            flush=True,
                        )
                        raise

    return results


def run_classification(
    platform_file,
    output_dir,
    data_tax,
    country_list,
    model,
    num_agents
):
    """
    data_tax:
        - 'schneider2010'
        - 'wu2010'
        - 'verduyn2020'

    country_list:
        e.g. ['ES', 'NL']
    """

    templates = {
        "schneider2010": p.prompt_dt_schneider_2010(),
        "wu2010": p.prompt_dt_wu_2010(),
        "verduyn2020": p.prompt_dt_verduyn_2020(),
    }

    template = templates[data_tax]
    country_str = "_".join(country_list)

    output_dir = Path(output_dir)

    platform_file_name = platform_file.stem
    platform = platform_file_name.split("_")[0]
    file_number = platform_file_name.split("_")[-1]

    print(
        f"\n{'=' * 80}\n"
        f"[{datetime.now()}] START PLATFORM: {platform} "
        f"FILE: {file_number}\n"
        f"{'=' * 80}",
        flush=True,
    )

    # --------------------------------------------------
    # Output paths
    # --------------------------------------------------

    out_dir = output_dir / platform
    out_dir.mkdir(parents=True, exist_ok=True)

    output_file = (
        out_dir
        / f"{platform}_{file_number}_class_ids_"
          f"{data_tax}_{country_str}_{model}.json"
    )

    # --------------------------------------------------
    # Read input
    # --------------------------------------------------

    df = pd.read_csv(platform_file)

    # --------------------------------------------------
    # Load existing results
    # --------------------------------------------------

    if output_file.exists():

        with open(output_file) as f:
            output_list = json.load(f)

        processed_paths = {
            item["path"]
            for item in output_list
        }

        print(
            f"[{datetime.now()}] Resuming {platform} "
            f"no. {file_number}: "
            f"{len(output_list)} rows already processed",
            flush=True,
        )

    else:
        output_list = []
        processed_paths = set()

    # --------------------------------------------------
    # Remove already processed rows
    # --------------------------------------------------

    df_to_process = df[
        ~df["final_path"].isin(processed_paths)
    ].copy()

    print(
        f"[{datetime.now()}] Processing "
        f"{len(df_to_process)} remaining rows for "
        f"{platform} no. {file_number}",
        flush=True,
    )

    if df_to_process.empty:
        print(
            f"[{datetime.now()}] Nothing left to process.",
            flush=True,
        )
        return

    # --------------------------------------------------
    # Split across agents
    # --------------------------------------------------

    chunks = [
        df_to_process.iloc[i::num_agents]
        for i in range(num_agents)
    ]

    # Don't create workers for empty chunks
    chunks = [
        (agent, chunk)
        for agent, chunk in enumerate(chunks)
        if not chunk.empty
    ]

    jobs = []

    for agent, chunk in chunks:

        tmp_file = (
            out_dir
            / f"agent_{agent}_{platform}_{file_number}.jsonl"
        )

        jobs.append(
            (
                chunk,
                template,
                agent,
                platform,
                file_number,
                tmp_file,
            )
        )

    # --------------------------------------------------
    # Run agents in parallel
    # --------------------------------------------------

    from multiprocessing import get_context

    with get_context("spawn").Pool(
        processes=len(jobs)
    ) as pool:

        results = pool.starmap(
            process_chunk,
            jobs,
            chunksize=1,
        )

    # --------------------------------------------------
    # Combine results
    # --------------------------------------------------

    new_results = [
        item
        for agent_results in results
        for item in agent_results
    ]

    output_list.extend(new_results)

    # --------------------------------------------------
    # Save final output
    # --------------------------------------------------

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            output_list,
            f,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------
    # Remove temporary agent files
    # --------------------------------------------------

    for _, _, _, _, _, tmp_file in jobs:
        tmp_file.unlink(missing_ok=True)

    print(
        f"\n[{datetime.now()}] COMPLETED PLATFORM: {platform} "
        f"FILE: {file_number}",
        flush=True,
    )

    print(
        f"Results: {output_file}",
        flush=True,
    )

    print(
        f"Total results: {len(output_list)}",
        flush=True,
    )



#####################################################################
# LLM AS JUDGE
#######################################################################
def test_classification_dev(input_file, output_dir_data, output_dir_results, country_list):

    if 'schneider2010' in input_file:
        template = p.prompt_judge_dt_schneider_2010()
        file_name = 'schneider2010'

    if 'wu2010' in input_file:
        template = p.prompt_judge_dt_wu_2010()
        file_name = 'wu2010'

    if 'verduyn2020' in input_file:
        template = p.prompt_dt_verduyn_2020()
        file_name = 'verduyn2020'

    country_str = '_'.join(country_list)
    output_file = f'{file_name}_{country_str}'

    with open(input_file, "r") as file:
        data = json.load(file)

    result_list = []
    for platform, results in data.items():
        correct_total = 0
        incorrect_total = 0
        total = len(results)

        print('PROCESSING PLATFORM:', platform)
        for r in tqdm(results, desc=f"Processing results for platform: {platform}"):

            input_result = json.dumps(r)
            output = gI.generate_output(data_1 = input_result, template = template)
            #print('OUTPUT TYPE:', type(output))
            output = json.loads(output)
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
        print(json.dumps(node, indent=2))


    json_str = json.dumps(data, indent=2)
    with open(f'{output_dir_data}/{output_file}_llm_judge.json', "w") as f:
        f.write(json_str)

    result_str = json.dumps(result_list, indent=2)
    with open(f'{output_dir_results}/{output_file}_results.json', "w") as f:
        f.write(result_str)



def test_classification(input_dir, output_dir_data, output_dir_results, country_list):

    country_str = "_".join(country_list)

    for platform_dir in input_dir.iterdir():

        platform = platform_dir.name

        for file in platform_dir.iterdir():

            if "schneider2010" in file.name:
                template = p.prompt_judge_dt_schneider_2010()
                file_name = "schneider2010"

            elif "wu2010" in file.name:
                template = p.prompt_judge_dt_wu2010()
                file_name = "wu2010"

            elif "verduyn2020" in file.name:
                template = p.prompt_dt_verduyn_2020()
                file_name = "verduyn2020"

            else:
                continue

            output_file = f"{platform}_{file_name}_{country_str}"

            data_output_path = (
                output_dir_data / f"{output_file}_llm_judge.json"
            )

            result_output_path = (
                output_dir_results / f"{output_file}_results.json"
            )

            # --------------------------------------------------
            # Load original data
            # --------------------------------------------------

            with open(file, "r") as f:
                data = json.load(f)

            # --------------------------------------------------
            # Resume existing results if available
            # --------------------------------------------------

            if data_output_path.exists():

                print(
                    f"[{datetime.now()}] Resuming from "
                    f"{data_output_path}",
                    flush=True
                )

                with open(data_output_path, "r") as f:
                    data = json.load(f)

            total = len(data)

            # --------------------------------------------------
            # Process
            # --------------------------------------------------

            for i, r in enumerate(
                tqdm(
                    data,
                    desc=f"Processing results for platform: {platform}"
                )
            ):

                # Skip rows that were already judged
                if "judgement" in r:
                    continue

                path = r.get("path", f"row {i}")

                for attempt in range(3):

                    try:

                        print(
                            f"[{datetime.now()}] "
                            f"WORKING {i + 1}/{total}: {path} "
                            f"(attempt {attempt + 1}/3)",
                            flush=True
                        )

                        input_result = json.dumps(r)

                        output = gI.generate_output(
                            data_1=input_result,
                            template=template
                        )

                        output = json.loads(output)

                        r.update(output)

                        # --------------------------------------
                        # SAVE IMMEDIATELY
                        # --------------------------------------

                        with open(data_output_path, "w") as f:
                            json.dump(
                                data,
                                f,
                                indent=2
                            )

                        print(
                            f"[{datetime.now()}] SAVED: {path}",
                            flush=True
                        )

                        # Successful -> next row
                        break

                    except Exception as e:

                        print(
                            f"[{datetime.now()}] FAILED: {path} "
                            f"(attempt {attempt + 1}/3): "
                            f"{type(e).__name__}: {e}",
                            flush=True
                        )

                        if attempt == 2:
                            print(
                                f"[{datetime.now()}] "
                                f"GIVING UP: {path}",
                                flush=True
                            )

            # --------------------------------------------------
            # Calculate final statistics from saved data
            # --------------------------------------------------

            correct_total = sum(
                r.get("judgement") == "CORRECT"
                for r in data
            )

            incorrect_total = sum(
                r.get("judgement") == "INCORRECT"
                for r in data
            )

            judged_total = correct_total + incorrect_total

            node = {
                "platform": platform,
                "total_cases": total,
                "total_judged": judged_total,
                "total_correct": correct_total,
                "total_incorrect": incorrect_total,
                "percentage_total_correct": (
                    f"{100 * correct_total / judged_total}%"
                    if judged_total else "0%"
                ),
                "percentage_total_incorrect": (
                    f"{100 * incorrect_total / judged_total}%"
                    if judged_total else "0%"
                ),
            }

            print(json.dumps(node, indent=2))

            # Save final summary
            with open(result_output_path, "w") as f:
                json.dump(
                    [node],
                    f,
                    indent=2
                )

    
    


    
    
    



    

