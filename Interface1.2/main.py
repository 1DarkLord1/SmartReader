import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.slider import Slider
from kivy.properties import ObjectProperty
from kivy.uix.togglebutton import ToggleButton
from kivy.core.audio import SoundLoader, Sound
from kivy.uix.popup import Popup
from kivy.clock import Clock


# Window.size = (1920, 1080)

class Music(Sound):
    def __init__(self, file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sound = SoundLoader.load(file)


class VolumePopup(Popup):
    pass


class GoToAudio(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cur_ref = ""
        self.audio_pos = []

    def go_to_audio(self):
        self.dismiss()
        self.func += 1
        print(self.cur_ref)


class Slicer:
    def __init__(self):
        self.str_len = 0
        self.cnt_str = 0
        self.page = ""
        self.pages = []

    def add_str_to_list(self, s):
        self.str_len += 1
        if (self.str_len >= 100 and s == ' ') or s == '\n':
            self.cnt_str += 1
            self.str_len = 0
        if self.cnt_str >= 50:
            self.cnt_str = 0
            self.pages.append(self.page)
            self.page = ""


def slice_pages():
    handle = open("test.txt", "r")
    data = handle.read()
    handle.close()
    cnt = 0
    beg = 0
    end = 0
    slicer = Slicer()
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
        slicer.add_str_to_list(s)
    slicer.pages.append(slicer.page)
    return slicer.pages


def get_audio(pos):
    audio_list = ['book1.mp3', 'numb.mp3']
    return Music(audio_list[pos])


def get_audio_list_len():
    return 2


class Container(BoxLayout):
    list = ObjectProperty(slice_pages())
    cnt = ObjectProperty(0)
    audio_file = ObjectProperty(get_audio(0))
    cur_audio = ObjectProperty(0)
    len_audio_list = ObjectProperty(get_audio_list_len())
    audio_len = ObjectProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vol_popup = VolumePopup()
        self.vol_popup.bind(volume=self.change_volume)
        self.go_to_audio_popup = GoToAudio()
        self.go_to_audio_popup.bind(func=self.go_to_pos_audio)

    def set_text_l(self):
        if len(self.list) > 0:
            return self.list[0]
        else:
            return ""

    def set_text_r(self):
        if len(self.list) > 1:
            return self.list[1]
        else:
            return ""

    def change_text_r(self):
        if self.cnt + 3 < len(self.list):
            self.left_page.text = self.list[self.cnt + 2]
            self.right_page.text = self.list[self.cnt + 3]
            self.cnt += 2
        else:
            if self.cnt + 2 < len(self.list):
                self.left_page.text = self.list[self.cnt + 2]
                self.right_page.text = ""
                self.cnt += 2

    def change_text_l(self):
        if self.cnt - 2 >= 0:
            self.left_page.text = self.list[self.cnt - 2]
            self.right_page.text = self.list[self.cnt - 1]
            self.cnt -= 2

    def play_or_stop(self):
        if self.music_button.state == 'down':
            self.music_button.text = "Stop"
            if self.audio_file.sound:
                self.audio_file.sound.play()

        else:
            self.music_button.text = "Play"
            if self.audio_file.sound:
                self.audio_file.sound.stop()

    def make_time_str(self, time):
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

    def move_pos_audio(self, value):
        length = self.audio_file.sound.length
        time_r = (value / 100) * length
        time = int(time_r)
        self.audio_file.sound.seek(time_r)
        self.time.text = self.make_time_str(time) + '/' + self.audio_len

    def next_audio(self):
        if self.cur_audio + 1 < self.len_audio_list:
            self.cur_audio += 1
            if self.audio_file.sound.on_play:
                self.audio_file.sound.stop()
            self.audio_file = get_audio(self.cur_audio)
            self.time.text = self.get_audio_len()
            self.slider.value = 0

    def prev_audio(self):
        if self.cur_audio - 1 >= 0:
            self.cur_audio -= 1
            if self.audio_file.sound.on_play:
                self.audio_file.sound.stop()
            self.audio_file = get_audio(self.cur_audio)
            self.time.text = self.get_audio_len()

    def volume_slider_open(self):
        self.vol_popup.open()

    def change_volume(self, instance, value):
        self.audio_file.sound.volume = value / 100

    def ref_press(self, instance, ref):
        self.go_to_audio_popup.cur_ref = ref
        self.go_to_audio_popup.open()

    def get_audio_len(self):
        length = int(self.audio_file.sound.length)
        self.audio_len = self.make_time_str(length)
        return "00:00/" + self.audio_len

    def go_to_book(self):
        print("hello")

    def go_to_pos_audio(self, instance, value):
        self.audio_file.sound.seek(60)

    def my_callback(self, dt):
        self.slider.value = (self.audio_file.sound.get_pos() / self.audio_file.sound.length) * 100
        time = int(self.audio_file.sound.get_pos())
        self.time.text = self.make_time_str(time) + '/' + self.audio_len

    def move_slider(self):
        Clock.schedule_interval(self.my_callback, 1)
        return 0


class SmartReaderApp(App):
    def build(self):
        return Container()


if __name__ == '__main__':
    SmartReaderApp().run()

