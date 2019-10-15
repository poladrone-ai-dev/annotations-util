import os
import xml.etree.ElementTree as ET
import glob

path = r'C:\Users\Deployment\Desktop\testfolder\annotations' #path where the annotation resides
OG_path = r'C:\Users\Jacklyn\Desktop\images-after-segregate\AugmentedData\c1203\AugmentedImages' # original path of the images in the xml
replacement = r'C:\Users\Deployment\Desktop\testfolder\annotations' #new path to replace the original path
os.chdir(path)

for f in glob.glob('*.xml'):
	tree = ET.parse(f)
	root = tree.getroot()
	filename = ""
	for child in tree.iter():

		if child.tag == 'filename':
			filename = child.text

		if child.tag == 'path':
			print(child.text)
			child.text = os.path.join(replacement, filename)
			print(child.text)

		tree.write(f)