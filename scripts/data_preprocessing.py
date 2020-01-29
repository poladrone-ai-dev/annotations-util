import argparse
import os
import shutil
import stat
import glob
import random
from pathlib import Path
from kmeans import YOLO_Kmeans
from change_path_name import change_path_name
from context_adding import context_adding
from data_augmentation import data_augmentation
from change_to_darknet_v2 import darknet_convert

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', dest='dataset_path', help='Path to dataset data (images and annotations).', required=True)
parser.add_argument('-o', '--output', dest='output_path', help='Path to save the processed data', required=True)
parser.add_argument('-c', '--context', dest='context', help='Context percentage for context adding (varies between 0 and 1)')
parser.add_argument('--train', type=float, required=False, help="train split (between 0 and 1)", default=0.7)
parser.add_argument('--valid', type=float, required=False, help="valid split (between 0 and 1)", default=0.2)
parser.add_argument('--test', type=float, required=False, help="test split (between 0 and 1)", default=0.1)
parser.add_argument('--labelImg', type=bool, required=False, help="set flag to true if xml file path needs changing", default=False)

args = parser.parse_args()

dataset_path = Path(args.dataset_path)
dataset_path.mkdir(parents=True, exist_ok=True)

output_path = Path(args.output_path)
output_path.mkdir(parents=True, exist_ok=True)

def move_data(input, image, split_type):
	image_basename = os.path.basename(image)
	image_base_no_ext = os.path.splitext(os.path.basename(image))[0]
	image_name = os.path.splitext(image)[0]
	ext = os.path.splitext(image)[1]

	shutil.move(image, os.path.join(input, split_type, image_basename))

	if os.path.isfile(image_name + ".xml"):
		shutil.move(image_name + ".xml", os.path.join(input, split_type, image_base_no_ext + ".xml"))
	if os.path.isfile(image_name + ".txt"):
		shutil.move(image_name + ".txt", os.path.join(input, split_type, image_base_no_ext + ".txt"))

def train_valid_split(input, image_count, train_valid_count):
	augmentations = ["-f0", "-f1", "_gaussian_blur"]
	random.seed(123)
	image_files = []

	try:
		percentage = (image_count * args.train) / train_valid_count
		print("Train Percentage: " + str(percentage))

	except ZeroDivisionError:
		print("Divide by 0 error.")
		sys.exit()

	for image_file in glob.glob(os.path.join(input, "*.jpg")):
		image_files.append(image_file)

	random.shuffle(image_files)
	split_index = int(percentage * len(image_files))

	train_data = image_files[:split_index]
	valid_data = image_files[split_index:]

	for image in train_data:
		move_data(input, image, "train")

	for image in valid_data:
		move_data(input, image, "valid")


def split_test_data(input, image_count):

	no_augment_images = []
	test_data = []
	augmentations = ["-f0", "-f1", "_gaussian_blur"]

	for image_file in glob.glob(os.path.join(input, "*.jpg")):
		noAug = True
		for augmentation in augmentations:
			if augmentation in image_file:
				noAug = False
		if noAug == True:
			no_augment_images.append(image_file)

	while len(test_data) <= int(args.test * (len(augmentations) + 1) * len(no_augment_images)):
		image = random.choice(no_augment_images)
		if not image in test_data:
			image_basename = os.path.basename(image)
			image_base_no_ext = os.path.splitext(os.path.basename(image))[0]
			image_name = os.path.splitext(image)[0]
			ext = os.path.splitext(image)[1]

			test_data.append(image)
			test_data.append(image_name + "-f0" + ext)
			test_data.append(image_name + "-f1" + ext)
			test_data.append(image_name + "_gaussian_blur" + ext)

			shutil.move(image, os.path.join(input, "test", image_basename))
			shutil.move(image_name + ".xml", os.path.join(input, "test", image_base_no_ext + ".xml"))
			shutil.move(image_name + ".txt", os.path.join(input, "test", image_base_no_ext + ".txt"))

			for augmentation in augmentations:
				shutil.move(image_name + augmentation + ext, os.path.join(input, "test", image_base_no_ext + augmentation + ext))
				shutil.move(image_name + augmentation + ".xml", os.path.join(input, "test", image_base_no_ext + augmentation + ".xml"))
				shutil.move(image_name + augmentation + ".txt", os.path.join(input, "test", image_base_no_ext + augmentation + ".txt"))

			no_augment_images.remove(image)

	return image_count - len(test_data)

if __name__ == "__main__":

	if args.labelImg:
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

	if os.path.isdir(os.path.join(output_path, "augmentation_result", "train")):
		shutil.rmtree(os.path.join(output_path, "augmentation_result", "train"))

	os.mkdir(os.path.join(output_path, "augmentation_result", "train"))

	if os.path.isdir(os.path.join(output_path, "augmentation_result", "valid")):
		shutil.rmtree(os.path.join(output_path, "augmentation_result", "valid"))

	os.mkdir(os.path.join(output_path, "augmentation_result", "valid"))

	if os.path.isdir(os.path.join(output_path, "augmentation_result", "test")):
		shutil.rmtree(os.path.join(output_path, "augmentation_result", "test"))

	os.mkdir(os.path.join(output_path, "augmentation_result", "test"))

	darknet_output_path = os.path.join(output_path, "darknet_output")

	if os.path.isdir(darknet_output_path):
		shutil.rmtree(darknet_output_path)

	darknet_convert(bbox_file, darknet_output_path, class_file, args.train, args.valid, args.test)

	cluster_number = 9
	kmeans = YOLO_Kmeans(cluster_number, bbox_file)
	kmeans.txt2clusters(darknet_output_path)

	image_count = 0
	for image_file in glob.glob(os.path.join(output_path, "augmentation_result", "*.jpg")):
		image_count += 1

	train_valid_count = split_test_data(os.path.join(output_path, "augmentation_result"), image_count)
	train_valid_split(os.path.join(output_path, "augmentation_result"), image_count, train_valid_count)
