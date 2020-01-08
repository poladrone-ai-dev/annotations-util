import os
import fileinput
import sys
import random
import shutil
import stat
from PIL import Image

classes = []

def move_files(output_path):

    if os.path.isdir(os.path.join(output_path, "train")):
        shutil.rmtree(os.path.join(output_path, "train"))

    if os.path.isdir(os.path.join(output_path, "valid")):
        shutil.rmtree(os.path.join(output_path, "valid"))

    if os.path.isdir(os.path.join(output_path, "test")):
        shutil.rmtree(os.path.join(output_path, "test"))

    os.mkdir(os.path.join(output_path, "train"))
    os.mkdir(os.path.join(output_path, "valid"))
    os.mkdir(os.path.join(output_path, "test"))

    with open(os.path.join(output_path, "train.txt")) as train_file:
        for line in train_file:
            image_source = line.replace("\n", "")
            image_dest = os.path.join(output_path, "train", os.path.basename(image_source))
            shutil.copyfile(image_source, image_dest)

            label_file = os.path.basename(line).replace(".jpg\n", ".txt")
            label_source = os.path.join(output_path, "label", label_file)
            label_dest = os.path.join(output_path, "train", os.path.basename(label_source))
            shutil.copyfile(label_source, label_dest)

    with open(os.path.join(output_path, "valid.txt")) as valid_file:
        for line in valid_file:
            image_source = line.replace("\n", "")
            image_dest = os.path.join(output_path, "valid", os.path.basename(image_source))
            shutil.copyfile(image_source, image_dest)

            label_file = os.path.basename(line).replace(".jpg\n", ".txt")
            label_source = os.path.join(output_path, "label", label_file)
            label_dest = os.path.join(output_path, "valid", os.path.basename(label_source))
            shutil.copyfile(label_source, label_dest)

    with open(os.path.join(output_path, "test.txt")) as test_file:
        for line in test_file:
            image_source = line.replace("\n", "")
            image_dest = os.path.join(output_path, "test", os.path.basename(image_source))
            shutil.copyfile(image_source, image_dest)

            label_file = os.path.basename(line).replace(".jpg\n", ".txt")
            label_source = os.path.join(output_path, "label", label_file)
            label_dest = os.path.join(output_path, "test", os.path.basename(label_source))
            shutil.copyfile(label_source, label_dest)

def file_len(fname):
    with open(fname) as f:
        count = sum(1 for _ in f)

    return count

def split_test_data(file, output_path, test_split):
    num_data = sum(1 for line in open(file))
    all_data = []
    all_data_no_augment = []
    train_data = []
    test_data = []

    with open(file, 'r', encoding="utf-8") as fp:
        for line in fp:
            all_data.append(line.replace("\n", ""))

    all_data_no_augment = [data for data in all_data if "-f0." not in data and "-f1." not in data]

    while len(test_data) <= int(test_split * num_data):
        filename = all_data_no_augment[random.randrange(len(all_data_no_augment)) ]
        filename_no_ext = filename[:-4]
        filename_vflip = filename_no_ext + "-f0.jpg"
        filename_hflip = filename_no_ext + "-f1.jpg"

        if filename_vflip in all_data and filename_hflip in all_data:
            test_data.append(filename)
            test_data.append(filename_vflip)
            test_data.append(filename_hflip)
            all_data.remove(filename)
            all_data.remove(filename_vflip)
            all_data.remove(filename_hflip)
            num_data -= 3

    if os.path.isfile(os.path.join(output_path, "train_valid.txt")):
        os.remove(os.path.join(output_path, "train_valid.txt"))

    if os.path.isfile(os.path.join(output_path, "test.txt")):
        os.remove(os.path.join(output_path, "test.txt"))

    with open(os.path.join(output_path, "train_valid.txt"), 'a') as train_file:
        for line in all_data:
            train_file.write(line + "\n")

    with open(os.path.join(output_path, "test.txt"), 'a') as test_file:
        for line in test_data:
            test_file.write(line + "\n")

    train_valid_len = file_len(os.path.join(output_path, "train_valid.txt"))

    return [len(all_data) , train_valid_len]

