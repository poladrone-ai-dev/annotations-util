"""
    Just like context_adding.py, but with the context reduced instead.
"""

import xml.etree.ElementTree as ET
import os
import glob

def context_reduction(XML_PATH=None):
    # print("Reducing {} % context".format(contextPercentage))
    XML_PATH = r'D:\training_data\images-after-relabel-20191016\young' # path where the xml resides
    os.chdir(XML_PATH)

    IMG_WIDTH = 0
    IMG_HEIGHT = 0

    CONTEXT = 0 # varies between 0 and 1
    for f in glob.glob('*.xml'):
        tree = ET.parse(f)
        root = tree.getroot()

        for child in tree.iter():
            if child.tag == "size":
                for dimensions in child.iter():
                    if dimensions.tag == "width":
                        IMG_WIDTH = int(dimensions.text)
                    if dimensions.tag == "height":
                        IMG_HEIGHT = int(dimensions.text)

            if child.tag == "object":
                for prop in child.iter():
                    if prop.tag == "name":
                        if prop.text == "palm1":
                            CONTEXT = float(0.1)
                            print("palm1 detected. adding 10% context")
                        if prop.text == "palm2":
                            CONTEXT = float(0.1)
                            print("palm2 detected. adding 10% context")
                        if prop.text == "palm3":
                            CONTEXT = float(0.05)
                            print("palm3 detected. adding 5% context")

            if child.tag == "bndbox":
                WIDTH = 0
                HEIGHT = 0 
                xmin = 0
                xmax = 0
                ymin = 0
                ymax = 0

                xmin = int(child.find("xmin").text)
                xmax = int(child.find("xmax").text)
                ymin = int(child.find("ymin").text)
                ymax = int(child.find("ymax").text)
                WIDTH = xmax - xmin
                HEIGHT = ymax - ymin

                for bndbox in child.iter():
                    if bndbox.tag != "bndbox":
                        # print(bndbox.tag + ": " + bndbox.text)

                        if bndbox.tag == "xmin" and int(bndbox.text) != 0:
                            newBound = int(bndbox.text) + (CONTEXT * WIDTH)
                            if newBound > IMG_WIDTH:
                                newBound = IMG_WIDTH

                            newBound = round(newBound)
                            bndbox.text = bndbox.text.replace(bndbox.text, str(newBound))
                            print(bndbox.tag + ": " + bndbox.text)

                        if bndbox.tag == "xmax" and int(bndbox.text != WIDTH):
                            newBound = int(bndbox.text) - (CONTEXT * WIDTH)
                            if newBound < 0:
                                newBound = 0

                            newBound = round(newBound)
                            bndbox.text = bndbox.text.replace(bndbox.text, str(newBound))
                            print(bndbox.tag + ": " + bndbox.text)

                        if bndbox.tag == "ymin" and int(bndbox.text) != 0:
                            newBound = int(bndbox.text) + (CONTEXT * HEIGHT)
                            if newBound > IMG_HEIGHT:
                                newBound = IMG_HEIGHT

                            newBound = round(newBound)
                            bndbox.text = bndbox.text.replace(bndbox.text, str(newBound))
                            print(bndbox.tag + ": " + bndbox.text)

                        if bndbox.tag == "ymax" and int(bndbox.text) != HEIGHT:
                            newBound = int(bndbox.text) - (CONTEXT * HEIGHT)
                            if newBound < 0:
                                newBound = 0

                            newBound = round(newBound)
                            bndbox.text = bndbox.text.replace(bndbox.text, str(newBound))
                            print(bndbox.tag + ": " + bndbox.text)

                        tree.write(f)

context_reduction()