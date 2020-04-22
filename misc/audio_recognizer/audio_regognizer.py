from pydub import AudioSegment
from collections import namedtuple
import speech_recognition as sr
import os


dir = os.path.join(os.getcwd(), "audio")
full_audio = AudioSegment.from_mp3(os.path.join(dir, "book4.mp3"))
time_step = 4 * 1000
audio = full_audio[:10 * time_step]
dur_time = int(audio.duration_seconds * 1000)
times = [t * time_step for t in range(0, dur_time // time_step)]
audio_segs = [audio[t - time_step // 2 if t != 0 else t : min(t + time_step, dur_time)] for t in times]

for audio_seg in audio_segs:
    audio_seg.export(os.path.join(dir, "audio_seg.wav"), format="wav")
    audiofile = os.path.join(dir, "audio_seg.wav")
    recogn = sr.Recognizer()
    sr_audiofile = sr.AudioFile(audiofile)
    with sr_audiofile as source:
        sr_audio = recogn.record(source)
        try:
            print(recogn.recognize_google(sr_audio, language="ru-RU"))
        except:
            print("(...)")

    os.remove(audiofile)
