

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
import traceback

###############################################################
# TESTING
###############################################################

def run_id_std_for_testing(input_file, output_dir, country_list):

    from src.inference import generateInference as gI
    from src.inference.legacy import prompts as p

    df = pd.read_csv(input_file)

    country_str = '_'.join(country_list)

    for platform in df["platform"].unique():

        df_filtered = df[df["platform"] == platform]
        cats = str(df_filtered["keepID"].values.tolist())

        print("CATS", cats)
        print("PROCESSING PLATFORM:", platform)

        output_list = []

        for _, row in tqdm(
            df_filtered.iterrows(),
            total=len(df_filtered),
            desc=platform
        ):
            if row["id"] == row["keepID"]:
                continue

            try:
                output = gI.generate_output(
                    data_1=row["final_path"],
                    template=p.prompt_std_ids_test(),
                    data_2=cats
                )

                print("OUTPUT", output)
                output = json.loads(output)

                if output["estimated_id"] not in cats:
                    output = gI.generate_output(
                        data_1=row["final_path"],
                        template=p.prompt_std_ids_retry(),
                        data_2=cats,
                        data_3=output["estimated_id"]
                    )
                    output = json.loads(output)

                node = {
                    "path": row["final_path"],
                    "true_id": row["keepID"]
                }

                node.update(output)
                output_list.append(node)

            except Exception as e:
                print(f"ERROR {e} for {row['final_path']}")

        # Save one file per platform
        output_file = f"{output_dir}/std_ids_{country_str}_{platform}.json"

        with open(output_file, "w") as f:
            json.dump(output_list, f, indent=2)

        print(f"SAVED: {output_file}")


def test_id_standardisation_old(input_file, output_dir_data, output_dir_results, df_cats, country_list):
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


from pathlib import Path
import json
from difflib import SequenceMatcher

import pandas as pd


