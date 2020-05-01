from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader, Sound
from kivy.uix.popup import Popup
from kivy.clock import Clock
import sys
sys.path.insert(0, "../libs/atb_model")
from atb_model import Model


# Window.size = (1920, 1080)


class Container(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.atb_model = Model()
        self.atb_model.load("../test/test_files/example_atb/book1_data.atb")
        self.last_words = []
        self.pages = self.slice_pages(self.atb_model.get_text(), 100, 50)
        self.cur_page = 0
        if len(self.pages) > 0:
            self.left_page.text = self.pages[0]
        if len(self.pages) > 1:
            self.right_page.text = self.pages[1]
        self.play_list = self.atb_model.get_audio_list()
        self.audio_file = self.Music(self.play_list[0])
        self.cur_audio = 0
        self.audio_len = ""
        self.time.text = self.get_audio_len()
        self.cur_ref = 0
        self.vol_popup = self.VolumePopup()
        self.vol_popup.bind(volume=self.change_volume)
        self.go_to_audio_popup = self.GoToAudio()
        self.go_to_audio_popup.bind(func=self.go_to_pos_audio)

    def change_text_r(self):
        if self.cur_page + 3 < len(self.pages):
            self.left_page.text = self.pages[self.cur_page + 2]
            self.right_page.text = self.pages[self.cur_page + 3]
            self.cur_page += 2
        else:
            if self.cur_page + 2 < len(self.pages):
                self.left_page.text = self.pages[self.cur_page + 2]
                self.right_page.text = ""
                self.cur_page += 2

    def change_text_l(self):
        if self.cur_page - 2 >= 0:
            self.left_page.text = self.pages[self.cur_page - 2]
            self.right_page.text = self.pages[self.cur_page - 1]
            self.cur_page -= 2

    def play_or_stop(self):
        if self.music_button.state == 'down':
            self.music_button.text = "Stop"
            if self.audio_file.sound:
                self.audio_file.sound.play()

        else:
            self.music_button.text = "Play"
            if self.audio_file.sound:
                self.audio_file.sound.stop()

    def move_pos_audio(self, value):
        length = self.audio_file.sound.length
        time_r = (value / 100) * length
        time = int(time_r)
        self.audio_file.sound.seek(time_r)
        self.time.text = self.make_time_str(time) + '/' + self.audio_len

    def next_audio(self):
        if self.cur_audio + 1 < len(self.play_list):
            self.cur_audio += 1
            if self.audio_file.sound.on_play:
                self.audio_file.sound.stop()
            self.audio_file = self.Music(self.play_list[self.cur_audio])
            self.time.text = self.get_audio_len()
            self.slider.value = 0

    def prev_audio(self):
        if self.cur_audio - 1 >= 0:
            self.cur_audio -= 1
            if self.audio_file.sound.on_play:
                self.audio_file.sound.stop()
            self.audio_file = self.Music(self.play_list[self.cur_audio])
            self.time.text = self.get_audio_len()

    def volume_slider_open(self):
        self.vol_popup.open()

    def change_volume(self, instance, value):
        self.audio_file.sound.volume = value / 100

    def ref_press(self, instance, ref):
        self.cur_ref = self.ref_to_word_num(ref)
        self.go_to_audio_popup.open()

    @staticmethod
    def ref_to_word_num(ref):
        res = ref[1:-1]
        return int(res)

    def get_audio_len(self):
        length = int(self.audio_file.sound.length)
        self.audio_len = self.make_time_str(length)
        return "00:00/" + self.audio_len

    def go_to_book(self):
        self.audio_file.sound.stop()
        word_num = self.atb_model.get_word_num([self.cur_audio, self.audio_file.sound.get_pos])
        ind = 0
        while self.last_words[ind] < word_num:
            ind += 1
        if ind < len(self.pages):
            if ind % 2 == 0:
                self.left_page.text = self.pages[ind]
                self.right_page.text = self.pages[ind + 1]
                self.cur_page = ind
            else:
                self.left_page.text = self.pages[ind - 1]
                self.right_page.text = self.pages[ind]
                self.cur_page = ind - 1

    def go_to_pos_audio(self, instance, value):
        pos = self.atb_model.get_sec(self.cur_ref)
        self.audio_file = self.Music(self.play_list[pos])
        self.audio_file.sound.seek(pos)
        self.time.text = self.get_audio_len()

    def my_callback(self, dt):
        self.slider.value = (self.audio_file.sound.get_pos() / self.audio_file.sound.length) * 100
        time = int(self.audio_file.sound.get_pos())
        self.time.text = self.make_time_str(time) + '/' + self.audio_len

    def move_slider(self):
        Clock.schedule_interval(self.my_callback, 1)
        return 0

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

    class Slicer:
        def __init__(self, p1, p2):
            self.str_len = 0
            self.cnt_str = 0
            self.page = ""
            self.pages = []
            self.last_words = []
            self.words_in_str = p1
            self.num_of_str = p2

        def add_str_to_list(self, s, cnt):
            self.str_len += 1
            if (self.str_len >= self.words_in_str and s == ' ') or s == '\n':
                self.cnt_str += 1
                self.str_len = 0
            if self.cnt_str >= self.num_of_str:
                self.cnt_str = 0
                self.pages.append(self.page)
                self.last_words.append(cnt - 1)
                self.page = ""

    def slice_pages(self, data, words_in_str, num_str):
        cnt = 0
        beg = 0
        end = 0
        slicer = self.Slicer(words_in_str, num_str)
        while end < len(data):
            s = data[end]
            if data[end] == ' ' or data[end] == '\n':
                if beg != end:
                    word = data[beg:end]
                    slicer.page += "[ref=<{}>]{}[/ref]".format(str(cnt), word)
                    cnt += 1
                slicer.page += data[end]
                end += 1
                beg = end
            else:
                end += 1
            slicer.add_str_to_list(s, cnt)
        slicer.pages.append(slicer.page)
        self.last_words = slicer.last_words
        return slicer.pages

    class Music(Sound):
        def __init__(self, file, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.sound = SoundLoader.load(file)

    class VolumePopup(Popup):
        pass

    class GoToAudio(Popup):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def go_to_audio(self):
            self.dismiss()
            self.func += 1


class SmartReaderApp(App):
    def build(self):
        return Container()


if __name__ == '__main__':
    SmartReaderApp().run()

