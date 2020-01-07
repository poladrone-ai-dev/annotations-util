import os
import fileinput
import sys
import random
import argparse
import shutil
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, required=True, help="input text file with name and bbox")
parser.add_argument("--output", type=str, required=True, help="output directory for conversion")
parser.add_argument("--train", type=float, required=True, help="training data split (0-1)")
parser.add_argument("--test", type=float, required=True, help="test data split (0-1)")
parser.add_argument("--valid", type=float, required=True, help="valid data split (0-1)")
parser.add_argument("--classes", type=str, required=True, help="text file with class names")
opt = parser.parse_args()

filepath = opt.input
# image_path = os.path.join(opt.output, "images")
filename_file = os.path.join(opt.output, "filename.txt")

classes = [] # fill this with your class names
current_file = r''

def move_files():

    if os.path.isdir(os.path.join(opt.output, "train")):
        shutil.rmtree(os.path.join(opt.output, "train"))

    if os.path.isdir(os.path.join(opt.output, "valid")):
        shutil.rmtree(os.path.join(opt.output, "valid"))

    if os.path.isdir(os.path.join(opt.output, "test")):
        shutil.rmtree(os.path.join(opt.output, "test"))

    os.mkdir(os.path.join(opt.output, "train"))
    os.mkdir(os.path.join(opt.output, "valid"))
    os.mkdir(os.path.join(opt.output, "test"))

    with open(os.path.join(opt.output, "train.txt")) as train_file:
        for line in train_file:
            image_source = line.replace("\n", "")
            image_dest = os.path.join(opt.output, "train", os.path.basename(image_source))
            shutil.copyfile(image_source, image_dest)

            label_source = line.replace(".jpg\n", ".txt")
            label_dest = os.path.join(opt.output, "train", os.path.basename(label_source))
            shutil.copyfile(label_source, label_dest)

    with open(os.path.join(opt.output, "valid.txt")) as valid_file:
        for line in valid_file:
            image_source = line.replace("\n", "")
            image_dest = os.path.join(opt.output, "valid", os.path.basename(image_source))
            shutil.copyfile(image_source, image_dest)

            label_source = line.replace(".jpg\n", ".txt")
            label_dest = os.path.join(opt.output, "valid", os.path.basename(label_source))
            shutil.copyfile(label_source, label_dest)

    with open(os.path.join(opt.output, "test.txt")) as test_file:
        for line in test_file:
            image_source = line.replace("\n", "")
            image_dest = os.path.join(opt.output, "test", os.path.basename(image_source))
            shutil.copyfile(image_source, image_dest)

            label_source = line.replace(".jpg\n", ".txt")
            label_dest = os.path.join(opt.output, "test", os.path.basename(label_source))
            shutil.copyfile(label_source, label_dest)

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def split_test_data(file):
    num_data = sum(1 for line in open(file))
    print(num_data)

    all_data = []
    all_data_no_augment = []
    train_data = []
    test_data = []

    with open(file, 'r', encoding="utf-8") as fp:
        for line in fp:
            all_data.append(line.replace("\n", ""))

    all_data_no_augment = [data for data in all_data if "-f0." not in data and "-f1." not in data]

    while len(test_data) <= int(opt.test * num_data):
        filename = all_data_no_augment[random.randrange(len(all_data_no_augment)) ]
        filename_no_ext = filename[:-4]
        filename_vflip = filename_no_ext + "-f0.jpg"
        filename_hflip = filename_no_ext + "-f1.jpg"
        # print("Filename: " + filename)
        # print("vflip: " + filename_vflip)
        # print("hflip: " + filename_hflip)

        if filename_vflip in all_data and filename_hflip in all_data:
            test_data.append(filename)
            test_data.append(filename_vflip)
            test_data.append(filename_hflip)
            all_data.remove(filename)
            all_data.remove(filename_vflip)
            all_data.remove(filename_hflip)
            num_data -= 3

    if os.path.isfile(os.path.join(opt.output, "train_valid.txt")):
        os.remove(os.path.join(opt.output, "train_valid.txt"))

    if os.path.isfile(os.path.join(opt.output, "test.txt")):
        os.remove(os.path.join(opt.output, "test.txt"))

    with open(os.path.join(opt.output, "train_valid.txt"), 'a') as train_file:
        for line in all_data:
            train_file.write(line + "\n")

    with open(os.path.join(opt.output, "test.txt"), 'a') as test_file:
        for line in test_data:
            test_file.write(line + "\n")

    train_valid_len = file_len(os.path.join(opt.output, "train_valid.txt"))
    print(train_valid_len)

    return [len(all_data) , train_valid_len]

def split_file(file, out1, out2, file_count, seed=123):
    """Splits a file in 2 given the `percentage` to go in the large file."""
    random.seed(seed)
    all_count = file_count[0]
    train_valid_count = file_count[1]

    percentage = (all_count * opt.train) / train_valid_count

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

if __name__ == "__main__":

    # if opt.train + opt.test + opt.valid != 1:
    #     print(opt.train + opt.test + opt.valid)
    #     print("Data split does not add up to 1. Please enter the correct data split again.")
    #     sys.exit()

    if opt.train > 1.0 or opt.test > 1.0 or opt.valid > 1.0:
        print("One of the data split is greater than 1. Please enter correct data split again.")
        sys.exit()

    if opt.train < 0 or opt.test < 0 or opt.valid < 0:
        print("One of the data split is less than 0. Please enter correct data split again.")
        sys.exit()

    if os.path.isfile(filename_file):
        os.remove(filename_file)

    with open(opt.classes) as class_fp:
        for line in class_fp:
            classes.append(line.replace("\n", ""))

    with open(filepath, 'r') as fp:
        for line in fp:
            filename_no_ext = line.split(' ')[0][:-4]
            image_filename = line.split(" ")[0]
            values = line.split(' ')[1].split(',')
            values[-1] = values[-1].replace('\n', '')
            current_file = os.path.join(opt.output, filename_no_ext + '.txt')
            image_file = line.split(' ')[0]

            try:
                im = Image.open(image_filename)
                WIDTH, HEIGHT = im.size
            except:
                print("Could not find " + image_filename + ". Please check that image exists.")

            x_center = (int(values[2]) + int(values[0])) / (2 * WIDTH)
            y_center = (int(values[3]) + int(values[1])) / (2 * HEIGHT)
            box_width = (int(values[2]) - int(values[0])) / WIDTH
            box_height = (int(values[3]) - int(values[1])) / HEIGHT

            # multiclass training
            class_index = int(classes.index(values[4]))

            anno = str(class_index) + " " + str(x_center) + " " + str(y_center) + " " + str(box_width) + " " + str(box_height) + '\n'
            # anno = str(class_index) + " " + str(int(values[0])) + " " + str(int(values[1])) + " " + str(int(values[2])) + " " + \
            #        str(int(values[3])) + '\n'

            # print("output: " + opt.output)
            # print("current file: " + current_file)
            print(image_file)
            with open(filename_file, 'a') as train_fp:
                if image_file not in seen_lines:
                    train_fp.write(image_file)
                    train_fp.write('\n')
                    seen_lines.append(image_file)

            with open(current_file, 'a') as out_fp:
                out_fp.write(anno)

    [all_count, train_valid_count] = split_test_data(os.path.join(opt.output, filename_file))

    split_file(os.path.join(opt.output, "train_valid.txt"),
               os.path.join(opt.output, "train.txt"),
               os.path.join(opt.output, "valid.txt"),
               [all_count, train_valid_count]
    )

    # os.remove(filename_file)
    # os.remove(os.path.join(opt.output, "train_valid.txt"))

    move_files()
