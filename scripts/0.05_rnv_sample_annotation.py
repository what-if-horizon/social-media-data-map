from pathlib import Path
import pandas as pd

input_dir = Path('/projects/prjs2007/data_donation/ddd_processed/00_ingest/005_merged_structures')
output_dir = Path("/projects/prjs2007/data_donation/ddd_annotation/sample")

output_dir.mkdir(parents=True, exist_ok=True)

for csv_file in input_dir.glob("*.csv"):
    df = pd.read_csv(csv_file)

    sample = df.sample(
        n=min(100, len(df)),
        random_state=42
    )
    file_name = csv_file.stem
    platform_name = file_name.split("_")[0]
    output_name = f'{file_name}_seed42_100rows.csv'

    output_dir_platform = output_dir / platform_name
    output_dir_platform.mkdir(parents=True, exist_ok=True)

    output_file = output_dir_platform / output_name
    sample.to_csv(output_file, index=False)

    print(f"{output_name}: {len(sample)} rows -> {output_file}")