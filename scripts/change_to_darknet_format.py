import os
import fileinput
import sys
import random

filepath = r'D:\testing_data\things_to_annotate_jpg\combined\combined\result\bb_box.txt'
label_path = r'D:\PyTorch-YOLOv3-master\data\custom\labels'
image_path = r'D:\PyTorch-YOLOv3-master\data\custom\images'
filename_file = r'D:\PyTorch-YOLOv3-master\data\custom\filename.txt'
valid_file = r'D:\PyTorch-YOLOv3-master\data\custom\valid.txt'

classes = ['0', '1', '2', '3'] # fill this with your class names
WIDTH = 500
HEIGHT = 500
current_file = r''

palm0_count = 0
palm1_count = 0
palm2_count = 0
palm3_count = 0

def split_file(file,out1,out2,percentage=0.8,isShuffle=True,seed=123):
    """Splits a file in 2 given the `percentage` to go in the large file."""
    random.seed(seed)
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

with open(filepath, 'r') as fp:
    for line in fp:
        filename = line.split(' ')[0][:-4]
        values = line.split(' ')[1].split(',')
        values[-1] = values[-1].replace('\n', '')
        current_file = os.path.join(label_path, filename + '.txt')
        image_file = os.path.join(image_path, os.path.basename(filename) + '.jpg')

        x_center = (int(values[2]) + int(values[0])) / (2 * WIDTH)
        y_center = (int(values[3]) + int(values[1])) / (2 * HEIGHT)
        box_width = (int(values[2]) - int(values[0])) / WIDTH
        box_height = (int(values[3]) - int(values[1])) / HEIGHT

        # multiclass training
        class_index = int(classes.index(values[4]))

        if class_index == 0:
            palm0_count += 1

        if class_index == 1:
            palm1_count += 1

        if class_index == 2:
            palm2_count += 1

        if class_index == 3:
            palm3_count += 1

        anno = str(class_index) + " " + str(x_center) + " " + str(y_center) + " " + str(box_width) + " " + str(box_height) + '\n'

        with open(filename_file, 'a') as train_fp:
            if image_file not in seen_lines:
                train_fp.write(image_file)
                train_fp.write('\n')
                seen_lines.append(image_file)

        with open(current_file, 'a') as out_fp:
            out_fp.write(anno)

split_file(r'D:\PyTorch-YOLOv3-master\data\custom\filename.txt',
           r'D:\PyTorch-YOLOv3-master\data\custom\train.txt',
           r'D:\PyTorch-YOLOv3-master\data\custom\valid.txt')

os.remove(filename_file)

print("Palm0 count: " + str(palm0_count))
print("Palm1 count: " + str(palm1_count))
print("Palm2 count: " + str(palm2_count))
print("Palm3 count: " + str(palm3_count))