import os
DATA_ROOT = os.environ.get("ROOT_DIR", "/projects/prjs2007/data_donation")

from src.ingest import extractJson as eJ
from datetime import datetime



#SURF STORAGE NOT MN5!!
input_dir = os.path.join(DATA_ROOT, 'ddd_cleaned')
output_dir = os.path.join(DATA_ROOT, 'ddd_processed/00_ingest/001_json_structures')


print('START ', datetime.now())

def main():
    eJ.extract_josn_from_placeholder_csv(input_dir, output_dir)

if __name__ == "__main__":
    main()

print('FINISH ', datetime.now())