def split_file(file, out1, out2, file_count, train_split, seed=123):
    """Splits a file in 2 given the `percentage` to go in the large file."""
    random.seed(seed)
    all_count = file_count[0]
    train_valid_count = file_count[1]

    try:
        percentage = (all_count * train_split) / train_valid_count
    except ZeroDivisionError:
        print("Divide by 0 error.")
        sys.exit()

    with open(file, 'r', encoding="utf-8") as fin, \
            open(out1, 'w') as foutBig, \
            open(out2, 'w') as foutSmall:

        for line in fin:
            r = random.random()
            if r < percentage:
                foutBig.write(line)
            else:
                foutSmall.write(line)

seen_lines = []  # stored seen lines here so that no lines written are duplicated

def darknet_convert(bbox_file, output_path, classes_file, train_split=0.7, valid_split=0.2, test_split=0.1):

    filename_file = os.path.join(output_path, "filename.txt")
    if train_split > 1.0 or test_split > 1.0 or valid_split > 1.0:
        print("One of the data split is greater than 1. Please enter correct data split again.")
        sys.exit()

    if train_split < 0 or test_split < 0 or valid_split < 0:
        print("One of the data split is less than 0. Please enter correct data split again.")
        sys.exit()

    if os.path.isfile(filename_file):
        os.remove(filename_file)

    with open(classes_file) as class_fp:
        for line in class_fp:
            classes.append(line.replace("\n", ""))

    if os.path.isdir(output_path):
        shutil.rmtree(output_path)

    os.mkdir(output_path)

    if os.path.isdir(os.path.join(output_path, "label")):
        shutil.rmtree(os.path.join(output_path, "label"))

    os.mkdir(os.path.join(output_path, "label"))

    with open(bbox_file, 'r') as fp:
        for line in fp:
            filename_no_ext = line.split(' ')[0][:-4]
            image_filename = line.split(" ")[0]
            values = line.split(' ')[1].split(',')
            values[-1] = values[-1].replace('\n', '')
            label_file = os.path.join(output_path, "label", os.path.basename(filename_no_ext) + '.txt')
            image_file = line.split(' ')[0]

            try:
                im = Image.open(image_filename)
                WIDTH, HEIGHT = im.size
            except:
                print("Could not find " + image_filename + ". Please check that image exists.")

            print("Image: " + image_filename)

            x_center = (int(values[2]) + int(values[0])) / (2 * WIDTH)
            y_center = (int(values[3]) + int(values[1])) / (2 * HEIGHT)
            box_width = (int(values[2]) - int(values[0])) / WIDTH
            box_height = (int(values[3]) - int(values[1])) / HEIGHT
            class_index = int(classes.index(values[4]))

            print("Class index: " + str(class_index))
            print("X_center: " + str(x_center))
            print("Y_center: " + str(y_center))
            print("Box_width: " + str(box_width))
            print("Box_height: " + str(box_height))
            print('\n')

            anno = str(class_index) + " " + str(x_center) + " " + str(y_center) + " " + str(box_width) + " " + str(box_height) + '\n'

            with open(filename_file, 'a') as train_fp:
                os.chmod(filename_file, stat.S_IWUSR)
                if image_file not in seen_lines:
                    train_fp.write(image_file)
                    train_fp.write('\n')
                    seen_lines.append(image_file)

            with open(label_file, 'a') as out_fp:
                out_fp.write(anno)

    [all_count, train_valid_count] = split_test_data(os.path.join(output_path, filename_file), output_path, test_split)

    print("All count: " + str(all_count))
    print("train valid count: " + str(train_valid_count))

    if all_count != 0 and split_file != 0:
        split_file(os.path.join(output_path, "train_valid.txt"),
                   os.path.join(output_path, "train.txt"),
                   os.path.join(output_path, "valid.txt"),
                   [all_count, train_valid_count],
                   train_split
        )

        move_files(output_path)

        if os.path.isfile(os.path.join(output_path, "train_valid.txt")):
            os.remove(os.path.join(output_path, "train_valid.txt"))

    os.remove(filename_file)
