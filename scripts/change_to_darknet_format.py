import os
import fileinput
import sys

filepath = r'D:\training_data\mature_5\combined\result\combined\bbox2.txt'
image_path = r'D:\PyTorch-YOLOv3-master\data\custom\labels'

classes = ['palm0', 'palm2']
WIDTH = 500
HEIGHT = 500
current_file = r''

with open(filepath, 'r') as fp:
    for line in fp:
        filename = line.split(',')[:1][0][:-4]
        values = line.split(',')[1:]
        values[-1] = values[-1].replace('\n', '')
        current_file = os.path.join(image_path, filename + '.txt')

        x_center = (int(values[2]) + int(values[0])) / (2 * WIDTH)
        y_center = (int(values[3]) + int(values[1])) / (2 * HEIGHT)
        box_width = (int(values[2]) - int(values[0])) / WIDTH
        box_height = (int(values[3]) - int(values[1])) / HEIGHT
        class_index = classes.index(values[4])
        anno = str(class_index) + " " + str(x_center) + " " + str(y_center) + " " + str(box_width) + " " + str(box_height) + '\n'

        print(current_file)

        # if os.path.exists(filename):
        #     append_write = 'a'
        # else:
        #     append_write = 'w'

        with open(current_file, 'a') as out_fp:
            out_fp.write(anno)


