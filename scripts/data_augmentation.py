
"""
Executable script on terminal 
-Modified from https://medium.co
if not os.path.exists(converted_annotation_in_txt_file):
    os.makedirs(converted_annotm/@bhuwanbhattarai/image-data-augmentation-and-parsing-into-an-xml-file-in-pascal-voc-format-for-object-detection-4cca3d24b33b
Specify the
@input_path dataset which consists of images and XML annotation in Pascal VOC Format and
@output_path for the augmented dataset.

"""

import cv2
import numpy as np
import os
import xml.etree.ElementTree as ET
from PIL import Image
import shutil

def imgAugmentation(imgPath, output_path):
    img = cv2.imread(imgPath)
    newName = imgPath.split("\\") 
    newName = newName[-1]
    # copy original image
    new_path = os.path.join(output_path, newName)
    if not os.path.isfile(new_path):
        cv2.imwrite(new_path, img)
    f_points = [0, 1]
    for f in f_points:
        f_img = cv2.flip(img, f)
        newName = imgPath.split("\\") 
        newName = newName[-1].split('.')
        newName = newName[0] + '-f' + str(f) + '.jpg'
        new_path = os.path.join(output_path, newName)

        if not os.path.isfile(new_path):
            cv2.imwrite(new_path, f_img)

def data_augmentation(input_path, output_path):
    print("Augmenting the Data...")
    # output bounding box text file
    out_path = "{}\\bb_box.txt".format(output_path)

    xml_paths = [os.path.join(input_path, s) for s in os.listdir(input_path)]

    for xml_file in xml_paths:
        if xml_file.endswith(".jpg"):
            imgAugmentation(xml_file, output_path)

    pwd_lines = []
    for xml_file in xml_paths:
        if xml_file.endswith(".xml"):
            et = ET.parse(xml_file)
            element = et.getroot()
            element_objs = element.findall('object') 
            element_filename = element.find('filename').text
            base_filename = os.path.join(input_path, element_filename)                              
            img = cv2.imread(base_filename)
            print(base_filename)
            rows, cols = img.shape[:2]
            element_obj_idx = 0

            img_split = element_filename.strip().split('.jpg')

            for element_obj in element_objs:
                class_name = element_obj.find('name').text # return name tag ie class of disease from xml file

                obj_bbox = element_obj.find('bndbox')
                x1 = int(round(float(obj_bbox.find('xmin').text)))
                y1 = int(round(float(obj_bbox.find('ymin').text)))
                x2 = int(round(float(obj_bbox.find('xmax').text)))
                y2 = int(round(float(obj_bbox.find('ymax').text)))

                # copying original images to new path
                new_name = img_split[0] + '.jpg'
                new_path = os.path.join(output_path, new_name) # join with augmented image path
                lines = [new_path, ' ', str(x1), ',', str(y1), ',', str(x2), ',', str(y2), ',', class_name, '\n']
                pwd_lines.append(lines)
                if not os.path.isfile(new_path):
                    cv2.imwrite(new_path, img)

                # for horizontal and vertical flip
                f_points = [0, 1]
                f_points_str = ['f0', 'f1']
                for f in f_points:
                    f_img = cv2.flip(img, f)
                    h,w = img.shape[:2]

                    if f == 1:
                        f_x1 = w-x2
                        f_y1 = y1
                        f_x2 = w-x1
                        f_y2 = y2
                        f_str = f_points_str[f]

                    elif f == 0:
                        f_x1 = x1
                        f_y1 = h-y2
                        f_x2 = x2
                        f_y2 = h-y1
                        f_str = f_points_str[f]

                    new_name = img_split[0] + '-' + f_str + '.jpg'
                    new_path = os.path.join(output_path, new_name)
                    lines = [new_path, ' ', str(f_x1), ',', str(f_y1), ',', str(f_x2), ',', str(f_y2), ',', class_name, '\n']
                    pwd_lines.append(lines)
                    if not os.path.isfile(new_path):
                        cv2.imwrite(new_path, f_img)

                    xmlname_no_ext, xmlname_ext = os.path.splitext(os.path.basename(xml_file))
                    new_xml = os.path.join(output_path, xmlname_no_ext + "-" + f_str + ".xml")

                    if not os.path.isfile(os.path.join(output_path, os.path.basename(xml_file))):
                        shutil.copyfile(xml_file, os.path.join(output_path, os.path.basename(xml_file)))

                    if not os.path.isfile(new_xml):
                        shutil.copyfile(xml_file, new_xml)

                    augmented_et = ET.parse(new_xml)
                    augmented_element = augmented_et.getroot()
                    augmented_element_objs = augmented_element.findall('object')

                    augmented_filename = augmented_element.find('filename')
                    augmented_path = augmented_element.find('path')
                    _augmented_filename, _augmented_file_ext = os.path.splitext(augmented_filename.text)

                    isFilenameAug = False
                    isFilepathAug = False
                    for aug_map in f_points_str:
                        if aug_map in augmented_filename.text:
                            isFilenameAug = True
                        if aug_map in augmented_path.text:
                            isFilepathAug = True

                    if not isFilenameAug:
                        augmented_filename.text = _augmented_filename + "-" + f_str + _augmented_file_ext

                    if not isFilepathAug:
                        augmented_path.text = os.path.join(os.path.dirname(augmented_path.text), augmented_filename.text)

                    aug_obj_bbox = augmented_element_objs[element_obj_idx].find('bndbox')
                    aug_obj_bbox.find('xmin').text = str(f_x1)
                    aug_obj_bbox.find('ymin').text = str(f_y1)
                    aug_obj_bbox.find('xmax').text = str(f_x2)
                    aug_obj_bbox.find('ymax').text = str(f_y2)

                    augmented_et.write(new_xml)

                element_obj_idx += 1
     
    #print(pwd_lines)
    if len(pwd_lines) > 0 :
        with open(out_path, 'w') as f:
            # print("Augmented Data:")
            for line in pwd_lines:
                # print(line[0])
                f.writelines(line)
                
    print('End')