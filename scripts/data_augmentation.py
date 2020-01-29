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
import bbox_utils
import shutil
import random

def FixBoxBounds(box, img_dim, img_name):
    if box[0] <= 0:
        print("Negative x1 found in " + os.path.basename(img_name))
        with open(os.path.join(os.path.dirname(img_name), "bad_file.txt"), 'a+') as fp:
            fp.write("Negative x1 found in " + os.path.basename(img_name) + '\n')
        box[0] = 1

    if box[1] <= 0:
        print("Negative y1 found in " + os.path.basename(img_name))
        with open(os.path.join(os.path.dirname(img_name), "bad_file.txt"), 'a+') as fp:
            fp.write("Negative y1 found in " + os.path.basename(img_name) +'\n')
        box[1] = 1

    if box[2] >= img_dim[0]:
        print("X2 bounds exceed found in " + os.path.basename(img_name))
        with open(os.path.join(os.path.dirname(img_name), "bad_file.txt"), 'a+') as fp:
            fp.write("X2 bounds exceed found in " + os.path.basename(img_name) +'\n')
        box[2] = img_dim[0] - 1

    if box[3] >= img_dim[1]:
        print("Y2 bounds exceed found in " + os.path.basename(img_name))
        with open(os.path.join(os.path.dirname(img_name), "bad_file.txt"), 'a+') as fp:
            fp.write("Y2 bounds exceed found in " + os.path.basename(img_name)+ '\n')
        box[3] = img_dim[1] - 1

    return [box[0], box[1], box[2], box[3]]

def ShrinkBbox(img, bbox):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    topleft = [int(bbox[0][0]), int(bbox[0][1])]
    bottomright = [int(bbox[0][2]), int(bbox[0][3])]
    topright = [int(bbox[0][2]), int(bbox[0][1])]
    bottomleft = [int(bbox[0][0]), int(bbox[0][3])]

    if [img[topleft[0], topleft[1]][0], img[topleft[0], topleft[1]][1], img[topleft[0], topleft[1]][2]] == [0,0,0]:
        # print("Shrinking top left corner: " + str(topleft))
        while [img[topleft[0], topleft[1]][0], img[topleft[0], topleft[1]][1], img[topleft[0], topleft[1]][2]] == [0,0,0]:
            topleft[0] += 5
            topleft[1] += 5
            # print([img[topleft[0], topleft[1]][0], img[topleft[0], topleft[1]][1], img[topleft[0], topleft[1]][2]] )
        # print("After shrinking: " + str(topleft))

    if [img[bottomright[0], bottomright[1]][0], img[bottomright[0], bottomright[1]][1], img[bottomright[0], bottomright[1]][2]] == [0,0,0]:
        while [img[bottomright[0], bottomright[1]][0], img[bottomright[0], bottomright[1]][1], img[bottomright[0], bottomright[1]][2]] == [0,0,0]:
            bottomright[0] -= 5
            bottomright[1] -= 5

    if [img[topright[0], topright[1]][0], img[topright[0], topright[1]][1], img[topright[0], topright[1]][2]] == [0,0,0]:
        while [img[topright[0], topright[1]][0], img[topright[0], topright[1]][1], img[topright[0], topright[1]][2]] == [0,0,0]:
            topright[0] -= 5
            topright[1] += 5

    if [img[bottomleft[0], bottomleft[1]][0], img[bottomleft[0], bottomleft[1]][1], img[bottomleft[0], bottomleft[1]][2]] == [0,0,0]:
        while [img[bottomleft[0], bottomleft[1]][0], img[bottomleft[0], bottomleft[1]][1], img[bottomleft[0], bottomleft[1]][2]] == [0,0,0]:
            bottomleft[0] += 5
            bottomleft[1] -= 5

    return [[topleft[0], topleft[1], bottomright[0], bottomright[1]]]

