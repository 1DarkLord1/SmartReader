# -*- coding: utf-8 -*-

import sys, os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'audio_text_mapper'))

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
        fb2_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', fb2_path)
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
        self.audio_list = [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',file.text)
        for file in audio.findall('file')]


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


    def save_map(self, mapinfo_rel_path):
        mapinfo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', mapinfo_rel_path)
        map_root = etree.Element('map')
        for item in self.word_sec.items():
            elem = etree.SubElement(map_root, 'elem')
            wordnum = etree.SubElement(elem, 'word')
            wordnum.text = str(item[0]).encode('utf-8')
            audionum = etree.SubElement(elem, 'audio-num')
            audionum.text = str(item[1].audio_num).encode('utf-8')
            secnd = etree.SubElement(elem, 'sec')
            secnd.text = str(item[1].sec).encode('utf-8')

        mapinfo_tree = etree.ElementTree(map_root)
        mapinfo_tree.write(mapinfo_path, pretty_print=True, xml_declaration=True, encoding='utf-8')


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

        self.save_map(os.path.join(self.fb2_dir, 'mapinfo_' + self.fb2_name + '.xml'))


    def load_map(self):
        mapinfo_rel_path = self.root.find('mapinfo').text
        mapinfo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', mapinfo_rel_path)
        mapinfo_tree = etree.parse(mapinfo_path, etree.XMLParser(remove_blank_text=True))
        map_root = mapinfo_tree.getroot()
        self.word_sec = {}
        self.sec_word = []
        for elem in map_root.findall('elem'):
            wordnum = int(elem.find('word').text)
            audionum = int(elem.find('audio-num').text)
            secnd = float(elem.find('sec').text)
            self.word_sec.update([(wordnum, namedtuple('Time', ['audio_num', 'sec'])(audionum, secnd))])
            if(len(self.sec_word) < audionum + 1):
                self.sec_word.append({})
            self.sec_word[audionum].update([(secnd, wordnum)])


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
