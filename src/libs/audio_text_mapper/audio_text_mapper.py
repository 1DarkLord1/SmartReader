# -*- coding: utf-8 -*-

from collections import namedtuple
import speech_recognition as sr
from statistics import mean

class ATMapper:
    def __init__(self, words, audio_paths, durs):
        self.audio_paths = audio_paths
        self.durs = durs
        self.words = words


    def recognize(self, audio_path, dur, chunk_time=5):
        recognized_words = []
        rec = sr.Recognizer()
        audio = sr.AudioFile(audio_path)
        with audio as source:
            recorded = rec.record(source)
            for time in range(0, dur, chunk_time)
                chunk_words = rec.recognize_google(recorded, language="ru-RU", duration=chunk_time).split(' ')
                recognized_words.append(namedtuple('Chunk', ['text', 'tstart', 'tend'])
                (chunk_words, time, time + min(dur - time, chunk_time)))
        return recognized_words


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


    def average_metrics(self, chunk, text_words):
        return mean([self.levenshtein_metrics(chunk_word, text_word) for chunk_word, text_word in zip(chunk, text_words)


    def chunk_search(self, chunk, begin, end):
        end = end - len(chunk) + 1
        matches = [(i, self.average_metrics(chunk, words[i:i + len(chunk)])) for i in range(begin, end)]
        return min(poses, key=lambda matches: matches[1])[0]


    
