
import pandas as pd

def extract_josn_from_placeholder_csv(root_dir, ouput_dir):
    for platform_dir in root_dir.iterdir():
        for p in platform_dir.rglob("placeholder"):
            file_name = p.name
            df = pd.read_csv(p)
            json_str = df['anonymized_data_structure']

            with open(f'{output_dir}/{file_name}.json', "w") as f:
                f.write(json_str)
                