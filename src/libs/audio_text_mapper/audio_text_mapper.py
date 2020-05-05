# -*- coding: utf-8 -*-

from collections import namedtuple
import speech_recognition as sr
from statistics import mean
from Levenshtein import distance
from bisect import bisect_left

class ATMapper:
    def __init__(self, words, audio_paths, durs):
        self.audio_paths = audio_paths
        self.durs = durs
        self.words = words
        self.word_sec = None
        self.sec_word = None
        self.seconds = None


    def recognize(self, audio_path, dur, chunk_time=5):
        recognized_chunks = []
        rec = sr.Recognizer()
        audio = sr.AudioFile(audio_path)
        with audio as source:
            for time in range(0, dur, chunk_time):
                recorded = rec.record(source, duration=chunk_time)
                chunk_words = list(map(lambda word: word.lower(), rec.recognize_google(recorded, language="ru-RU").split(' ')))
                recognized_chunks.append(namedtuple('Chunk', ['text', 'tstart', 'tend'])
                (chunk_words, time, time + min(dur - time, chunk_time)))
        return recognized_chunks


    def average_metrics(self, chunk, text_words):
        return mean([distance(chunk_word, text_word) for chunk_word, text_word in zip(chunk, text_words)])


    def chunk_search(self, chunk, startp, endp):
        endp = endp - len(chunk) + 1
        matches = [(i, self.average_metrics(chunk, self.words[i:i + len(chunk)])) for i in range(startp, endp)]
        return min(matches, key=lambda match: match[1])[0]


    def map_words(self):
        deep_coef = 8
        markup = []
        pos = 0
        for audio_path, dur in zip(self.audio_paths, self.durs):
            chunks = self.recognize(audio_path, dur)
            for chunk in chunks:
                if chunk.text == '':
                    continue
                chunk_pos = self.chunk_search(chunk.text, pos, min(pos + deep_coef * len(chunk), len(self.words)))
                markup.append(namedtuple('Markup', ['tstart', 'tend', 'num'])(chunk.tstart, chunk.tend, chunk_pos))
                pos = chunk_pos + len(chunk)
        return markup


    def make_mapping(self):
        markup = self.map_words()
        self.word_sec = {}
        self.sec_word = []
        audio_num = 0
        for i in range(len(markup)):
            if markup[i].tstart == 0:
                audio_num += 1
                self.sec_word.append({})
            pos = markup[i].num
            nextpos = markup[i + 1].num if i + 1 < len(markup) else len(self.words)
            aver_speed = float(nextpos - pos) / (markup[i].tend - markup[i].tstart)
            chunk_word_sec = [(wordnum, namedtuple('Time', ['audio_num', 'sec'])(audio_num, markup[i].tstart + (wordnum - pos) * aver_speed))
            for wordnum in range(pos, nextpos)]
            chunk_sec_word = [(chunk[1].sec, chunk[0]) for chunk in chunk_word_sec]
            self.word_sec.update(dict(chunk_word_sec))
            self.sec_word[-1].update(dict(chunk_sec_word))

        seconds = sorted([time.sec for time in self.word_sec.values()])


    def get_word_sec(self):
        return self.word_sec


    def get_sec_word(self):
        return self.sec_word
