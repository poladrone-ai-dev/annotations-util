

import numpy as np
import os
import xml.etree.ElementTree as ET

def start():

    # contextAddingFolderName = "contextAdding-10"

    # path where the images and xml resides
    input_path = r'C:\Users\Deployment\Desktop\10_context_training\annotations'

    image_path = r'C:\Users\Deployment\Desktop\10_context_training\images'
    
    # output dir 
    output_path = r"C:\Users\Deployment\Desktop\10_context_training"

    # dirName = "c0411"

    # input dir of XML files 
    xml_path = input_path

    # output bounding box text file
    out_path = "{}\\bb_box.txt".format(output_path)

    xml_paths = [os.path.join(xml_path, s) for s in os.listdir(xml_path)]

    # for xml_file in xml_paths:
    #     if xml_file.endswith(".jpg"):
    #         dataAugmentation(xml_file)

    pwd_lines = []
    for xml_file in xml_paths:
        if xml_file.endswith(".xml"):
            et = ET.parse(xml_file)
            element = et.getroot()
            element_objs = element.findall('object') 
            element_filename = element.find('filename').text
            element_path = element.find('path').text
            base_filename = os.path.join(xml_path, element_filename)
            print(base_filename)                               
            # img = cv2.imread(base_filename)
            # rows, cols = img.shape[:2] 


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
                # new_name = img_split[0] + '.jpg'
                # new_path = os.path.join(output_img_path, new_name) # join with augmented image path
                # lines = [new_name, ',', str(x1), ',', str(y1), ',', str(x2), ',', str(y2), ',', class_name, '\n']
                # pwd_lines.append(lines)
                # if not os.path.isfile(new_path):
                #     cv2.imwrite(new_path, img)

                # # for horizontal and vertical flip
                # f_points = [0, 1]
                # for f in f_points:
                #     f_img = cv2.flip(img, f)
                #     h,w = img.shape[:2]

                #     if f == 1:
                #         f_x1 = w-x2
                #         f_y1 = y1
                #         f_x2 = w-x1
                #         f_y2 = y2
                #         f_str = 'f1'
                #     elif f == 0:
                #         f_x1 = x1
                #         f_y1 = h-y2
                #         f_x2 = x2
                #         f_y2 = h-y1
                #         f_str = 'f0'

                #     new_name = img_split[0] + '-' + f_str + '.jpg'
                #     new_path = os.path.join(output_img_path, new_name)
        #             print(new_path)
                new_path = image_path + '\\' + element_filename
                lines = [new_path, ' ', str(x1), ',', str(y1), ',', str(x2), ',', str(y2), ',', class_name[-1], '\n']
                pwd_lines.append(lines)
                # if not os.path.isfile(new_path):
                #     cv2.imwrite(new_path, f_img)


            
        
    #print(pwd_lines)
    if len(pwd_lines) > 0 :
        with open(out_path, 'w') as f:
            for line in pwd_lines:
                f.writelines(line)
                
    print('End')



if __name__ == "__main__":
    start()