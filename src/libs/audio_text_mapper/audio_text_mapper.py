# -*- coding: utf-8 -*-

from collections import namedtuple
import speech_recognition as sr
from statistics import mean

class ATMapper:
    def __init__(self, words, audio_paths, durs):
        self.audio_paths = audio_paths
        self.durs = durs
        self.words = words
        self.word_sec = None
        self.sec_word = None


    def recognize(self, audio_path, dur, chunk_time=5):
        recognized_chunks = []
        rec = sr.Recognizer()
        audio = sr.AudioFile(audio_path)
        with audio as source:
            recorded = rec.record(source)
            for time in range(0, dur, chunk_time)
                chunk_words = rec.recognize_google(recorded, language="ru-RU", duration=chunk_time).split(' ')
                recognized_words.append(namedtuple('Chunk', ['text', 'tstart', 'tend'])
                (chunk_words, time, time + min(dur - time, chunk_time)))
        return recognized_chunks


    def calc_levenshtein(self, first, second, i, j, dist):
        if i == 0 or j == 0:
            dist[i][j] = max(i, j)
        elif not(dist[i][j] is None):
            return
        else:
            self.calc_levenshtein(first, second, i - 1, j, dist)
            self.calc_levenshtein(first, second, i, j - 1, dist)
            dist[i][j] = min(min(dist[i - 1][j], dist[i][j - 1]) + 1, dist[i - 1][j - 1] + first[i] != second[j])


    def levenshtein_metrics(self, first, second):
        first = ' ' + first
        second = ' ' + second
        dist = [[None for i in range(len(first))] for i in range(len(second))]
        self.calc_levenshtein(first, second, 0, 0, dist)
        return dist[-1][-1]


    def average_metrics(self, chunk, text_words):
        return mean([self.levenshtein_metrics(chunk_word, text_word) for chunk_word, text_word in zip(chunk, text_words)


    def chunk_search(self, chunk, begin, end):
        end = end - len(chunk) + 1
        matches = [(i, self.average_metrics(chunk, words[i:i + len(chunk)])) for i in range(begin, end)]
        return min(poses, key=lambda match: match[1])[0]


    def map_words(self):
        deep_coef = 8
        markup = []
        pos = 0
        for audio_path, dur in zip(self.audio_paths, self.durs):
            chunks = self.recognize(audio_path, dur)
            for chunk in chunks:
                if chunk.text = '':
                    continue
                chunk_pos = self.chunk_search(chunk.text, pos, min(pos + deep_coef * len(chunk), len(words)))
                markup.append(namedtuple('Markup', ['tstart', 'tend', 'num'])(chunk.tstart, chunk.tend, chunk_pos))
                pos = chunk_pos + len(chunk)
        return markup


    def make_mapping(self):
        markup = self.map_words()
        self.word_sec = {i:None for i in range(len(words)}
        self.sec_word = []
        for i in range(len(markup)):
            pos = markup[i].num
            nextpos = markup[i + 1].num if i + 1 < len(markup) else len(words)
            aver_speed = float(nextpos - pos) / (markup[i].tend - markup[i].tstart)
            chunk_word_sec = [(wordnum, markup[i].tstart + (wordnum - pos) * aver_speed) for wordnum in range(pos, nextpos)]
            chunk_sec_word = [chunk[::-1] for chunk in chunk_word_sec]
            self.word_sec.update(chunk_word_sec)
            if markup[i].tstart == 0:
                self.sec_word.append(dict(chunk_sec_word))
            else:
                self.sec_word[-1].update(dict(chink_sec_word))

        assert not(None in set(self.word_sec.values()))