def GaussianBlur(imgPath, xml_path, output_path, pwd_lines, class_names):
    img = cv2.imread(imgPath)
    newName = imgPath.split("\\")
    newName = newName[-1]
    new_path = os.path.join(output_path, newName)
    new_path = os.path.splitext(new_path)[0] + "_gaussian_blur" + os.path.splitext(new_path)[1]

    dst = cv2.GaussianBlur(img, (25,25), 0)
    h, w, channels = dst.shape
    cv2.imwrite(new_path, dst)

    new_xml_path = os.path.join(output_path, os.path.splitext(os.path.basename(xml_path))[0] + "_gaussian_blur.xml")
    shutil.copyfile(xml_path, new_xml_path)

    et = ET.parse(new_xml_path)
    element = et.getroot()
    element_objs = element.findall('object')

    element.find('filename').text = os.path.basename(new_path)

    for element_obj in element_objs:
        obj_bbox = element_obj.find('bndbox')
        x1 = int(round(float(obj_bbox.find('xmin').text)))
        y1 = int(round(float(obj_bbox.find('ymin').text)))
        x2 = int(round(float(obj_bbox.find('xmax').text)))
        y2 = int(round(float(obj_bbox.find('ymax').text)))

        class_name = element_obj.find('name').text
        if class_name not in class_names:
            class_names.append(class_name)

        [x1, y1, x2, y2] = FixBoxBounds([x1, y1, x2, y2], [w,h], imgPath)

        gaussian_line = [os.path.join(output_path, os.path.splitext(os.path.basename(xml_path))[0] + "_gaussian_blur.jpg"),
                         ' ', str(x1), ',', str(y1), ',', str(x2), ',', str(y2), ',', class_name, '\n']
        pwd_lines.append(gaussian_line)

    et.write(new_xml_path)
    return pwd_lines, class_names

def ImageRotate(imgPath, output_path, xml_file, angle, pwd_lines, class_names):
    img = cv2.imread(imgPath)
    newName = imgPath.split("\\")
    newName = newName[-1]
    new_path = os.path.join(output_path, newName)
    new_path = os.path.splitext(new_path)[0] + "_rotate_" + str(angle) + os.path.splitext(new_path)[1]

    (height, width) = img.shape[:2]
    center = (width / 2, height / 2)

    scale = 1.0
    rotation_mat = cv2.getRotationMatrix2D(center, angle, scale)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    rotation_mat[0, 2] += bound_w / 2 - center[0]
    rotation_mat[1, 2] += bound_h / 2 - center[1]

    # dst = cv2.warpAffine(img, rotation_mat, (bound_w, bound_h))
    dst = cv2.warpAffine(img, rotation_mat, (width, height))

    cv2.imwrite(new_path, dst)

    xml_dst = os.path.splitext(new_path)[0] + ".xml"
    shutil.copyfile(xml_file, xml_dst)

    et = ET.parse(xml_dst)
    element = et.getroot()
    element_objs = element.findall('object')
    element.find('filename').text = os.path.basename(new_path)

    rotated_img = cv2.imread(new_path)
    for element_obj in element_objs:
        obj_bbox = element_obj.find('bndbox')
        x1 = int(round(float(obj_bbox.find('xmin').text)))
        y1 = int(round(float(obj_bbox.find('ymin').text)))
        x2 = int(round(float(obj_bbox.find('xmax').text)))
        y2 = int(round(float(obj_bbox.find('ymax').text)))

        array = np.array([x1, y1, x2, y2]).reshape(1,4)
        corners = bbox_utils.GetCorners(array)
        rotated_coords = bbox_utils.RotateBox(corners, angle, center[0], center[1], height, width)
        new_bbox = bbox_utils.GetEnclosingBox(rotated_coords)
        # new_bbox = ShrinkBbox(rotated_img, new_bbox)

        [x1, y1, x2, y2] = FixBoxBounds([int(new_bbox[0][0]), int(new_bbox[0][1]),
                                         int(new_bbox[0][2]), int(new_bbox[0][3]) ], [width, height], imgPath)

        obj_bbox.find('xmin').text = str(x1)
        obj_bbox.find('ymin').text = str(y1)
        obj_bbox.find('xmax').text = str(x2)
        obj_bbox.find('ymax').text = str(y2)

        class_name = element_obj.find('name').text
        if class_name not in class_names:
            class_names.append(class_name)

        lines = [new_path, ' ', str(x1), ',', str(y1),
                 ',', str(x2), ',', str(y2), ',', class_name, '\n']

        pwd_lines.append(lines)

    et.write(xml_dst)
    return pwd_lines, class_names

