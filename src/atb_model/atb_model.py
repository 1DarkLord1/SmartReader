# -*- coding: utf-8 -*-

from lxml import etree
import re

class Model:
    def __init__(self):
        self.tree = None
        self.root = None
        self.text = None
        self.word_list = None
        self.audio_list = None


    def __get_fb2_root(self, fb2_path):
        fb2_tree = etree.parse(fb2_path, etree.XMLParser(remove_blank_text=True))
        fb2_root = fb2_tree.getroot()
        for elem in fb2_root.getiterator():
            elem.tag = etree.QName(elem).localname
        etree.cleanup_namespaces(fb2_root)
        return fb2_root


    def __fb2_text_parse(self, fb2_path):
        fb2_root = self.__get_fb2_root(fb2_path)
        raw_text = etree.tostring(fb2_root.find('body'), encoding='utf-8').decode('utf-8')
        repl_cltag = '#~?$'
        book_text = re.sub('<.*?>', '', re.sub('</.*?>', repl_cltag, raw_text)).replace(repl_cltag, '\n')
        return book_text


    def __load_text(self):
        book_path = self.root.find('fb2').text
        self.text =  self.__fb2_text_parse(book_path)


    def __make_word_list(self):
        self.word_list = [filter(lambda ch: ch.isalpha() or ch == '-' or ch.isdigit(), word)
        for word in re.split(' |\n', self.text)]
        self.word_list = filter(lambda word: word != "", self.word_list)


    def __parse_audio_list(self):
        audio = self.root.find('audio')
        self.audio_list = [file.text for file in audio.findall('file')]


    def load(self, path):
        self.tree = etree.parse(path, etree.XMLParser(remove_blank_text=True))
        self.root = self.tree.getroot()
        self.__load_text()
        self.__make_word_list()
        self.__parse_audio_list()


    def save(self, path):
        self.tree.write(path, pretty_print=True)


    def get_audio_list(self):
        return self.audio_list


    def get_text(self):
        return self.text


    def get_word_list(self):
        return self.word_list
