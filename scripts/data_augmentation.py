
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

def imgAugmentation(imgPath, output_path):
    
    output_path = output_path;
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

def create_BBox_txt(input_path, output_path):
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
            rows, cols = img.shape[:2] 


            img_split = element_filename.strip().split('.jpg')

            for element_obj in element_objs:
                class_name = element_obj.find('name').text # return name tag ie class of disease from xml file

                obj_bbox = element_obj.find('bndbox')
                #print(obj_bbox)
                x1 = int(round(float(obj_bbox.find('xmin').text)))
                y1 = int(round(float(obj_bbox.find('ymin').text)))
                x2 = int(round(float(obj_bbox.find('xmax').text)))
                y2 = int(round(float(obj_bbox.find('ymax').text)))

                # copying original images to new path
                new_name = img_split[0] + '.jpg'
                new_path = os.path.join(output_path, new_name) # join with augmented image path
                lines = [new_path, ' ', str(x1), ',', str(y1), ',', str(x2), ',', str(y2), ',', class_name[-1], '\n']
                pwd_lines.append(lines)
                if not os.path.isfile(new_path):
                    cv2.imwrite(new_path, img)

                # for horizontal and vertical flip
                f_points = [0, 1]
                for f in f_points:
                    f_img = cv2.flip(img, f)
                    h,w = img.shape[:2]

                    if f == 1:
                        f_x1 = w-x2
                        f_y1 = y1
                        f_x2 = w-x1
                        f_y2 = y2
                        f_str = 'f1'
                    elif f == 0:
                        f_x1 = x1
                        f_y1 = h-y2
                        f_x2 = x2
                        f_y2 = h-y1
                        f_str = 'f0'

                    new_name = img_split[0] + '-' + f_str + '.jpg'
                    new_path = os.path.join(output_path, new_name)
                    lines = [new_path, ' ', str(f_x1), ',', str(f_y1), ',', str(f_x2), ',', str(f_y2), ',', class_name[-1], '\n']
                    pwd_lines.append(lines)
                    if not os.path.isfile(new_path):
                        cv2.imwrite(new_path, f_img)
     
    #print(pwd_lines)
    if len(pwd_lines) > 0 :
        with open(out_path, 'w') as f:
            # print("Augmented Data:")
            for line in pwd_lines:
                # print(line[0])
                f.writelines(line)


# convert bb_box.txt to converted_annotation_in_txt XML files

def make_dataset(input_path):
    all_imgs = {}
    with open(input_path,'r') as f:
        # print('Parsing annotation files')
        for line in f:
            line_split = line.strip().split(' ', 1)
            filename = line_split[0]
            line_split = line_split[1].strip().split(',')
            # print(line_split)
            (x1,y1,x2,y2,class_name) = line_split
            if filename not in all_imgs:
                all_imgs[filename] = {}
                
                all_imgs[filename]['filepath'] = filename
                all_imgs[filename]['bboxes'] = []
                
            all_imgs[filename]['bboxes'].append({'class': class_name, 'x1': int(x1), 'x2': int(x2), 'y1': int(y1), 'y2': int(y2)})
            
        all_data = []
        
        for key in all_imgs:
            all_data.append(all_imgs[key])
            
        return all_data

def createAnnotation(multitext_file, output_path):
    out_path = "{}\\bb_box.txt".format(output_path)
    dataset = make_dataset(out_path)

    for i in range(len(dataset)):
        dataset_path = dataset[i]['filepath']
        dataset_name = dataset_path.split(' ')[0]
        dataset_name = dataset_name.split('\\')[-1]
        print(dataset_path)
        sep_dataset = dataset[i]['bboxes']
            
        with open(multitext_file + str(dataset_name)+ ".txt", 'w') as f:
            for j in range(len(sep_dataset)):
                save_dataset = sep_dataset[j]
                
                data = "{} {} {} {} {} \n".format(sep_dataset[j]['class'],sep_dataset[j]['x1'],sep_dataset[j]['y1'], sep_dataset[j]['x2'], sep_dataset[j]['y2'])
                
                f.write(data)

def create_root(output_path, file_prefix, width, height):
    root = ET.Element("annotations")
    ET.SubElement(root, "filename").text = "{}.jpg".format(file_prefix)
    ET.SubElement(root, "folder").text = "AugmentedImages"
    ET.SubElement(root, "path").text = str(output_path) + "\\{}.jpg".format(file_prefix)
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    ET.SubElement(size, "depth").text = "3"
    return root

def create_object_annotation(root, voc_labels):
    for voc_label in voc_labels:
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = voc_label[0]
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = str(0)
        ET.SubElement(obj, "difficult").text = str(0)
        bbox = ET.SubElement(obj, "bndbox")
        ET.SubElement(bbox, "xmin").text = str(voc_label[1])
        ET.SubElement(bbox, "ymin").text = str(voc_label[2])
        ET.SubElement(bbox, "xmax").text = str(voc_label[3])
        ET.SubElement(bbox, "ymax").text = str(voc_label[4])
    return root

def create_file(output_path, file_prefix, width, height, voc_labels):
    root = create_root(output_path, file_prefix, width, height)
    root = create_object_annotation(root, voc_labels)
    tree = ET.ElementTree(root)
    # output path for xml  
    xmlPath ="{}\\AugmentedXML\\".format(output_path)
    if not os.path.exists(xmlPath):
        os.makedirs(xmlPath)
    tree.write("{}{}.xml".format(xmlPath, file_prefix))

def read_file(output_path, multitext_file, file_path):
    file_prefix = file_path.split(".jpg")[0]
    file_path_data = multitext_file + file_path
    image_file_name = "{}.jpg".format(file_prefix)
    img = Image.open("{}/{}".format(output_path, image_file_name))
    w, h = img.size
    with open(file_path_data, 'r') as file:
        lines = file.readlines()
        voc_labels = []
        for line in lines:
            voc = []
            line = line.strip()
            data = line.split()
            voc.append(data[0])
            voc.append(data[1])
            voc.append(data[2])
            voc.append(data[3])
            voc.append(data[4])
            voc_labels.append(voc)
        create_file(output_path, file_prefix, w, h, voc_labels)

def data_augmentation(input_path, output_path):
    # creating bb_box.txt
    create_BBox_txt(input_path, output_path)

    # creating multitext file for converting back to XML
    multitext_file = "{}\\converted_annotation_in_txt\\".format(output_path)
    if not os.path.exists(multitext_file):
        os.makedirs(multitext_file)
    createAnnotation(multitext_file, output_path)

    # creating XML annotation
    for filename in os.listdir(multitext_file):
        # print(filename)
        if filename.endswith('txt'):
            read_file(output_path, multitext_file, filename)
        else:
            print("Skipping file: {}".format(filename))

    print('End')