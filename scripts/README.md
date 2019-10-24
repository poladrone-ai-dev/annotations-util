This is a work in progress pipeline for preprocessing images and VOC annotations into YOLO format.

The pipeline is listed as shown below.

1.) Change the filepaths of the xml.
2.) Perform context adding on the xml.
3.) Perform image augmentation on the xml.
4.) Add the file path to the bounding box text file, and convert categorical classes into numerical representations. 

File Pipeline Order (WIP)

change_path_name.py -> context_adding.py -> data_augmentation.py -> change_csv_file.py
