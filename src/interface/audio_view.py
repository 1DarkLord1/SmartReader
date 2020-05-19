from kivy.core.audio import SoundLoader, Sound


class AudioView:
    class Music(Sound):
        def __init__(self, file, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.sound = SoundLoader.load(file)

    def __init__(self, audio_list, music_button, time_label, cur_volume, slider):
        self.play_list = audio_list
        self.audio_file = self.Music(self.play_list[0])
        self.cur_volume = cur_volume
        self.time_label = time_label
        self.audio_file.sound.volume = self.cur_volume / 100
        self.cur_audio = 0
        self.audio_len = ""
        self.time_label.text = self.get_audio_len()
        self.is_play = False
        self.music_button = music_button
        self.slider = slider

    def play_or_stop(self):
        if not self.is_play:
            if self.audio_file.sound:
                self.audio_file.sound.play()
                self.music_button.icon = 'pause-circle-outline'
                self.is_play = True
        else:
            if self.audio_file.sound:
                self.audio_file.sound.stop()
                self.music_button.icon = 'play-circle-outline'
                self.is_play = False

    def move_pos_audio(self, value):
        length = self.audio_file.sound.length
        time_r = (value / 100) * length
        time = int(time_r)
        self.audio_file.sound.seek(time_r)
        self.time_label.text = self.make_time_str(time) + '/' + self.audio_len

    def next_audio(self):
        if self.cur_audio + 1 < len(self.play_list):
            self.cur_audio += 1
            if self.audio_file.sound.on_play:
                self.audio_file.sound.stop()
            self.audio_file = self.Music(self.play_list[self.cur_audio])
            self.time_label.text = self.get_audio_len()
            self.slider.value = 0

    def prev_audio(self):
        if self.cur_audio - 1 >= 0:
            self.cur_audio -= 1
            if self.audio_file.sound.on_play:
                self.audio_file.sound.stop()
            self.audio_file = self.Music(self.play_list[self.cur_audio])
            self.time_label.text = self.get_audio_len()

    def get_audio_len(self):
        length = int(self.audio_file.sound.length)
        self.audio_len = self.make_time_str(length)
        return "00:00/" + self.audio_len

    @staticmethod
    def make_time_str(time):
        minutes = time // 60
        sec = time % 60
        if minutes < 10:
            res = '0' + str(minutes)
        else:
            res = str(minutes)
        if sec < 10:
            res += ':0' + str(sec)
        else:
            res += ':' + str(sec)
        return res

    def timer_callback(self, dt):
        self.slider.value = (self.audio_file.sound.get_pos() / self.audio_file.sound.length) * 100
        time = int(self.audio_file.sound.get_pos())
        self.time_label.text = self.make_time_str(time) + '/' + self.audio_len
