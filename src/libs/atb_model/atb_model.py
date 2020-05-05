# -*- coding: utf-8 -*-

from lxml import etree
import re, pydub, sys, os
dir = '/home/dword/Desktop/SmartReader_denil_sharipov/src/libs/audio_text_mapper/'
sys.path.insert(0, dir)
from pydub import AudioSegment
from bisect import bisect_left
from audio_text_mapper import ATMapper

class Model:
    def __init__(self):
        self.tree = None
        self.root = None
        self.text = None
        self.word_list = None
        self.audio_list = None
        self.word_sec = None
        self.sec_word = None
        self.seconds = None


    def get_fb2_root(self, fb2_path):
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
        self.audio_list = [file.text for file in audio.findall('file')]


    def load(self, path):
        self.tree = etree.parse(path, etree.XMLParser(remove_blank_text=True))
        self.root = self.tree.getroot()
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
            #durs.append(self.create_wav(audio))
            self.create_wav_from_mp3(audio)
            durs.append(90)

        wav_list = list(map(lambda audio_path: audio_path.replace('mp3', 'wav'), self.audio_list))
        mapper = ATMapper(self.word_list[:200], wav_list, durs)
        mapper.make_mapping()
        self.word_sec = mapper.get_word_sec()
        self.sec_word = mapper.get_sec_word()
        self.seconds = sorted([time.sec for time in self.word_sec.values()])
        for wav_audio in wav_list:
            os.remove(wav_audio)


    def save(self, path):
        self.tree.write(path, pretty_print=True)


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
