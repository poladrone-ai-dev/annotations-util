import argparse
import os
import shutil
import stat
import glob
import random
import sys
import time
from pathlib import Path
from kmeans import YOLO_Kmeans
from change_path_name import change_path_name
from context_adding import context_adding
from data_augmentation import data_augmentation
from change_to_darknet_v2 import darknet_convert

parser = argparse.ArgumentParser()
parser.add_argument('--config', required=True, help="config file with project names")
parser.add_argument('-c', '--context', dest='context', help='Context percentage for context adding (varies between 0 and 1)')
parser.add_argument('--train', type=float, required=False, help="train split (between 0 and 1)", default=0.7)
parser.add_argument('--valid', type=float, required=False, help="valid split (between 0 and 1)", default=0.2)
parser.add_argument('--test', type=float, required=False, help="test split (between 0 and 1)", default=0.1)
# parser.add_argument('--labelImg', type=bool, required=False, help="set flag to true if xml file path needs changing", default=False)

args = parser.parse_args()

def CheckForMissingXML(input):
    print("Checking for images with missing xml in " + input + "...")
    noMissingFile = True
    for image_file in glob.glob(os.path.join(input, "*.jpg")):
        image_name = os.path.splitext(image_file)[0]
        if not os.path.isfile(image_name + ".xml"):
            print(image_file + " is missing its xml.")
            noMissingFile = False

    if noMissingFile:
        print("All image files have their corresponding xmls.")

def move_data(input, image, split_type):
    image_basename = os.path.basename(image)
    image_base_no_ext = os.path.splitext(os.path.basename(image))[0]
    image_name = os.path.splitext(image)[0]

    try:
        shutil.copyfile(image, os.path.join(input, split_type, image_basename))
        shutil.copyfile(image_name + ".xml", os.path.join(input, split_type, image_base_no_ext + ".xml"))
        shutil.copyfile(image_name + ".txt", os.path.join(input, split_type, image_base_no_ext + ".txt"))
    except Exception as e:
        print(e)

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
    all_images = []
    no_augment_images = []
    test_data = []
    augmentations = ["-f0", "-f1", "_gaussian_blur"]

    for image_file in glob.glob(os.path.join(input, "*.jpg")):
        all_images.append(image_file)
        noAug = True
        for augmentation in augmentations:
            if augmentation in image_file:
                noAug = False
        if noAug == True:
            no_augment_images.append(image_file)

    while len(test_data) <= int(args.test * len(all_images)):
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

            shutil.copyfile(image, os.path.join(input, "test", image_basename))
            shutil.copyfile(image_name + ".xml", os.path.join(input, "test", image_base_no_ext + ".xml"))
            shutil.copyfile(image_name + ".txt", os.path.join(input, "test", image_base_no_ext + ".txt"))

            for augmentation in augmentations:
                shutil.copyfile(image_name + augmentation + ext, os.path.join(input, "test", image_base_no_ext + augmentation + ext))
                shutil.copyfile(image_name + augmentation + ".xml", os.path.join(input, "test", image_base_no_ext + augmentation + ".xml"))
                shutil.copyfile(image_name + augmentation + ".txt", os.path.join(input, "test", image_base_no_ext + augmentation + ".txt"))
                all_images.remove(image_name + augmentation + ext)

            no_augment_images.remove(image)
            all_images.remove(image)

        return image_count - len(test_data)

if __name__ == "__main__":

    if not os.path.isfile(args.config):
        print("Could not find config file.")
        sys.exit()

    projects = []

    with open(args.config, 'r') as fp:
        for line in fp:
            projects.append(line.replace('\n', ''))

    for project in projects:
        print("<<<<<<<<<<<<<<<<<<<<<Performing data preprocessing for " + project + "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

        project_path = os.path.join(os.path.dirname(args.config), project)
        start_time = time.time()
        CheckForMissingXML(project_path)

        change_path_start_time = time.time()
        #if args.labelImg:
        change_path_name(project_path, project_path)
        change_path_end_time = time.time()

        if (args.context):
            context_adding(project_path, args.context)

        if os.path.isdir(os.path.join(project_path, "augmentation_result")):
            os.chmod(os.path.join(project_path, "augmentation_result"), stat.S_IWUSR)
            shutil.rmtree(os.path.join(project_path, "augmentation_result"))

        os.mkdir(os.path.join(project_path, "augmentation_result"))

        augmentation_output_path = os.path.join(project_path, "augmentation_result")

        augmentation_start_time = time.time()
        data_augmentation(project_path, augmentation_output_path)
        augmentation_end_time = time.time()

        bbox_file = os.path.join(project_path, "augmentation_result", "bb_box.txt")
        class_file = os.path.join(project_path, "augmentation_result", "classes.txt")

        if os.path.isdir(os.path.join(project_path, "augmentation_result", "train")):
            shutil.rmtree(os.path.join(project_path, "augmentation_result", "train"))

        os.mkdir(os.path.join(project_path, "augmentation_result", "train"))

        if os.path.isdir(os.path.join(project_path, "augmentation_result", "valid")):
            shutil.rmtree(os.path.join(project_path, "augmentation_result", "valid"))

        os.mkdir(os.path.join(project_path, "augmentation_result", "valid"))

        if os.path.isdir(os.path.join(project_path, "augmentation_result", "test")):
            shutil.rmtree(os.path.join(project_path, "augmentation_result", "test"))

        os.mkdir(os.path.join(project_path, "augmentation_result", "test"))

        darknet_output_path = os.path.join(project_path, "darknet_output")

        if os.path.isdir(darknet_output_path):
            shutil.rmtree(darknet_output_path)

        darknet_start_time = time.time()
        darknet_convert(bbox_file, darknet_output_path, class_file, args.train, args.valid, args.test)
        darknet_end_time = time.time()

        cluster_number = 9
        kmeans = YOLO_Kmeans(cluster_number, bbox_file)
        kmeans.txt2clusters(darknet_output_path)

        image_count = 0
        for image_file in glob.glob(os.path.join(project_path, "augmentation_result", "*.jpg")):
            image_count += 1

        train_test_split_start_time = time.time()
        train_valid_count = split_test_data(os.path.join(project_path, "augmentation_result"), image_count)
        train_valid_split(os.path.join(project_path, "augmentation_result"), image_count, train_valid_count)
        train_test_split_end_time = time.time()

        end_time = time.time()

        print("Total time elapsed: " + str(end_time - start_time) + "s.")
        print("Change path time elapsed: " + str(change_path_end_time - change_path_start_time) + "s.")
        print("Augmentation time elapsed: " + str(augmentation_end_time - augmentation_start_time) + "s.")
        print("Darknet time elapsed: " + str(darknet_end_time - darknet_start_time) + "s.")
        print("Train test split elapsed: " + str(train_test_split_end_time - train_test_split_start_time) + "s.")
