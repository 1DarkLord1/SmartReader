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
import shutil
import threading



class Model:
    def __init__(self):
        self.root_name = 'books'

        self.tree = None
        self.root = None
        self.fb2_dir = None
        self.fb2_name = None

        self.text = None
        self.word_list = None
        self.audio_list = None
        self.wav_list = None
        self.durs = None

        self.word_sec = None
        self.sec_word = None
        self.seconds = None

        self.mutex = threading.Lock()
        
        
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
        self.audio_list = [gen_path(['..', '..', file.text]) for file in audio.findall('file')]
        

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
        self.durs = []
        for audio in self.audio_list:
            self.durs.append(self.create_wav_from_mp3(audio))

        self.wav_list = list(map(lambda audio_path: audio_path.replace('mp3', 'wav'), self.audio_list))
        mapper = ATMapper(self)
        self.word_sec = {}
        self.sec_word = [{} for i in range(len(self.audio_list))]
        self.seconds = [[] for i in range(len(self.audio_list))]
        mapper.recognize_all()

        for wav_audio in self.wav_list:
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
        self.seconds = []
        for data in self.word_sec.items():
            word = data[0]
            sec = data[1].sec
            audio_num = data[1].audio_num
            while len(self.sec_word) < audio_num + 1:
                self.sec_word.append({})
                self.seconds.append([])
            self.sec_word[audio_num].update([(sec, word)])
            self.seconds[audio_num].append(sec)
        self.seconds = [sorted(cur_secs) for cur_secs in self.seconds]


    def import_book(self, book_path, audio_paths):
        book_name = book_path.split('/')[-1].replace('.fb2', '')
        folder_path = gen_path(['..', '..', self.root_name, book_name])
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.mkdir(folder_path)
        shutil.copyfile(book_path, os.path.join(folder_path, book_name + '.fb2'))
        for audio_path in audio_paths:
            shutil.copyfile(audio_path, os.path.join(folder_path, audio_path.split('/')[-1]))
        rel_folder_path = os.path.join(self.root_name, folder_path.split('/')[-1])
        rel_book_path = os.path.join(rel_folder_path, book_name + '.fb2')
        rel_audio_paths = [os.path.join(rel_folder_path, path.split('/')[-1]) for path in audio_paths]
        self.make_atb(rel_book_path, book_name, rel_audio_paths, rel_folder_path, folder_path)


    def make_atb(self, book_path, book_name, audio_paths, rel_folder_path, folder_path):
        atb_root = etree.Element('atb')
        fb2 = etree.SubElement(atb_root, 'fb2')
        fb2.text = book_path
        audio = etree.SubElement(atb_root, 'audio')
        for audio_path in audio_paths:
            file = etree.SubElement(audio, 'file')
            file.text = audio_path
        mapinfo = etree.SubElement(atb_root, 'mapinfo')
        mapinfo.text = os.path.join(rel_folder_path, 'mapinfo_' + book_name + '.dat')

        atb_tree = etree.ElementTree(atb_root)
        atb_tree.write(os.path.join(folder_path, book_name + '_data' + '.atb'), pretty_print=True, xml_declaration=True, encoding='utf-8')

        
    def get_audio_list(self):
        return self.audio_list

      
    def get_text(self):
        return self.text

      
    def get_word_list(self):
        return self.word_list

      
    def get_sec(self, word):
        self.mutex.acquire()
        sec = self.word_sec.get(word, None)
        self.mutex.release()
        return sec


    def get_word(self, audio_num, sec):
        self.mutex.acquire()
        audio_secs = self.seconds[audio_num]
        if len(audio_secs) == 0 or bisect_left(audio_secs, sec) == len(audio_secs):
            self.mutex.release()
            return None
        lb_sec_pos = bisect_left(audio_secs, sec)
        near_sec = audio_secs[lb_sec_pos] if audio_secs[lb_sec_pos] == sec else audio_secs[lb_sec_pos - 1]
        word = self.sec_word[audio_num][near_sec]
        self.mutex.release()
        return word