def calculate_metrics(results, cats):
    """
    Calculate evaluation metrics for a list of standardisation results.
    """

    total = len(results)
    correct = 0
    incorrect = 0

    similarity_ratios = []
    present_in_list = 0

    for d in results:

        estimated_id = d["estimated_id"]
        true_id = d["true_id"]

        if estimated_id == true_id:
            correct += 1
            d["result"] = "CORRECT"

        else:
            incorrect += 1
            d["result"] = "INCORRECT"

            sim_ratio = SequenceMatcher(
                None,
                true_id,
                estimated_id
            ).ratio()

            d["sim_ratio"] = sim_ratio
            similarity_ratios.append(sim_ratio)

            if d["estimated_id"] in cats:
                d["present_in_list"] = True
                present_in_list += 1
            else:
                d["present_in_list"] = False

    # Avoid division by zero
    if total > 0:
        accuracy = correct / total
        error_rate = incorrect / total
    else:
        accuracy = 0
        error_rate = 0

    if similarity_ratios:
        mean_similarity = sum(similarity_ratios) / len(similarity_ratios)
        median_similarity = sorted(similarity_ratios)[
            len(similarity_ratios) // 2
        ]

        # Better median calculation for even number of values
        n = len(similarity_ratios)
        sorted_ratios = sorted(similarity_ratios)

        if n % 2 == 0:
            median_similarity = (
                sorted_ratios[n // 2 - 1] +
                sorted_ratios[n // 2]
            ) / 2
        else:
            median_similarity = sorted_ratios[n // 2]

    else:
        mean_similarity = None
        median_similarity = None

    if incorrect > 0:
        percentage_present_in_list = (
            present_in_list / incorrect
        )
    else:
        percentage_present_in_list = None

    metrics = {
        "total_cases": total,
        "total_correct": correct,
        "total_incorrect": incorrect,

        "accuracy": accuracy,
        "accuracy_percentage": accuracy * 100,

        "error_rate": error_rate,
        "error_rate_percentage": error_rate * 100,

        "incorrect_mean_similarity": mean_similarity,
        "incorrect_median_similarity": median_similarity,

        "incorrect_estimated_id_present_in_list": present_in_list,
        "incorrect_estimated_id_present_in_list_percentage":
            None if percentage_present_in_list is None
            else percentage_present_in_list * 100
    }

    return results, metrics


def test_id_standardisation(
    input_dir,
    output_dir_data,
    output_dir_results,
    df_cats,
    country_list
):

    input_dir = Path(input_dir)
    output_dir_data = Path(output_dir_data)
    output_dir_results = Path(output_dir_results)

    output_dir_data.mkdir(parents=True, exist_ok=True)
    output_dir_results.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # LOAD VALID IDs
    # ---------------------------------------------------------

    df = pd.read_csv(df_cats)
    print(df)

    cats = set(
        df["keepID"]
        .dropna()
        .astype(str)
    )

    # ---------------------------------------------------------
    # FIND PLATFORM FILES
    # ---------------------------------------------------------

    json_files = sorted(input_dir.glob("*.json"))

    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return

    country_str = "_".join(country_list)

    # ---------------------------------------------------------
    # STORAGE FOR POOLED RESULTS
    # ---------------------------------------------------------

    pooled_results = []

    platform_metrics = {}

    # ---------------------------------------------------------
    # PROCESS EACH PLATFORM FILE
    # ---------------------------------------------------------

    for input_file in json_files:

        print(f"\nProcessing: {input_file.name}")

        # -----------------------------------------------------
        # LOAD FILE
        # -----------------------------------------------------

        with open(input_file, "r") as file:
            data = json.load(file)

        # -----------------------------------------------------
        # DETERMINE PLATFORM
        # -----------------------------------------------------

        # Expected possibilities:
        #
        # {
        #     "tiktok": [...]
        # }
        #
        # or
        #
        # [...]
        #

        if isinstance(data, dict):

            # If the JSON contains a single platform key
            if len(data) == 1:
                platform = next(iter(data))
                results = data[platform]

            else:
                # If multiple platforms happen to be present
                for platform, results in data.items():

                    results, metrics = calculate_metrics(results, cats)

                    platform_metrics[platform] = metrics
                    pooled_results.extend(results)

                    output_data = {
                        platform: results
                    }

                    output_file = (
                        output_dir_data /
                        f"{platform}_std_ids_test_{country_str}.json"
                    )

                    with open(output_file, "w") as f:
                        json.dump(
                            output_data,
                            f,
                            indent=2
                        )

                continue

        else:
            # If the file itself contains the list of results
            platform = input_file.stem
            results = data

        # -----------------------------------------------------
        # EVALUATE PLATFORM
        # -----------------------------------------------------

        results, metrics = calculate_metrics(results, cats)

        platform_metrics[platform] = metrics

        # Add results to pooled evaluation
        pooled_results.extend(results)

        # -----------------------------------------------------
        # SAVE ANNOTATED PLATFORM RESULTS
        # -----------------------------------------------------

        output_data = {
            platform: results
        }

        output_file = (
            output_dir_data /
            f"{platform}_std_ids_test_{country_str}.json"
        )

        with open(output_file, "w") as f:
            json.dump(
                output_data,
                f,
                indent=2
            )

        # -----------------------------------------------------
        # PRINT PLATFORM RESULTS
        # -----------------------------------------------------

        print(
            f"{platform}: "
            f"{metrics['total_correct']}/"
            f"{metrics['total_cases']} "
            f"({metrics['accuracy_percentage']:.2f}%) correct"
        )

    # =========================================================
    # POOLED EVALUATION
    # =========================================================

    _, pooled_metrics = calculate_metrics(pooled_results, cats)

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    summary = {
        "platforms": platform_metrics,
        "pooled": pooled_metrics
    }

    # ---------------------------------------------------------
    # SAVE SUMMARY
    # ---------------------------------------------------------

    summary_file = (
        output_dir_results /
        f"std_ids_test_results_{country_str}.json"
    )

    with open(summary_file, "w") as f:
        json.dump(
            summary,
            f,
            indent=2
        )

    # =========================================================
    # PRINT RESULTS
    # =========================================================

    print("\n" + "=" * 60)
    print("RESULTS PER PLATFORM")
    print("=" * 60)

    for platform, metrics in platform_metrics.items():

        print(
            f"\n{platform}"
        )

        print(
            f"  Total cases:    {metrics['total_cases']}"
        )

        print(
            f"  Correct:        {metrics['total_correct']}"
        )

        print(
            f"  Incorrect:      {metrics['total_incorrect']}"
        )

        print(
            f"  Accuracy:       "
            f"{metrics['accuracy_percentage']:.2f}%"
        )

        print(
            f"  Error rate:     "
            f"{metrics['error_rate_percentage']:.2f}%"
        )

        if metrics["incorrect_mean_similarity"] is not None:

            print(
                f"  Mean similarity:"
                f" {metrics['incorrect_mean_similarity']:.4f}"
            )

            print(
                f"  Median similarity:"
                f" {metrics['incorrect_median_similarity']:.4f}"
            )

        if (
            metrics[
                "incorrect_estimated_id_present_in_list_percentage"
            ]
            is not None
        ):

            print(
                f"  Incorrect IDs in list:"
                f" {metrics['incorrect_estimated_id_present_in_list_percentage']:.2f}%"
            )

    # =========================================================
    # PRINT POOLED RESULTS
    # =========================================================

    print("\n" + "=" * 60)
    print("POOLED ACROSS ALL PLATFORMS")
    print("=" * 60)

    print(
        f"Total cases:    "
        f"{pooled_metrics['total_cases']}"
    )

    print(
        f"Correct:        "
        f"{pooled_metrics['total_correct']}"
    )

    print(
        f"Incorrect:      "
        f"{pooled_metrics['total_incorrect']}"
    )

    print(
        f"Accuracy:       "
        f"{pooled_metrics['accuracy_percentage']:.2f}%"
    )

    print(
        f"Error rate:     "
        f"{pooled_metrics['error_rate_percentage']:.2f}%"
    )

    if pooled_metrics["incorrect_mean_similarity"] is not None:

        print(
            f"Mean similarity:"
            f" {pooled_metrics['incorrect_mean_similarity']:.4f}"
        )

        print(
            f"Median similarity:"
            f" {pooled_metrics['incorrect_median_similarity']:.4f}"
        )

    if (
        pooled_metrics[
            "incorrect_estimated_id_present_in_list_percentage"
        ]
        is not None
    ):

        print(
            f"Incorrect IDs in list:"
            f" {pooled_metrics['incorrect_estimated_id_present_in_list_percentage']:.2f}%"
        )
###############################################################
# PRODUCTION
###############################################################
#-------------------------------------------------------------
# Run inference not distributed
#-------------------------------------------------------------
def run_id_std_solo(input_dir, output_dir, id_dir, country_list, model, sample = None, selected_platform = None):

    from src.inference import generateInference as gI
    from src.inference.legacy import prompts as p

    input_dir = Path(input_dir)
    id_dir = Path(id_dir)
    output_dir = Path(output_dir)

    country_str = "_".join(country_list)

    for platform_dir in id_dir.iterdir():

        platform = platform_dir.name
        if selected_platform != None:
            if platform != selected_platform:
                continue

        print(
            f"\n{'='*80}\n"
            f"[{datetime.now()}] START PLATFORM: {platform}\n"
            f"{'='*80}",
            flush=True
        )

        output_file = f"{platform}_std_ids_{country_str}_{model}.json"

        all_paths = next(
            input_dir.glob(f"{platform}*")
        )

        reference_paths = next(
            platform_dir.iterdir()
        )

        df_all_paths = pd.read_csv(all_paths)
        df_reference_paths = pd.read_csv(reference_paths)

        # Remove paths that are already reference/classified paths
        df_all_paths = df_all_paths[
            ~df_all_paths["final_path"].isin(
                df_reference_paths["final_path"]
            )
        ]

        refs = str(
            df_reference_paths["final_path"].values.tolist()
        )

        if sample != None:
            df_all_paths = df_all_paths.sample(n = sample, random_state=42)

        output_list = []

        print(
            f"[{datetime.now()}] Processing {len(df_all_paths)} "
            f"rows for {platform}",
            flush=True
        )

        for _, row in tqdm(
            df_all_paths.iterrows(),
            total=len(df_all_paths),
            desc=f"Processing {platform}"
        ):

            try:
                print(
                    f"[{datetime.now()}] "
                    f"WORKING row={row['final_path']}",
                    flush=True
                )

                output = gI.generate_output(
                    data_1=row["final_path"],
                    template=p.prompt_std_ids(),
                    data_2=refs
                )

                print(
                    f"[{datetime.now()}] "
                    f"OUTPUT row={row['final_path']}: {output}",
                    flush=True
                )

            except Exception as e:
                print(
                    f"[{datetime.now()}] "
                    f"ERROR row={row['final_path']}: {e}",
                    flush=True
                )
                traceback.print_exc()
                continue

            try:
                output = json.loads(output)

            except Exception as e:
                print(
                    f"[{datetime.now()}] "
                    f"JSON error for row={row['final_path']}: {e}",
                    flush=True
                )
                continue

            node = {
                "path": row["final_path"]
            }

            node.update(output)
            output_list.append(node)

        # Make sure platform output directory exists
        platform_output_dir = output_dir / platform
        platform_output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # Save combined output
        output_path = platform_output_dir / output_file

        with open(output_path, "w") as f:
            json.dump(output_list, f, indent=2)

        print(
            f"[{datetime.now()}] "
            f"FINISHED {platform}: "
            f"{len(output_list)} results",
            flush=True
        )

        print(
            f"[{datetime.now()}] "
            f"SAVED: {output_path}",
            flush=True
        )

#-------------------------------------------------------------
# Run inference distributed
#-------------------------------------------------------------
import json, re, traceback
from datetime import datetime
from multiprocessing import get_context
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def parse_json(raw):
    """Accept dicts, plain JSON, or JSON wrapped in ```json fences."""
    if isinstance(raw, dict):
        return raw
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(raw).strip())
    return json.loads(text)


def process_chunk(chunk, refs, agent, platform, model, tmp_file):
    # If agent maps to a GPU, set CUDA_VISIBLE_DEVICES here, before imports.
    from src.inference import generateInference as gI
    from src.inference.legacy import prompts as p

    template = p.prompt_std_ids()          # build once, not per row
    results, failures = [], []

    with open(tmp_file, "a", encoding="utf-8") as f:
        for _, row in tqdm(chunk.iterrows(), total=len(chunk),
                           desc=f"{platform} agent {agent}", position=agent):
            path = row["final_path"]
            raw = None
            try:
                raw = gI.generate_output(
                    data_1=path, template=template,
                    data_2=refs, agent_no=agent,   # add model=model if supported
                )
                parsed = parse_json(raw)
                if not isinstance(parsed, dict):
                    raise ValueError(f"Expected dict, got {type(parsed).__name__}")
                
            except Exception as e:
                print(f"[{datetime.now()}] ERROR agent={agent}, {path}: {e}", flush=True)
                traceback.print_exc()
                failures.append({"path": path, "error": str(e), "raw": str(raw)})
                continue

            node = {"path": path, **parsed}
            results.append(node)
            f.write(json.dumps(node, ensure_ascii=False) + "\n")   # checkpoint
            f.flush()

    return results, failures


def run_id_std(platform_file, output_dir, id_dir, country_list, model, num_agents):
    id_dir, output_dir =Path(id_dir), Path(output_dir)
    num_agents = int(num_agents)
    country_str = "_".join(country_list)

    
    platform_file_name = platform_file.stem
    platform = platform_file_name.split("_")[0]
    file_number = platform_file_name.split("_")[-1]

    print(f"\n{'=' * 80}\n[{datetime.now()}] START PLATFORM: {platform}\n{'=' * 80}", flush=True)

    out_dir = output_dir / platform
    out_dir.mkdir(parents=True, exist_ok=True)
    output_file = out_dir / f"{platform}_{file_number}_std_ids_{country_str}_{model}.json"
    failed_file = out_dir / f"{platform}_{file_number}_std_ids_failed_{country_str}_{model}.json"

    platform_dir = id_dir / platform
    reference_paths = next(platform_dir.iterdir())
    
    df_all = pd.read_csv(platform_file)
    df_ref = pd.read_csv(reference_paths)

    ref_set = set(df_ref["final_path"])
    df_all = df_all[~df_all["final_path"].isin(ref_set)].drop_duplicates("final_path")


    refs = str(df_ref["final_path"].tolist())

    chunks = [df_all.iloc[i::num_agents] for i in range(num_agents)]
    jobs = [(chunk, refs, agent, platform, model, out_dir / f"agent_{agent}_{platform}_{file_number}.jsonl")
            for agent, chunk in enumerate(chunks)]

    with get_context("spawn").Pool(processes=num_agents) as pool:
        results = pool.starmap(process_chunk, jobs, chunksize=1)

    output_list = [r for res, _ in results for r in res]
    failures = [x for _, fail in results for x in fail]

    output_file.write_text(json.dumps(output_list, indent=2, ensure_ascii=False), encoding="utf-8")
    failed_file.write_text(json.dumps(failures, indent=2, ensure_ascii=False), encoding="utf-8")

    # Final files are safely on disk, so the agent checkpoints are no longer needed
    for _, _, _, _, _, tmp_file in jobs:
        tmp_file.unlink(missing_ok=True)

    print(f"Finished {platform}: {len(output_list)} ok, {len(failures)} failed", flush=True)

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

    disagreement_dir = Path(f'{disagreements_dir}/{platform}')
    agreement_dir = Path(f'{agreements_dir}/{platform}')
  

    disagreements.to_json(
        disagreement_dir / f"{platform}_id_std_disagreements_{country_str}.json",
        orient="records",
        indent=4)

    agreements.to_json(
            agreement_dir / f"{platform}_id_std_agreements_{country_str}.json",
            orient="records",
            indent=4)



def resolve_disagreements(disagreements_dir, refs, platform, resolved_dir, country_str):

    import json
    from pathlib import Path
    from tqdm import tqdm

    from src.inference import generateInference as gI
    from src.inference.legacy import prompts as p

    
    disagreement_dir = Path(disagreements_dir) / platform
    print('disagreement dir', disagreement_dir)
    disagreement_json = next(disagreement_dir.iterdir())
    print('diagreement json', disagreement_json)

    # Load JSON
    with open(disagreement_json, "r") as f:
        data = json.load(f)

    output_list = []

    for row in tqdm(data, total=len(data), desc=f"Processing {platform}"):

        output = gI.generate_output(
            data_1=row["path"],
            template=p.prompt_std_ids_resolve(),
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
    with open(f"{resolved_dir}/{platform}/{output_file}", "w") as f:
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
    id_dir = Path(id_dir)
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

        

def combine_user_std_paths(user_data_dir, std_path_1_dir, std_path_2_dir):
    user_data_dir = Path(user_data_dir)
    for platform_dir in user_data_dir.iterdir(): 

        platform = platform_dir.name
        std_1_dir = Path(std_path_1_dir)/platform
        std_2_dir = Path(std_path_2_dir)/platform
        std_1 = next(std_1_dir.iterdir())
        std_2 = next(std_2_dir.iterdir())

        std_1_df = pd.read_csv(std_1)
        std_1_df['std_path'] = std_1_df['final_path']

        with open(std_2, "r") as f:
            std_2_json = json.load(f)
        std_2_df = pd.DataFrame(std_2_json)
        std_2_df = std_2_df.rename(columns={
                        "path": "final_path",
                        "estimated_path": "std_path"})

        std_df = pd.concat([std_1_df, std_2_df], ignore_index=True)
        dfs = []

        for csv_file in user_data_dir.glob("*.csv"):
            df = pd.read_csv(csv_file)
            df["source_file"] = csv_file.stem
            dfs.append(df)

        combined = pd.concat(dfs, ignore_index=True)

        df_final = combined.merge(std_df, on="final_path", how="left") 
        
