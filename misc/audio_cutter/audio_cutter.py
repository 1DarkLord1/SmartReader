from pydub import AudioSegment
from collections import namedtuple
import os


dir = os.path.join(os.getcwd(), "audio")
cnt = 4
audios = []
for i in range(1, cnt + 1):
    audio = AudioSegment.from_mp3(os.path.join(dir, "book" + str(i) + ".mp3"))
    audios.append(audio)

time_step = 1 * 1000
procd_audios =
    [namedtuple('Audio', ['audio', 'dur_time', 'times'])
    (audio, int(audio.duration_seconds * 1000),
    [t * time_step for t in range(0, int(audio.duration_seconds * 1000) // time_step)])
    for audio in audios]
audio_segs = []

for audio in procd_audios:
    audio_segs.append([audio.audio[t: min(t + time_step, audio.dur_time)] for t in audio.times])

for audio_seg_set in audio_segs:
    print("This loop splitted on " + str(len(audio_seg_set)) + " loops")
