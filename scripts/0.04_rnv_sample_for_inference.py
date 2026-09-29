from pathlib import Path
import random
import shutil

source_dir = Path('/projects/prjs2007/data_donation/ddd_processed/00_ingest/005_merged_structures')
sample_dir = Path('/projects/prjs2007/data_donation/ddd_sample/00_ingest/005_merged_structures')

for platform in source_dir.iterdir():
    if platform.is_dir():
        platform_name = platform.name

        sample_platform_dir = sample_dir / platform_name

        sample_platform_dir.mkdir(parents=True, exist_ok=True)

        files = list(source_dir.glob(f"{platform_name}_merged_structures_*.csv"))

        # Randomly select 3 files
        sample_files = random.sample(files, 3)

        for file in sample_files:
            shutil.copy2(file, sample_dir / file.name)
            print(f"Copied: {file.name}")