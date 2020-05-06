# -*- coding: utf-8 -*-

import unittest, sys, os
dir = '/home/dword/Desktop/SmartReader_denil_sharipov/src/libs/atb_model/'
sys.path.insert(0, dir)
from atb_model import Model

test_path = '/home/dword/Desktop/SmartReader_denil_sharipov/src/test/test_files/'

class test_atb_model(unittest.TestCase):

    def test_simple_get_audio_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'simple.atb')
        mdl.load(dir)
        correct_audio_list = ['1.mp3', '2.mp3', '3.mp3', '4.mp3']
        self.assertEqual(mdl.get_audio_list(), correct_audio_list)


    def test_hard_names_get_audio_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'hard_names.atb')
        mdl.load(dir)
        correct_audio_list = ['dwdawsdw.mp3', '^12e31.mp3', 'sFSDSA.mp3', 'dsaxaS.mp3',
        '2`3WEFFECWDA.mp3', 'DCESXMXK.mp3', '7xsxs.mp3', '213dom,.mp3', 'xazz.mp3',
        'dekassx.mp3', 'xwqslq.mp3', 'pf[]q.mp3', 'sxzxx.mp3', '120DWS.mp3', 'DDS.mp3']
        self.assertEqual(mdl.get_audio_list(), correct_audio_list)


    def test_book1_get_word_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'book1_data.atb')
        mdl.load(dir)
        correct_word_list = ['дж', 'к', 'ролинг', 'гарри', 'поттер', 'и', 'философский', 'камень', 'глава',
        '1', 'мальчик', 'который', 'выжил', 'мистер', 'и', 'миссис', 'дурсль', 'проживали', 'в', 'доме', 'номер', 'четыре',
        'по', 'тисовой', 'улице', 'и', 'всегда', 'с', 'гордостью', 'заявляли', 'что', 'они']
        self.assertEqual(mdl.get_word_list()[:len(correct_word_list)], correct_word_list)


    def test_book2_get_word_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'book2_data.atb')
        mdl.load(dir)
        correct_word_list = ['николай', 'васильевич', 'гоголь', 'записки', 'сумасшедшего', 'октября',
        '3', 'сегодняшнего', 'дня', 'случилось', 'необыкновенное', 'приключение', 'я', 'встал', 'поутру', 'довольно']
        self.assertEqual(mdl.get_word_list()[:len(correct_word_list)], correct_word_list)


    def test_book3_get_word_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'book3_data.atb')
        mdl.load(dir)
        correct_word_list = ['илья', 'ильф', 'евгений', 'петров', 'собрание', 'сочинений', 'в', 'пяти', 'томах', 'том', '1', 'двенадцать',
        'стульев', 'двенадцать', 'стульев', 'посвящается', 'валентину', 'петровичу', 'катаеву', 'часть']
        self.assertEqual(mdl.get_word_list()[:len(correct_word_list)], correct_word_list)


    def test_book4_get_word_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'book4_data.atb')
        mdl.load(dir)
        correct_word_list = ['том', 'первый', 'глава', 'i', 'несколько', 'лет', 'тому', 'назад', 'в', 'одном', 'из', 'своих',
         'поместий', 'жил', 'старинный', 'русский', 'барин', 'кирила', 'петрович', 'троекуров']
        self.assertEqual(mdl.get_word_list()[:len(correct_word_list)], correct_word_list)


    def test_book1_get_text(self):
        mdl = Model()
        dir = os.path.join(test_path, 'book1_data.atb')
        mdl.load(dir)
        correct_text = 'Дж. К. Ролинг\nГарри Поттер и философский камень\n\nГлава 1\nМальчик, который выжил\n\nМистер и миссис Дурсль проживали'+\
        ' в доме номер четыре по Тисовой улице и всегда с гордостью заявляли, что они, слава богу, абсолютно нормальные люди.'+\
         ' Уж от кого-кого, а от них никак нельзя было ожидать, чтобы они попали'
        self.assertEqual(mdl.get_text()[:len(correct_text)], correct_text)


if __name__ == '__main__':
    unittest.main()
