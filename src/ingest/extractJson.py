
import pandas as pd
from pathlib import Path
import json
from tqdm import tqdm


def extract_josn_from_placeholder_csv(input_dir, output_dir):

    input_dir = Path(input_dir)
    for platform_dir in input_dir.iterdir():
        platform = platform_dir.parts[-1]
        print(f'Processing platform: {platform}')
        for folder in platform_dir.iterdir():
            
            if folder.parts[-1] != 'placeholder':
                continue

            files = list(folder.iterdir())
            for file in tqdm(files, desc=f"Processing files of platform: {platform}"):
                file_name = file.stem
                df = pd.read_csv(file)


                if df['placeholder_for_research_purpose'].notna().any():
                    json_str = df['placeholder_for_research_purpose'].dropna().iloc[0]
                else:
                    json_str = df['anonymized_data_structure'].dropna().iloc[0]

                #print(str(json_str))
                #print(type(json_str))
    
                #json_str = json.loads(json_str)
                json_str = json.dumps(json_str, indent = 2)
                with open(f'{output_dir}/{platform}/{file_name}.json', "w") as f:
                    f.write(json_str)
                