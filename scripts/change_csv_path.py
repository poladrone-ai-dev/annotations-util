import os
import fileinput
import sys

filepath = r'C:\Users\Deployment\Desktop\keras-yolo3\train.txt'

def replaceAll(file, searchExp, replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)

def replaceFirst(file, searchExp, replaceExp):
    for line in fileinput.input(file, inplace=1):
        line = line.replace(searchExp, replaceExp, 1)
        sys.stdout.write(line)

replaceAll(filepath, "", r'C:\Users\Deployment\Desktop\palmtree-data-pix-segamat\c1203\images\\')
replaceFirst(filepath, ',', ' ')
replaceAll(filepath, "palm0", "0")
replaceAll(filepath, "palm1", "1")
