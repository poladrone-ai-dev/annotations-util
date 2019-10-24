"""
    Changes the csv file generated from Pascal VOC XML into YOLO format.
    path/to/img xmin,ymin,xmax,ymax,class xmin,ymin,xmax,ymax,class

"""
import os
import fileinput
import sys

filepath = r'D:\training_data\young_and_mature_20\combined\result\combined\bbox.txt'

def replaceAll(file, searchExp, replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)

def replaceFirst(file, searchExp, replaceExp):
    for line in fileinput.input(file, inplace=1):
        line = line.replace(searchExp, replaceExp, 1)
        sys.stdout.write(line)

replaceFirst(filepath, "", r'D:\training_data\young_and_mature_20\combined\result\combined\AugmentedImages\\')
replaceFirst(filepath, ',', ' ')
replaceAll(filepath, "palm0", "0")
replaceAll(filepath, "palm1", "1")
replaceAll(filepath, "palm2", "2")
