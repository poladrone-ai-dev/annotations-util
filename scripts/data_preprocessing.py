import argparse
from pathlib import Path
import os
from change_path_name import change_path_name
from context_adding import context_adding
from data_augmentation import data_augmentation
# from change_csv_file import change_csv_file

parser = argparse.ArgumentParser()

parser.add_argument(
'-i',
'--input',
dest='dataset_path',
help='Path to dataset data (images and annotations).',
required=True)

parser.add_argument(
'-o',
'--output',
dest='output_path',
help='Path to save the processed data',
required=True)

# context varies between 0 and 1
parser.add_argument(
'-c',
'--context',
dest='context',
help='Context percentage for context adding (varies between 0 and 1)')

args = parser.parse_args()

dataset_path = Path(args.dataset_path)
dataset_path.mkdir(parents=True, exist_ok=True)

output_path = Path(args.output_path)
output_path.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
	change_path_name(dataset_path, output_path)
	if (args.context):
		context_adding(dataset_path, args.context)
	else:
		# default context == 0
		context_adding(dataset_path, 0)
	data_augmentation(dataset_path, output_path)
