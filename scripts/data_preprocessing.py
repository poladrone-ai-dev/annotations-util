import argparse
import os
import shutil
import stat
from pathlib import Path
from change_path_name import change_path_name
from context_adding import context_adding
from data_augmentation import data_augmentation
from change_to_darknet_v2 import darknet_convert
# from change_csv_file import change_csv_file

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input', dest='dataset_path', help='Path to dataset data (images and annotations).', required=True)

parser.add_argument('-o', '--output', dest='output_path', help='Path to save the processed data', required=True)

# context varies between 0 and 1
parser.add_argument('-c', '--context', dest='context', help='Context percentage for context adding (varies between 0 and 1)')

parser.add_argument('--train', type=float, required=False, help="train split (between 0 and 1)", default=0.7)
parser.add_argument('--valid', type=float, required=False, help="valid split (between 0 and 1)", default=0.2)
parser.add_argument('--test', type=float, required=False, help="test split (between 0 and 1)", default=0.1)

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

	if os.path.isdir(os.path.join(output_path, "augmentation_result")):
		os.chmod(os.path.join(output_path, "augmentation_result"), stat.S_IWUSR)
		shutil.rmtree(os.path.join(output_path, "augmentation_result"))

	os.mkdir(os.path.join(output_path, "augmentation_result"))

	augmentation_output_path = os.path.join(output_path, "augmentation_result")
	data_augmentation(dataset_path, augmentation_output_path)

	bbox_file = os.path.join(output_path, "augmentation_result", "bb_box.txt")
	class_file = os.path.join(output_path, "augmentation_result", "classes.txt")

	darknet_output_path = os.path.join(output_path, "darknet_output")
	darknet_convert(bbox_file, darknet_output_path, class_file, args.train, args.valid, args.test)
