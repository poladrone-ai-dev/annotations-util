import os
import sys
import xml.etree.ElementTree as ET
import glob
import shutil
import argparse
from pathlib import Path
from PIL import Image

def check_anno(args):
    og_path = os.path.abspath(__file__)
    image_types = ['.png', '.jpg', '.PNG', '.JPG', '.tif', '.jpeg', '.JPEG']
    os.chdir(args.input)

    for image in glob.glob("*"):
        if os.path.splitext(image)[1] in image_types:
            parent_dir = os.path.dirname(image)
            image_name_no_ext = os.path.splitext(os.path.basename(image))[0]
            if not os.path.isfile(os.path.join(parent_dir, image_name_no_ext + ".xml")):
                print(image + " is missing its annotation.")

    os.chdir(os.path.dirname(og_path))

def copy_files(args):
    og_path = os.path.abspath(__file__)
    os.chdir(args.input)

    for file in glob.glob("*"):
        if not os.path.isdir(file):
            dest_filename = os.path.splitext(os.path.basename(file))[0]
            dest_ext = os.path.splitext(os.path.basename(file))[1]
            dest = os.path.join(args.output, dest_filename + "_scale_" + str(args.scale) + dest_ext)
            shutil.copyfile(file, dest)

    os.chdir(os.path.dirname(og_path))

def resize_img(args):
    og_path = os.path.abspath(__file__)
    os.chdir(args.output)

    image_types = ['.png', '.jpg', '.PNG', '.JPG', '.tif', '.jpeg', '.JPEG']

    for image_file in glob.glob("*"):
        if not os.path.isdir(image_file):
            if os.path.splitext(image_file)[1] in image_types:
                print("Resizing " + os.path.basename(image_file) + " by a factor of " + str(args.scale) + "...")
                image = Image.open(image_file)
                width, height = image.size
                image = image.resize((int(width * args.scale), int(height * args.scale)), Image.ANTIALIAS)
                quality_val = 90
                image.save(image_file, 'JPEG', quality=quality_val)

            if image_file.endswith(".xml"):
                et = ET.parse(image_file)
                element = et.getroot()
                element_objs = element.findall('object')
                print("Resizing " + os.path.basename(image_file) + " by a factor of " + str(args.scale) + "...")
                for element_obj in element_objs:
                    obj_bbox = element_obj.find('bndbox')
                    x1 = int(round(float(obj_bbox.find('xmin').text)))
                    y1 = int(round(float(obj_bbox.find('ymin').text)))
                    x2 = int(round(float(obj_bbox.find('xmax').text)))
                    y2 = int(round(float(obj_bbox.find('ymax').text)))

                    obj_bbox.find('xmin').text = str(int(x1 * args.scale))
                    obj_bbox.find('ymin').text = str(int(y1 * args.scale))
                    obj_bbox.find('xmax').text = str(int(x2 * args.scale))
                    obj_bbox.find('ymax').text = str(int(y2 * args.scale))
                    et.write(image_file)

    print("Finished resizing images and xmls.")
    os.chdir(os.path.dirname(og_path))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scale', type=float, required=True, help='scaling factor between 0 to 1')
    parser.add_argument('--input', type=str, required=True, help='path to input image and annotations')
    parser.add_argument('--output', type=str, required=True, help='path to store scaled output')
    args = parser.parse_args()

    if args.scale < 0 or args.scale > 1:
        print("Please enter a valid value for scale.")
        sys.exit()

    if os.path.isdir(args.output):
        shutil.rmtree(args.output)

    os.mkdir(args.output)

    check_anno(args)
    copy_files(args)
    resize_img(args)

main()