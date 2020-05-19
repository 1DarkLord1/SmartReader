# -*- coding: utf-8 -*-

import sys, os

def gen_path(paths):
    full_path = os.path.dirname(os.path.abspath(__file__))
    for path in paths:
        full_path = os.path.join(full_path, path)
    return full_path

sys.path.append(gen_path(['..', 'audio_text_mapper']))

import dill
from lxml import etree
import re
from pydub import AudioSegment
from bisect import bisect_left
from collections import namedtuple
from audio_text_mapper import ATMapper

class Model:
    def __init__(self):
        self.tree = None
        self.root = None
        self.text = None
        self.word_list = None
        self.audio_list = None
        self.fb2_dir = None
        self.fb2_name = None
        self.word_sec = None
        self.sec_word = None
        self.seconds = None


    def get_fb2_root(self, fb2_path):
        fb2_path = gen_path(['..', '..', fb2_path])
        fb2_tree = etree.parse(fb2_path, etree.XMLParser(remove_blank_text=True))
        fb2_root = fb2_tree.getroot()
        for elem in fb2_root.getiterator():
            elem.tag = etree.QName(elem).localname
        etree.cleanup_namespaces(fb2_root)
        return fb2_root


    def load_text(self):
        book_path = self.root.find('fb2').text
        fb2_root = self.get_fb2_root(book_path)
        raw_text = etree.tostring(fb2_root.find('body'), encoding='utf-8').decode('utf-8')
        repl_cltag = '#~?$'
        self.text = re.sub('<.*?>', '', re.sub('</.*?>', repl_cltag, raw_text)).replace(repl_cltag, '\n')


    def make_word_list(self):
        self.word_list = [''.join(list(filter(lambda ch: ch.isalpha() or ch == '-' or ch.isdigit(), word))).lower()
        for word in re.split(' |\n', self.text)]
        self.word_list = list(filter(lambda word: word != "", self.word_list))


    def parse_audio_list(self):
        audio = self.root.find('audio')
        self.audio_list = [gen_path(['..', '..',file.text]) for file in audio.findall('file')]


    def load(self, path):
        self.tree = etree.parse(path, etree.XMLParser(remove_blank_text=True))
        self.root = self.tree.getroot()
        self.fb2_name = self.root.find('fb2').text.split('/')[-1].replace('.fb2', '')
        self.fb2_dir = self.root.find('fb2').text.replace(self.fb2_name + '.fb2', '')
        self.load_text()
        self.make_word_list()
        self.parse_audio_list()


    def create_wav_from_mp3(self, audio_path):
        source = AudioSegment.from_mp3(audio_path)
        source.export(audio_path.replace('mp3', 'wav'), format='wav')
        return int(source.duration_seconds)


    def make_mapping(self):
        durs = []
        for audio in self.audio_list:
            durs.append(self.create_wav_from_mp3(audio))

        wav_list = list(map(lambda audio_path: audio_path.replace('mp3', 'wav'), self.audio_list))
        mapper = ATMapper(self.word_list, wav_list, durs)
        mapper.make_mapping()
        self.word_sec = mapper.get_word_sec()
        self.sec_word = mapper.get_sec_word()
        self.seconds = sorted([time.sec for time in self.word_sec.values()])
        for wav_audio in wav_list:
            os.remove(wav_audio)

        mapinfo_path = gen_path(['..', '..', self.fb2_dir, 'mapinfo_' + self.fb2_name + '.dat'])
        with open(mapinfo_path, "wb") as file:
            dill.dump(self.word_sec, file)


    def load_map(self):
        mapinfo_rel_path = self.root.find('mapinfo').text
        mapinfo_path = gen_path(['..', '..', mapinfo_rel_path])
        with open(mapinfo_path, "rb") as file:
            self.word_sec = dill.load(file)
        self.sec_word = []
        for data in self.word_sec.items():
            word = data[0]
            sec = data[1].sec
            audio_num = data[1].audio_num
            if(len(self.sec_word) < audio_num + 1):
                self.sec_word.append({})
            self.sec_word[audio_num].update([(sec, word)])
        self.seconds = sorted([time.sec for time in self.word_sec.values()])


    def make_atb(self, book_path, audio_paths, folder):
        folder_name = folder.split('/')[-1]
        audio_paths = [os.path.join(folder_name, path.split('/')[-1]) for path in audio_paths]
        book_name = book_path.split('/')[-1].replace('.fb2', '')
        book_path = os.path.join(folder_name, book_name + '.fb2')

        atb_root = etree.Element('atb')
        fb2 = etree.SubElement(atb_root, 'fb2')
        fb2.text = book_path
        audio = etree.SubElement(atb_root, 'audio')
        for audio_path in audio_paths:
            file = etree.SubElement(audio, 'file')
            file.text = audio_path
        mapinfo = etree.SubElement(atb_root, 'mapinfo')
        mapinfo.text = os.path.join(folder_name, 'mapinfo_' + book_name + '.dat')

        atb_tree = etree.ElementTree(atb_root)
        atb_tree.write(os.path.join(folder, book_name + '_data' + '.atb'), pretty_print=True, xml_declaration=True, encoding='utf-8')


    def get_audio_list(self):
        return self.audio_list


    def get_text(self):
        return self.text


    def get_word_list(self):
        return self.word_list


    def get_sec(self, word):
        return self.word_sec[word]


    def get_word(self, audio_num, sec):
        lb_sec_pos = bisect_left(self.seconds, sec)
        near_sec = self.seconds[lb_sec_pos] if self.seconds[lb_sec_pos] == sec else self.seconds[lb_sec_pos - 1]
        return self.sec_word[audio_num][near_sec]
