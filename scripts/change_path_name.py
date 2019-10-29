"""
	Change the path in the Pascal XML file.
	Because the path in xml is relative to machine, the paths need to be changed everytime the files are moved somewhere else.
"""

import os
import xml.etree.ElementTree as ET
import glob

# filepath = r'D:\training_data\young_and_mature_20\combined' #path where the annotation resides
# replacement = r'D:\training_data\young_and_mature_20\combined' #new file path to replace in the xml
def change_path_name(filePath, outputPath):
	print("Changing Path Name...")
	os.chdir(filePath)

	for f in glob.glob('*.xml'):
		tree = ET.parse(f)
		root = tree.getroot()
		filename = ""
		for child in tree.iter():

			if child.tag == 'filename':
				filename = child.text

			if child.tag == 'path':
				# print(child.text)
				child.text = os.path.join(outputPath, filename)
				# print(child.text)

			tree.write(f)