# -*- coding: utf-8 -*-

from collections import namedtuple
import speech_recognition as sr
from statistics import mean
from Levenshtein import distance
import threading
from numpy import linalg
import math


class ATMapper:
    def __init__(self, atb_mdl, last_inv_speed, div_coef, pow_coef):
        self.mdl = atb_mdl
        self.Chunk = namedtuple('Chunk', ['text', 'tstart', 'pos'])
        self.Time = namedtuple('Time', ['audio_num', 'sec'])
        self.Markup = namedtuple('Markup', ['word_num', 'sec'])
        self.startp = 0
        self.last_chunk = self.Chunk([], 0, None)


    def handle_end(self, audio_num, endp):
        if self.last_chunk.pos:
            self.write_mapinfo(audio_num, self.map_segment(self.last_chunk.pos, endp, self.last_chunk.tstart, self.mdl.durs[audio_num]))


    def map_all(self):
        chunk_time = 15
        audio_num = 0
        for dur, audio_path in zip(self.mdl.durs, self.mdl.wav_list):
            self.make_mapping(audio_path, audio_num, dur, chunk_time)
            audio_num += 1


    def get_chunk(self, recognized, start_pos, time):
        chunk_words = [''.join(list(filter(lambda ch: ch.isalpha() or ch.isdigit(), word))).lower()
                        for word in recognized.split()]
        chunk_words = list(filter(lambda word: word != '', chunk_words))
        recognized_chunk = self.Chunk(chunk_words, time, self.chunk_find(chunk_words, start_pos))
        return recognized_chunk


    def handle_start(self, audio_path, audio_num, chunk_time):
        rec = sr.Recognizer()
        audio = sr.AudioFile(audio_path)
        start_time = 0
        recognized = ''
        with audio as source:
            recorded = rec.record(source, duration=chunk_time)
            try:
                recognized = rec.recognize_google(recorded, language='ru-RU')
            except Exception as e:
                return
        chunk = self.get_chunk(recognized, self.startp, start_time)
        self.startp = chunk.pos
        self.write_mapinfo(audio_num, self.map_segment(chunk.pos, chunk.pos + len(chunk.text), chunk.tstart, chunk.tstart + chunk_time))
        return chunk.pos, chunk.pos + len(chunk.text)


    def make_mapping(self, audio_path, audio_num, dur, chunk_time):
        start_chunk_pos, self.startp = self.handle_start(audio_path, audio_num, chunk_time)
        self.handle_end(audio_num - 1, start_chunk_pos)
        self.last_chunk = self.Chunk([], chunk_time, start_chunk_pos)
        segm_count = math.ceil(dur ** pow_coef / div_coef)
        fragm_step = math.floor(dur / segm_count)
        rec = sr.Recognizer()
        audio = sr.AudioFile(audio_path)
        with audio as source:
            for time in range(fragm_step, dur + 1, fragm_step):
                recorded = rec.record(source, offset=fragm_step - chunk_time, duration=chunk_time)
                recognized = ''
                try:
                    recognized = rec.recognize_google(recorded, language='ru-RU')
                except Exception as e:
                    continue
                chunk = self.get_chunk(recognized, self.startp, time - chunk_time)
                segment_markup = self.map_segment(self.startp, chunk.pos, self.last_chunk.tstart, chunk.tstart)
                self.last_chunk = chunk
                self.startp = chunk.pos
                self.write_mapinfo(audio_num, segment_markup)
        if audio_num == len(self.mdl.audio_list) - 1 and abs(len(self.mdl.word_list) - (self.last_chunk.tstart + chunk_time)) < fragm_step:
            self.handle_end(len(self.mdl.audio_list) - 1, len(self.mdl.word_list))
        else:
            self.write_mapinfo(audio_num, self.map_segment(self.startp, math.floor(self.last_chunk.pos + last_inv_speed * (dur - self.last_chunk.tstart)),
            self.last_chunk.tstart, dur))


    def average_metrics(self, chunk, text_words):
        return mean([distance(chunk_word, text_word) for chunk_word, text_word in zip(chunk, text_words)])


    def chunk_search(self, chunk, startp, endp):
        endp = endp - len(chunk) + 1
        matches = [(i, self.average_metrics(chunk, self.mdl.word_list[i:i + len(chunk)])) for i in range(startp, endp)]
        return min(matches, key=lambda match: match[1])[0]


    def map_segment(self, start_pos, end_pos, start_time, end_time):
        dur = end_time - start_time
        syll_cnt = [0]
        symbs = {'а', 'о', 'е', 'и', 'ы', 'у', 'э', 'ё', 'я', 'ю', '.', '?', '!'}
        for word_num in range(start_pos, end_pos):
            word = self.mdl.word_list[word_num]
            syll_cnt.append(syll_cnt[-1] + sum(1 if ch[1] in symbs else 0 for ch in enumerate(word)))
        last_inv_speed = (end_pos - start_pos) / dur
        return [self.Markup(word_num, start_time + (dur / syll_cnt[-1]) * syll_cnt[word_num - start_pos]) for word_num
                in range(start_pos, end_pos)]


    def chunk_find(self, chunk, startp):
        return self.chunk_search(chunk, startp, len(self.mdl.word_list))


    def write_mapinfo(self, audio_num, markup):
        self.mdl.mutex.acquire()
        self.mdl.sec_word[audio_num].update([(word.sec, word.word_num) for word in markup])
        self.mdl.word_sec.update([(word.word_num, self.Time(audio_num, word.sec)) for word in markup])
        self.mdl.seconds[audio_num] += [word.sec for word in markup]
        self.mdl.mutex.release()
