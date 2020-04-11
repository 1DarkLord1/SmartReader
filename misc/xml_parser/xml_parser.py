import xml.etree.cElementTree as ET
from xml.dom import minidom
import os

def indent(elem, level=0):
    i = "n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def parse_terminal_tags(root):
    for xml_tag in root.iter():
        if len(xml_tag) == 0:
            print("Tag name: {0}".format(xml_tag.tag))
            print("Tag text: {0}\n".format(xml_tag.text))

def add_audio(audio_name, root):
    audio_tag = root[1]
    new_file = ET.SubElement(audio_tag, 'file')
    new_file.text = audio_name


xml_file = os.path.join(os.getcwd(), "sample.xml")
tree = ET.ElementTree(file=xml_file)
root = tree.getroot()
#add_audio("5.mp3", root)
#tree.write(xml_file)
parse_terminal_tags(root)