def ImageFlip(imgPath, output_path, xml_file, pwd_lines, class_names):
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

    et = ET.parse(xml_file)
    element = et.getroot()
    element_objs = element.findall('object')
    element_filename = element.find('filename').text
    img = cv2.imread(element_filename)
    height, width, channels = img.shape
    element_obj_idx = 0
    img_split = element_filename.strip().split('.jpg')

    element.find('filename').text = os.path.basename(new_path)

    for element_obj in element_objs:
        class_name = element_obj.find('name').text  # return name tag ie class of disease from xml file

        if class_name not in class_names:
            class_names.append(class_name)

        obj_bbox = element_obj.find('bndbox')

        x1 = int(round(float(obj_bbox.find('xmin').text)))
        y1 = int(round(float(obj_bbox.find('ymin').text)))
        x2 = int(round(float(obj_bbox.find('xmax').text)))
        y2 = int(round(float(obj_bbox.find('ymax').text)))

        if x1 <= 0:
            x1 = 1
        if y1 <= 0:
            y1 = 1
        if x2 >= width:
            x2 = width - 1
        if y2 >= height:
            y2 >= height - 1

        # copying original images to new path
        new_name = img_split[0] + '.jpg'
        new_path = os.path.join(output_path, new_name)  # join with augmented image path
        lines = [new_path, ' ', str(x1), ',', str(y1), ',', str(x2), ',', str(y2), ',', class_name, '\n']
        pwd_lines.append(lines)
        if not os.path.isfile(new_path):
            cv2.imwrite(new_path, img)

        # for horizontal and vertical flip
        f_points = [0, 1]
        f_points_str = ['f0', 'f1']
        for f in f_points:
            f_img = cv2.flip(img, f)
            h, w = img.shape[:2]

            if f == 1:
                f_x1 = w - x2
                f_y1 = y1
                f_x2 = w - x1
                f_y2 = y2
                f_str = f_points_str[f]

            elif f == 0:
                f_x1 = x1
                f_y1 = h - y2
                f_x2 = x2
                f_y2 = h - y1
                f_str = f_points_str[f]

            new_name = img_split[0] + '-' + f_str + '.jpg'
            new_path = os.path.join(output_path, new_name)

            [f_x1, f_y1, f_x2, f_y2] = FixBoxBounds([x1, y1, x2, y2], [width, height], imgPath)

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
            _augmented_filename, _augmented_file_ext = os.path.splitext(augmented_filename.text)

            isFilenameAug = False

            for aug_map in f_points_str:
                if aug_map in augmented_filename.text:
                    isFilenameAug = True

            if not isFilenameAug:
                augmented_filename.text = _augmented_filename + "-" + f_str + _augmented_file_ext

            aug_obj_bbox = augmented_element_objs[element_obj_idx].find('bndbox')
            aug_obj_bbox.find('xmin').text = str(f_x1)
            aug_obj_bbox.find('ymin').text = str(f_y1)
            aug_obj_bbox.find('xmax').text = str(f_x2)
            aug_obj_bbox.find('ymax').text = str(f_y2)

            augmented_et.write(new_xml)

        element_obj_idx += 1

    return pwd_lines, class_names

