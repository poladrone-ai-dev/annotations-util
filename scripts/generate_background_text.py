import glob
import os
import sys

image_path = r'D:\training_data\background_data\image'
anno_path = r'D:\training_data\background_data\annotations'

os.chdir(image_path)

for image in glob.glob('*.jpg'):

    image_name = os.path.basename(image)[:-4]
    anno_name = os.path.join(anno_path, image_name + '.txt')

    print(anno_name)

    with open(anno_name, 'w') as fp:
        pass

    pass