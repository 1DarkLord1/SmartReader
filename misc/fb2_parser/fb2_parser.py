import xml.etree.ElementTree as ET
from collections import namedtuple
from xml.parsers import expat
from xml.dom import minidom
import os

def parse_info(root):
    descr = root.find('description').find("title-info")
    genre = descr.find('genre')
    author = descr.find('author')
    book_title = descr.find('book-title')
    return namedtuple('Info', ['genre', 'author', 'title'])(genre, author, book_title)


oldcreate = expat.ParserCreate
expat.ParserCreate = lambda encoding, sep: oldcreate(encoding, None)

xml_file = os.path.join(os.getcwd(), "book2.fb2")
tree = ET.ElementTree(file=xml_file)
root = tree.getroot()
info = parse_info(root)
print(info.genre.text)
print(' '.join([name.text for name in info.author]))
print(info.title.text)
