
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

input_path = r'D:\training_data\young_and_mature_20' # path where the images and xml resides
output_path = r"D:\training_data\young_and_mature_20\combined\result"
dirName = "combined"

# input images
data_path = "{}\\{}".format(input_path, dirName)

# input XML files
xml_path = "{}\\{}".format(input_path, dirName)

# output path for augmented images
output_img_path = "{}\\{}\\AugmentedImages".format(output_path, dirName)

if not os.path.exists(output_img_path):
    os.makedirs(output_img_path)

# output path for xml
xmlPath ="{}\\{}\\AugmentedXML\\".format(output_path, dirName)

if not os.path.exists(xmlPath):
    os.makedirs(xmlPath)

# output bounding box text file
out_path = "{}\\{}\\bb_box.txt".format(output_path, dirName)

# output bounding box multitext file
converted_annotation_in_txt_file = "{}\\{}\\converted_annotation_in_txt\\".format(output_path, dirName)


def dataAugmentation(imgPath):
    img = cv2.imread(imgPath)
    newName = imgPath.split("\\") 
    newName = newName[-1]
    # copy original image
    new_path = os.path.join(output_img_path, newName)
    if not os.path.isfile(new_path):
        cv2.imwrite(new_path, img)
    f_points = [0, 1]
    for f in f_points:
        f_img = cv2.flip(img, f)
        newName = imgPath.split("\\") 
        newName = newName[-1].split('.')
        newName = newName[0] + '-f' + str(f) + '.jpg'
        # print(newName)

        new_path = os.path.join(output_img_path, newName)

        if not os.path.isfile(new_path):
            cv2.imwrite(new_path, f_img)

xml_paths = [os.path.join(data_path, s) for s in os.listdir(data_path)]

for xml_file in xml_paths:
    if xml_file.endswith(".jpg"):
        dataAugmentation(xml_file)

pwd_lines = []
for xml_file in xml_paths:
    if xml_file.endswith(".xml"):
        et = ET.parse(xml_file)
        element = et.getroot()
        element_objs = element.findall('object') 
        element_filename = element.find('filename').text
        base_filename = os.path.join(data_path, element_filename)
        print(base_filename)                               
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
    # if you specify range(1) total number of augmented data is 6 for one image
    # 6 types of augmentation means pca, horizontal and vertical flip, 3 rotation
    # if you specify range(2) total number of augmented data is 12 for one image
    #         for color in range(1):
    #             img_color = pca_color_augmentation(img)
    #             color_name = img_split[0]+ '-color' + str(color)
    #             color_jpg = color_name + '.jpg'

            # copying original images to new path
            new_name = img_split[0] + '.jpg'
            new_path = os.path.join(output_img_path, new_name) # join with augmented image path
            lines = [new_name, ',', str(x1), ',', str(y1), ',', str(x2), ',', str(y2), ',', class_name, '\n']
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
                new_path = os.path.join(output_img_path, new_name)
    #             print(new_path)

                lines = [new_name, ',', str(f_x1), ',', str(f_y1), ',', str(f_x2), ',', str(f_y2), ',', class_name, '\n']
                pwd_lines.append(lines)
                if not os.path.isfile(new_path):
                    cv2.imwrite(new_path, f_img)


        
    
#print(pwd_lines)
if len(pwd_lines) > 0 :
    with open(out_path, 'w') as f:
        for line in pwd_lines:
            f.writelines(line)
            
print('End')



# for convertin .txt to .xml

# output filename
filepath = "file_name.txt"

def make_dataset(input_path):
    all_imgs = {}
    print("the input path is", input_path)
    with open(input_path,'r') as f:
        print('Parsing annotation files')
        for line in f:
            line_split = line.strip().split(',')
            (filename,x1,y1,x2,y2,class_name) = line_split
            if filename not in all_imgs:
                all_imgs[filename] = {}
                
                all_imgs[filename]['filepath'] = filename
                all_imgs[filename]['bboxes'] = []
                
            all_imgs[filename]['bboxes'].append({'class': class_name, 'x1': int(x1), 'x2': int(x2), 'y1': int(y1), 'y2': int(y2)})
            
        all_data = []
        
        for key in all_imgs:
            all_data.append(all_imgs[key])
            
        return all_data
            
dataset = make_dataset(out_path)

for i in range(len(dataset)):
    dataset_path = dataset[i]['filepath']
    dataset_name = dataset_path.split(',')[0]
    sep_dataset = dataset[i]['bboxes']
    
#     with open(filepath, 'a') as fn:
#         file_name = "{}\n".format(dataset_name)
#         fn.write(file_name)
        
    with open(converted_annotation_in_txt_file + str(dataset_name)+ ".txt", 'w') as f:
        for j in range(len(sep_dataset)):
            save_dataset = sep_dataset[j]
            
            data = "{} {} {} {} {} \n".format(sep_dataset[j]['class'],sep_dataset[j]['x1'],sep_dataset[j]['y1'], sep_dataset[j]['x2'], sep_dataset[j]['y2'])
            
            f.write(data)


def create_root(file_prefix, width, height):
    root = ET.Element("annotations")
    ET.SubElement(root, "filename").text = "{}.jpg".format(file_prefix)
    ET.SubElement(root, "folder").text = "AugmentedImages"
    ET.SubElement(root, "path").text = output_img_path + "\\{}.jpg".format(file_prefix)
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

def create_file(file_prefix, width, height, voc_labels):
    root = create_root(file_prefix, width, height)
    root = create_object_annotation(root, voc_labels)
    tree = ET.ElementTree(root)
#     xmlPath ="D:\Internship-Poladrone-Jacklyn\c0411(done) - Copy\\converted_XML\\"
#     if not os.path.exists(xmlPath):
#         os.makedirs(xmlPath)
    tree.write("{}{}.xml".format(xmlPath, file_prefix))

def read_file(file_path):
    file_prefix = file_path.split(".jpg")[0]
    file_path_data = converted_annotation_in_txt_file + file_path
#     print("the file path data", file_path_data)
    image_file_name = "{}.jpg".format(file_prefix)
    img = Image.open("{}/{}".format(output_img_path, image_file_name))
    w, h = img.size
    with open(file_path_data, 'r') as file:
        lines = file.readlines()
        voc_labels = []
        for line in lines:
            voc = []
            line = line.strip()
            data = line.split()
#             print(data[0],data[1],data[2],data[3],data[4])
            voc.append(data[0])
            voc.append(data[1])
            voc.append(data[2])
            voc.append(data[3])
            voc.append(data[4])
            voc_labels.append(voc)
#             print(voc_labels)
        create_file(file_prefix, w, h, voc_labels)
    # print("Processing complete for file: {}".format(file_path))

def start():
#     if not os.path.exists(DESTINATION_DIR):
#         os.makedirs(DESTINATION_DIR)
    for filename in os.listdir(converted_annotation_in_txt_file):
        # print(filename)
        if filename.endswith('txt'):
            read_file(filename)
        else:
            print("Skipping file: {}".format(filename))
#     if os.path.isfile(out_path):
#         os.remove(out_path)
#     if os.path.exists(ANNOTATIONS_DIR_PREFIX):
#         shutil.rmtree(ANNOTATIONS_DIR_PREFIX)
    

if __name__ == "__main__":
    start()