def RandomShear(imgPath, output_path, xml_file, pwd_lines, class_names, shear_factor=0.2):
    if type(shear_factor) == tuple:
        assert len(shear_factor) == 2, "Invalid range for scaling factor"
    else:
        shear_factor = (-shear_factor, shear_factor)

    shear_factor = random.uniform(*shear_factor)

    img = cv2.imread(imgPath)
    newName = imgPath.split("\\")
    newName = newName[-1]
    new_path = os.path.join(output_path, newName)
    new_path = os.path.splitext(new_path)[0] + "_shear" + os.path.splitext(new_path)[1]

    (height, width) = img.shape[:2]

    M = np.array([[1, abs(shear_factor), 0], [0, 1, 0]])
    nW = img.shape[1] + abs(shear_factor * img.shape[0])
    img = cv2.warpAffine(img, M, (int(nW), img.shape[0]))
    img = cv2.resize(img, (width, height))

    cv2.imwrite(new_path, img)

    et = ET.parse(xml_file)
    element = et.getroot()
    element_objs = element.findall('object')
    element_filename = element.find('filename').text
    img = cv2.imread(element_filename)
    element.find('filename').text = os.path.basename(new_path)

    xml_dst = os.path.splitext(new_path)[0] + ".xml"
    shutil.copyfile(xml_file, xml_dst)

    for element_obj in element_objs:
        class_name = element_obj.find('name').text
        if class_name not in class_names:
            class_names.append(class_name)

        obj_bbox = element_obj.find('bndbox')
        x1 = int(round(float(obj_bbox.find('xmin').text)))
        y1 = int(round(float(obj_bbox.find('ymin').text)))
        x2 = int(round(float(obj_bbox.find('xmax').text)))
        y2 = int(round(float(obj_bbox.find('ymax').text)))

        x1 += int(y1 * abs(shear_factor))
        x2 += int(y2 * abs(shear_factor))

        new_bbox = ShrinkBbox(img, [[min(x1, width - 1), min(y1, height - 1), min(x2, width - 1), min(y2, height - 1)]])

        [x1, y1, x2, y2] = FixBoxBounds([int(new_bbox[0][0]), int(new_bbox[0][1]),
                                         int(new_bbox[0][2]), int(new_bbox[0][3])], [width, height], imgPath)

        lines = [new_path, ' ', str(x1), ',', str(y1),
                 ',', str(x2), ',', str(y2), ',', class_name, '\n']

        pwd_lines.append(lines)

    et.write(xml_dst)
    return pwd_lines, class_names

def CheckNegativeData(xml_path, output_path):
    et = ET.parse(xml_path)
    element = et.getroot()
    element_objs = element.findall('object')

    if element_objs == None:
        print(xml_path + " contains negative data. Excluding it from data augmentation.")
        with open(os.path.join(output_path, "bad_file.txt"), 'a+') as fp:
            fp.write(xml_path + " contains negative data. Excluding it from data augmentation.")

        return True

    return False

def data_augmentation(input_path, output_path):
    pwd_lines = []
    class_names = []
    angles = [60, 120]

    if os.path.isfile(os.path.join(output_path, "bad_file.txt")):
        os.remove(os.path.join(output_path, "bad_file.txt"))

    print("Augmenting the Data...")
    # output bounding box text file
    out_path = "{}\\bb_box.txt".format(output_path)

    xml_paths = [os.path.join(input_path, s) for s in os.listdir(input_path)]

    for file in xml_paths:
        if file.endswith(".jpg"):
            xml_path = os.path.splitext(file)[0] + ".xml"

            if not CheckNegativeData(xml_path, output_path):
                print("Performing image flipping on " + file)
                pwd_lines, class_names = ImageFlip(file, output_path, xml_path, pwd_lines, class_names)
                print("Performing Gaussian blur on " + file)
                pwd_lines, class_names = GaussianBlur(file, xml_path, output_path, pwd_lines, class_names)

                # for angle in angles:
                #     print("Performing " + str(angle) + " degrees rotation on " + file)
                #     pwd_lines, class_names = ImageRotate(file, output_path, xml_path, angle, pwd_lines, class_names)
                #
                # print("Performing shearing on " + file)
                # pwd_lines, class_names = RandomShear(file, output_path, xml_path, pwd_lines, class_names)

    if os.path.isfile(os.path.join(output_path, "class.txt")):
        os.remove(os.path.join(output_path, "class.txt"))

    with open(os.path.join(output_path, "classes.txt"), 'a') as class_fp:
        for class_name in class_names:
            class_fp.write(class_name + '\n')

    if len(pwd_lines) > 0 :
        with open(out_path, 'a') as f:

            for line in pwd_lines:
                f.writelines(line)
                gt_file = os.path.splitext(line[0])[0] + ".txt"
                fp = open(gt_file, "a+")
                fp.write(line[10] + " " + line[2] + " " + line[4] + " " + line[6] + " " + line[8] + "\n")
            fp.close()
                
    print('End')