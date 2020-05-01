# -*- coding: utf-8 -*-

from collections import namedtuple
import speech_recognition as sr

class ATMapper:
    def __init__(self, path, dur):
        self.path = path
        self.dur = dur


    def recognize(self):
        recognized_text = []
        chunk_time = 5
        rec = sr.Recognizer()
        audio = sr.AudioFile(self.path)
        with audio as source:
            recorded = rec.record(source)
            for time in range(0, self.dur, chunk_time)
                recognized_text.append(namedtuple('Chunk', ['text', 'dur'])
                (rec.recognize_google(recorded, language="ru-RU", duration=chunk_time), time))
        return recognized_text


    def calc_levenshtein(self, first, second, i, j, dist):
        if i == 0 or j == 0:
            dist[i][j] = max(i, j)
        elif not(dist[i][j] is None):
            return
        else:
            self.calc_levenshtein(first, second, i - 1, j, dist)
            self.calc_levenshtein(firt, second, i, j - 1, dist)
            dist[i][j] = min(min(dist[i - 1][j], dist[i][j - 1]) + 1, dist[i - 1][j - 1] + first[i] != second[j])


    def levenshtein_metrics(self, first, second):
        first = ' ' + first
        second = ' ' + second
        dist = [[None for i in range(len(first))] for i in range(len(second))]
        self.calc_levenshtein(first, second, 0, 0, dist)
        return dist[len(first) - 1][len(second) - 1]


    def chunk_search(self):
        pass
