# -*- coding: utf-8 -*-

import sys, os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'audio_text_mapper'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'atb_model'))

import unittest
from statistics import mean
from audio_text_mapper import ATMapper
from atb_model import Model


class test_audio_text_mapper(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(test_audio_text_mapper, self).__init__(*args, **kwargs)
        self.test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'test_files')
        self.mdl = Model()
        self.mdl.load(os.path.join(self.test_path, 'book1_data.atb'))
        self.audio_paths = list(map(lambda path: path.replace('mp3', 'wav'), self.mdl.get_audio_list()))

        maxpos = 200
        dur = 90
        self.words = self.mdl.get_word_list()[:maxpos]
        self.durs = [dur]


    def test_chunk_search_correct(self):
        mapper = ATMapper(self.words, self.audio_paths, self.durs)
        chunk = ['а', 'от', 'них', 'никак', 'нельзя', 'было', 'ожидать']
        startp = 0
        endp = 100
        match_pos = mapper.chunk_search(chunk, startp, endp)
        correct_pos = 40
        self.assertEqual(match_pos, correct_pos)


    def test_chunk_search_with_mistake(self):
        mapper = ATMapper(self.words, self.audio_paths, self.durs)
        chunk = ['а', 'вт', 'ник', 'микак', 'нельзя', 'мыло', 'ажедать']
        startp = 0
        endp = 100
        match_pos = mapper.chunk_search(chunk, startp, endp)
        correct_pos = 40
        self.assertEqual(match_pos, correct_pos)

    """
    def test_recognize(self):
        mapper = ATMapper(self.words, self.audio_paths, self.durs)
        print(mapper.recognize(self.audio_paths[0], self.durs[0]))
    """

    """
    def test_map_words(self):
        mapper = ATMapper(self.words, self.audio_paths, self.durs)
        print(mapper.map_words())
    """


    def test_make_mapping(self):
        mapper = ATMapper(self.words, self.audio_paths, self.durs)
        secs = [5 * i for i in range(17)]
        word_nums = [13, 24, 33, 45, 54, 63, 70, 77, 88, 98, 112, 122, 131, 142, 155, 165, 175]
        mapper.make_mapping()
        diff = [mapper.sec_word[0][sec] - correct_num for sec, correct_num in zip(secs, word_nums)]
        print('Average inaccuracy: {0}'.format(mean(diff)))


if __name__ == '__main__':
    unittest.main()
