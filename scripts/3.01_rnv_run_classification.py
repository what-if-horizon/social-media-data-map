
import pandas as pd
from src.inference import classification as c

project_root = '/home/bsc/bsc093754/GIT/social-media-data-map/'

input_file = f'{project_root}data/processed/inference_sample.csv'
output_dir = f'{project_root}data/processed/'
platform = 'Facebook'


def main():
    c.run_classification(input_file, output_dir, platform)

if __name__ == "__main__":
    main()