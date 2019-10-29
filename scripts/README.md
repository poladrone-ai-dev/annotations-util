# Preprocessing Images & VOC annotations into YOLO format  

This is a work in progress pipeline for preprocessing images and VOC annotations into YOLO format.

<!-- The pipeline is listed as shown below.

1.) Change the filepaths of the xml.
2.) Perform context adding on the xml.
3.) Perform image augmentation on the xml.
4.) Add the file path to the bounding box text file, and convert categorical classes into numerical representations. 

File Pipeline Order (WIP)

change_path_name.py -> context_adding.py -> data_augmentation.py -> change_csv_file.py -->

## Folder Structure
```<INPUT_PATH>```: Directory which contains images and VOC annotation XML files 
```<OUTPUT_PATH>```: Targetted empty directory to store augmented images and annotations in YOLO format 

### Example of Folder Structure
```<INPUT_PATH>```
|-- c0411-009.jpg
|-- c0411-009.xml

## Usage
Run ```python data_preprocessing.py -i <INPUT_PATH> -o <OUTPUT_PATH> -c <CONTEXT_PERCENTAGE>```

## Example

With no Context Adding
```
python data_preprocessing.py -i C:\Users\Jacklyn\Desktop\c0411 -o C:\Users\Jacklyn\Desktop\AugmentedData_Test
```
With 10% Context Adding

```
python data_preprocessing.py -i C:\Users\Jacklyn\Desktop\c0411 -o C:\Users\Jacklyn\Desktop\AugmentedData_Test -c 0.1
```

## Command Line Arguments

Use the following for help:```python data_preprocessing.py --help```

```
usage: data_preprocessing.py [-h] -i DATASET_PATH -o OUTPUT_PATH [-c CONTEXT]

optional arguments:
  -h, --help            show this help message and exit
  -i DATASET_PATH, --input DATASET_PATH
                        Path to dataset data (images and annotations).
  -o OUTPUT_PATH, --output OUTPUT_PATH
                        Path to save the processed data
  -c CONTEXT, --context CONTEXT
                        Context percentage for context adding (varies between
                        0 and 1)
```
