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
import logging


class Model:
    def __init__(self, file=False):
        if file == True:
            logging.basicConfig(filename=gen_path('..', '..', 'logs', 'logs.txt'), filemode='w'))
        else:
            logging.basicConfig(level=logging.INFO)

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
        logging.info('get_fb2_root(): fb2_path={}\n'.format(fb2_path))
        fb2_path = gen_path(['..', '..', fb2_path])
        fb2_tree = etree.parse(fb2_path, etree.XMLParser(remove_blank_text=True))
        fb2_root = fb2_tree.getroot()
        for elem in fb2_root.getiterator():
            elem.tag = etree.QName(elem).localname
        etree.cleanup_namespaces(fb2_root)
        return fb2_root


    def load_fb2_text(self):
        logging.info('load_fb2_text()\n')
        book_path = self.root.find('fb2').text
        fb2_root = self.get_fb2_root(book_path)
        raw_text = etree.tostring(fb2_root.find('body'), encoding='utf-8').decode('utf-8')
        repl_cltag = '#~?$'
        self.text = re.sub('<.*?>', '', re.sub('</.*?>', repl_cltag, raw_text)).replace(repl_cltag, '\n')


    def make_word_list(self):
        logging_info('make_word_list()\n')
        self.word_list = [''.join(list(filter(lambda ch: ch.isalpha() or ch.isdigit(), word))).lower()
                         for word in self.text.split()]
        self.word_list = list(filter(lambda word: word != '', self.word_list))


    def parse_audio_list(self):
        logging.info('parse_audio_list()\n')
        audio = self.root.find('audio')
        self.audio_list = [gen_path(['..', '..', file.text]) for file in audio.findall('file')]


    def load(self, path):
        logging.info('load(): path={}\n'.format(path))
        self.tree = etree.parse(path, etree.XMLParser(remove_blank_text=True))
        self.root = self.tree.getroot()
        self.fb2_name = self.root.find('fb2').text.split('/')[-1].replace('.fb2', '')
        self.fb2_dir = self.root.find('fb2').text.replace(self.fb2_name + '.fb2', '')
        self.load_fb2_text()
        self.make_word_list()
        self.parse_audio_list()
        logging.info('Fb2 file {} loaded\n'.format(self.fb2_name))


    def create_wav_from_mp3(self, audio_path):
        logging.info('create_wav_from_mp3(): audio_path={}\n'.format(audio_path))
        source = AudioSegment.from_mp3(audio_path)
        wav_path = audio_path.replace('mp3', 'wav')
        source.export(wav_path, format='wav')
        logging.info('Wav file {} created\n'.format(wav_path))
        return int(source.duration_seconds)


    def make_mapping(self):
        logging.info('make_mapping()\n')
        self.durs = []
        for audio in self.audio_list:
            self.durs.append(self.create_wav_from_mp3(audio))
        logging.info('Wav files created\n')

        self.wav_list = list(map(lambda audio_path: audio_path.replace('mp3', 'wav'), self.audio_list))
        mapper = ATMapper(atb_mdl=self, last_inv_speed=0.4, div_coef=2.5, pow_coef=1/3)
        logging.info('ATMapper created\n')

        self.word_sec = {}
        self.sec_word = [{} for i in range(len(self.audio_list))]
        self.seconds = [[] for i in range(len(self.audio_list))]
        mapper.map_all()
        logging.info('All book mapped\n')

        for wav_audio in self.wav_list:
            os.remove(wav_audio)
        logging.info('Wav files removed\n')

        mapinfo_path = gen_path(['..', '..', self.fb2_dir, 'mapinfo_' + self.fb2_name + '.dat'])
        with open(mapinfo_path, "wb") as file:
            dill.dump(self.word_sec, file)
        logging.info('Mapinfo saved\n')


    def load_map(self):
        logging.info('load_map()\n')
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
        logging.info('Mapinfo loaded\n')


    def import_book(self, book_path, audio_paths):
        logging.info('import_book(): book_path={}, audio_paths={}\n'.format(book_path, audio_paths))
        book_name = book_path.split('/')[-1].replace('.fb2', '')
        folder_path = gen_path(['..', '..', self.root_name, book_name])
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.mkdir(folder_path)
        shutil.copyfile(book_path, os.path.join(folder_path, book_name + '.fb2'))
        logging.info('Books have been copied\n')
        for audio_path in audio_paths:
            shutil.copyfile(audio_path, os.path.join(folder_path, audio_path.split('/')[-1]))
        logging.info('Audios have been copied\n')
        rel_folder_path = os.path.join(self.root_name, folder_path.split('/')[-1])
        rel_book_path = os.path.join(rel_folder_path, book_name + '.fb2')
        rel_audio_paths = [os.path.join(rel_folder_path, path.split('/')[-1]) for path in audio_paths]
        self.make_atb(rel_book_path, book_name, rel_audio_paths, rel_folder_path, folder_path)


    def make_atb(self, book_path, book_name, audio_paths, rel_folder_path, folder_path):
        logging.info('make_atb(): book_path={}, book_name={}, audio_paths={}, rel_folder_path={}, folder_path={}\n'.format(book_path, book_name,
        audio_paths, rel_folder_path, folder_path))
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
        atb_tree.write(os.path.join(folder_path, book_name + '_data' + '.atb'), pretty_print=True, xml_declaration=True,
                       encoding='utf-8')
        logging.info('Atb created\n')


    def get_audio_list(self):
        logging.info('get_audio_list()\n')
        return self.audio_list


    def get_text(self):
        logging.info('get_text()\n')
        return self.text


    def get_word_list(self):
        logging.info('get_word_list()\n')
        return self.word_list

    def get_sec(self, word):
        self.mutex.acquire()
        logging.info('get_sec(): word={}\n'.format(word))
        sec = None
        if self.word_sec:
            sec = self.word_sec.get(word, None)
        self.mutex.release()
        return sec


    def get_word(self, audio_num, sec):
        self.mutex.acquire()
        logging.info('get_word(): audio_num={}, sec={}\n'.format(audio_num, sec))
        if not self.seconds:
            self.mutex.release()
            return None
        audio_secs = self.seconds[audio_num]
        if len(audio_secs) == 0 or bisect_left(audio_secs, sec) == len(audio_secs):
            self.mutex.release()
            return None
        lb_sec_pos = bisect_left(audio_secs, sec)
        near_sec = audio_secs[lb_sec_pos] if audio_secs[lb_sec_pos] == sec else audio_secs[lb_sec_pos - 1]
        word = self.sec_word[audio_num][near_sec]
        self.mutex.release()
        return word


    def get_len_word_sec(self):
        self.mutex.acquire()
        logging.info('get_len_word_sec()\n')
        res = 0
        if self.word_sec:
            res = round(len(self.word_sec) / len(self.word_list) * 100, 1)
        self.mutex.release()
        return res
