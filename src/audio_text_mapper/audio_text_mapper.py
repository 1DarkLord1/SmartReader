# -*- coding: utf-8 -*-

from collections import namedtuple
import speech_recognition as sr
from statistics import mean
from Levenshtein import distance
import threading
from numpy import linalg
import math


class ATMapper:
    def __init__(self, atb_mdl):
        self.mdl = atb_mdl
        self.Chunk = namedtuple('Chunk', ['text', 'tstart'])
        self.Time = namedtuple('Time', ['audio_num', 'sec'])
        self.Markup = namedtuple('Markup', ['word_num', 'sec'])
        self.startp = 0
        self.last_chunk = self.Chunk('', 0)
        self.last_inv_speed = 0.4
        self.prev_chunk_pos = None
        self.prev_dur = None
        self.start = None


    def recognize_all(self):
        chunk_time = 15
        audio_num = 0
        for dur, audio_path in zip(self.mdl.durs, self.mdl.wav_list):
            self.recognize(audio_path, audio_num, dur, chunk_time)
            audio_num += 1


    def get_startp(self, audio_path, audio_num, chunk_time):
        rec = sr.Recognizer()
        audio = sr.AudioFile(audio_path)
        start_time = 0
        with audio as source:
            recorded = rec.record(source, duration=chunk_time)
            recognized = ''
            try:
                recognized = rec.recognize_google(recorded, language='ru-RU')
            except Exception as e:
                pass

            #chunk_words = list(map(lambda word: word.lower(), recognized.split(' ')))

            word_l = recognized.split()
            chunk_words = []
            for word in word_l:
                new_word = ''.join(list(filter(lambda ch: ch.isalpha() or ch.isdigit(), word))).lower()
                if new_word != '':
                    chunk_words.append(new_word)

            # print(chunk_words)

            recognized_chunk = self.Chunk(chunk_words, start_time)

            self.start = self.chunk_find(recognized_chunk, self.startp)
            end = self.start + len(recognized_chunk.text)
            segment_markup = self.map_segment(self.start, end, 0, chunk_time)
            self.write_mapinfo(audio_num, segment_markup)
            return end


    def recognize(self, audio_path, audio_num, dur, chunk_time):
        self.startp = self.get_startp(audio_path, audio_num, chunk_time)
        # div_coef = 2
        # pow_coef = 1 / 3
        # segm_count = math.ceil(dur ** pow_coef / div_coef)
        # fix issue with audio optimal segmentation

        if self.prev_chunk_pos:
            segment_markup = self.map_segment(self.prev_chunk_pos, self.start, self.last_chunk.tstart, self.prev_dur)
            self.write_mapinfo(audio_num - 1, segment_markup)

        self.prev_dur = dur

        segm_count = math.ceil(dur / 180)
        fragm_step = math.floor(dur / segm_count)
        rec = sr.Recognizer()
        audio = sr.AudioFile(audio_path)
        last_failed = False
        self.last_chunk = self.Chunk('', chunk_time)
        with audio as source:
            rec.adjust_for_ambient_noise(source)
            for time in range(fragm_step, dur + 1, fragm_step):
                #if abs(dur - time) < fragm_step:
                 #   time = dur
                start_time = time - chunk_time

                recorded = rec.record(source, offset=fragm_step - chunk_time, duration=chunk_time)
                recognized = ''
                try:
                    recognized = rec.recognize_google(recorded, language='ru-RU')
                except Exception as e:
                    if time == dur:
                        last_failed = True
                    continue
                #chunk_words = list(map(lambda word: word.lower(), recognized.split(' ')))

                word_l = recognized.split()
                chunk_words = []
                for word in word_l:
                    new_word = ''.join(list(filter(lambda ch: ch.isalpha() or ch.isdigit(), word))).lower()
                    if new_word != '':
                        chunk_words.append(new_word)

                # print(chunk_words)
                recognized_chunk = self.Chunk(chunk_words, start_time)
                self.make_mapping(recognized_chunk, audio_num, dur, time)

            if last_failed:
                segm_dur = dur - self.last_chunk.tstart
                markup = self.map_segment(self.startp, math.ceil(self.startp + segm_dur * self.last_inv_speed),
                                          self.last_chunk.tstart, dur)
                self.write_mapinfo(audio_num, markup)


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
        self.last_inv_speed = (end_pos - start_pos) / dur
        return [self.Markup(word_num, start_time + (dur / syll_cnt[-1]) * syll_cnt[word_num - start_pos]) for word_num
                in range(start_pos, end_pos)]


    def chunk_find(self, chunk, startp):
        chunk_pos = self.chunk_search(chunk.text, startp, len(self.mdl.word_list))
        return chunk_pos


    def make_mapping(self, chunk, audio_num, dur, endt):
        chunk_pos = self.chunk_find(chunk, self.startp)
        segment_markup = self.map_segment(self.startp, chunk_pos, self.last_chunk.tstart, chunk.tstart)
        if endt != dur:
            self.startp = chunk_pos
        self.last_chunk = chunk
        self.prev_chunk_pos = chunk_pos
        self.write_mapinfo(audio_num, segment_markup)


    def write_mapinfo(self, audio_num, markup):
        self.mdl.mutex.acquire()
        self.mdl.sec_word[audio_num].update([(word.sec, word.word_num) for word in markup])
        self.mdl.word_sec.update([(word.word_num, self.Time(audio_num, word.sec)) for word in markup])
        self.mdl.seconds[audio_num] += [word.sec for word in markup]
        self.mdl.mutex.release()
