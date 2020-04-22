# -*- coding: utf-8 -*-

import unittest, sys, os
dir = '/home/dword/Desktop/SmartReader/src/libs/atb_model/'
sys.path.insert(0, dir)
from atb_model import Model

test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class test_atb_model(unittest.TestCase):

    def test_simple_get_audio_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'test_files', 'simple.atb')
        mdl.load(dir)
        correct_audio_list = ['1.mp3', '2.mp3', '3.mp3', '4.mp3']
        self.assertEqual(mdl.get_audio_list(), correct_audio_list)


    def test_hard_names_get_audio_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'test_files', 'hard_names.atb')
        mdl.load(dir)
        correct_audio_list = ['dwdawsdw.mp3', '^12e31.mp3', 'sFSDSA.mp3', 'dsaxaS.mp3',
        '2`3WEFFECWDA.mp3', 'DCESXMXK.mp3', '7xsxs.mp3', '213dom,.mp3', 'xazz.mp3',
        'dekassx.mp3', 'xwqslq.mp3', 'pf[]q.mp3', 'sxzxx.mp3', '120DWS.mp3', 'DDS.mp3']
        self.assertEqual(mdl.get_audio_list(), correct_audio_list)


    def test_book1_get_word_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'test_files', 'book1_data.atb')
        mdl.load(dir)
        correct_word_list = ['Дж', 'К', 'Ролинг', 'Гарри', 'Поттер', 'и', 'философский', 'камень', 'Глава',
        '1', 'Мальчик', 'который', 'выжил', 'Мистер', 'и', 'миссис', 'Дурсль', 'проживали', 'в', 'доме', 'номер', 'четыре',
        'по', 'Тисовой', 'улице', 'и', 'всегда', 'с', 'гордостью', 'заявляли', 'что', 'они']
        correct_word_list = [word.decode('utf-8') for word in correct_word_list]
        self.assertEqual(mdl.get_word_list()[:len(correct_word_list)], correct_word_list)


    def test_book2_get_word_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'test_files', 'book2_data.atb')
        mdl.load(dir)
        correct_word_list = ['Николай', 'Васильевич', 'Гоголь', 'Записки', 'сумасшедшего', 'Октября',
        '3', 'Сегодняшнего', 'дня', 'случилось', 'необыкновенное', 'приключение', 'Я', 'встал', 'поутру', 'довольно']
        correct_word_list = [word.decode('utf-8') for word in correct_word_list]
        self.assertEqual(mdl.get_word_list()[:len(correct_word_list)], correct_word_list)


    def test_book3_get_word_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'test_files', 'book3_data.atb')
        mdl.load(dir)
        correct_word_list = ['Илья', 'Ильф', 'Евгений', 'Петров', 'Собрание', 'сочинений', 'в', 'пяти', 'томах', 'Том', '1', 'Двенадцать',
        'стульев', 'Двенадцать', 'стульев', 'Посвящается', 'Валентину', 'Петровичу', 'Катаеву', 'Часть']
        correct_word_list = [word.decode('utf-8') for word in correct_word_list]
        self.assertEqual(mdl.get_word_list()[:len(correct_word_list)], correct_word_list)


    def test_book4_get_word_list(self):
        mdl = Model()
        dir = os.path.join(test_path, 'test_files', 'book4_data.atb')
        mdl.load(dir)
        correct_word_list = ['Том', 'первый', 'Глава', 'I', 'Несколько', 'лет', 'тому', 'назад', 'в', 'одном', 'из', 'своих',
         'поместий', 'жил', 'старинный', 'русский', 'барин', 'Кирила', 'Петрович', 'Троекуров']
        correct_word_list = [word.decode('utf-8') for word in correct_word_list]
        self.assertEqual(mdl.get_word_list()[:len(correct_word_list)], correct_word_list)


    def test_book1_get_text(self):
        mdl = Model()
        dir = os.path.join(test_path, 'test_files', 'book1_data.atb')
        mdl.load(dir)
        correct_text = 'Дж. К. Ролинг\nГарри Поттер и философский камень\n\nГлава 1\nМальчик, который выжил\n\nМистер и миссис Дурсль проживали'+\
        ' в доме номер четыре по Тисовой улице и всегда с гордостью заявляли, что они, слава богу, абсолютно нормальные люди.'+\
         ' Уж от кого-кого, а от них никак нельзя было ожидать, чтобы они попали'
        correct_text = correct_text.decode('utf-8')
        self.assertEqual(mdl.get_text()[:len(correct_text)], correct_text)


if __name__ == '__main__':
    unittest.main()
