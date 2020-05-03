import os
from os import listdir
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.core.audio import SoundLoader, Sound
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivymd.app import MDApp

from atb.atb_model import Model
from kivy.app import App
from kivymd.toast import toast
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton, MDRectangleFlatIconButton, MDIconButton, \
    MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.slider import MDSlider
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from kivymd.uix.filemanager import MDFileManager


class Container(BoxLayout):
    class Music(Sound):
        def __init__(self, file, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.sound = SoundLoader.load(file)

    class VolumePopup(Popup):
        pass

    class ChooseFile(FloatLayout):
        select = ObjectProperty(None)
        cancel = ObjectProperty(None)
        fb2_is_load = ObjectProperty(False)
        mp3_is_load = ObjectProperty(False)
        fb2_path = ObjectProperty(None)

        @staticmethod
        def get_path():
            return os.path.abspath(os.curdir)

        def get_color(self, name, num):
            return get_color_from_hex(colors[name][num])

    class FileDialog(BoxLayout):
        import_book = ObjectProperty(None)
        open_atb = ObjectProperty(None)

    class MessagePopup(BoxLayout):
        close = ObjectProperty(None)

    class LoadingBar(BoxLayout):
        close = ObjectProperty(None)
        func = ObjectProperty(None)

    class GoToAudio(FloatLayout):
        func = ObjectProperty(None)
        color = ObjectProperty(None)

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flag = True
        self.is_load = False
        self.atb_model = None
        self.last_words = None
        self.pages = None
        self.cur_page = None
        self.play_list = None
        self.audio_file = None
        self.cur_audio = None
        self.audio_len = None
        self.cur_ref = None
        self.vol_popup = self.VolumePopup()
        self.vol_popup.bind(volume=self.change_volume)
        self.vol_popup.separator_color = [0, 0, 0, 1]
        self.vol_popup.background = '../images/back.jpg'
        self.vol_popup.title_color = [0, 0, 0, 1]
        self.go_to_audio_popup = Popup(title="",
                                       content=self.GoToAudio(func=self.go_to_pos_audio, color=self.get_color),
                                       size_hint=(0.15, 0.15), separator_color=[0, 0, 0, 1], title_size='0')
        self.file_popup = None

        self.msg_popup = None
        self.loading_popup = Popup(title="Loading", content=self.LoadingBar(close=self.close_loading_bar,
                                                                            func=self.make_atb),
                                   size_hint=(0.4, 0.15))
        self.move_slider()
        self.update_bar_trigger = Clock.create_trigger(self.update_bar)
        menu_items = [{"icon": "git", "text": f"Import book"}, {"icon": "git", "text": f"Open atb"}]
        self.menu = MDDropdownMenu(
            caller=self.file_btn,
            items=menu_items,
            position="auto",
            callback=self.set_item,
            width_mult=4,
        )
        Clock.schedule_interval(self.menu.set_menu_properties, 0.1)
        self.dialog = None
        self.cur_volume = 100
        self.night_mode_on = False

    def set_item(self, instance):
        if instance.text == 'Open atb':
            self.open_atb_file()
        else:
            self.import_book()

    def change_text_r(self):
        if self.is_load:
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
        if self.is_load:
            if self.cur_page - 2 >= 0:
                self.left_page.text = self.pages[self.cur_page - 2]
                self.right_page.text = self.pages[self.cur_page - 1]
                self.cur_page -= 2

    def play_or_stop(self):
        if self.is_load:
            if self.flag:
                if self.audio_file.sound:
                    self.audio_file.sound.play()
                    self.music_button.icon = 'pause-circle-outline'
                    self.flag = False
            else:
                if self.audio_file.sound:
                    self.audio_file.sound.stop()
                    self.music_button.icon = 'play-circle-outline'
                    self.flag = True

    def move_pos_audio(self, value):
        if self.is_load:
            length = self.audio_file.sound.length
            time_r = (value / 100) * length
            time = int(time_r)
            self.audio_file.sound.seek(time_r)
            self.time.text = self.make_time_str(time) + '/' + self.audio_len

    def next_audio(self):
        if self.is_load:
            if self.cur_audio + 1 < len(self.play_list):
                self.cur_audio += 1
                if self.audio_file.sound.on_play:
                    self.audio_file.sound.stop()
                self.audio_file = self.Music(self.play_list[self.cur_audio])
                self.time.text = self.get_audio_len()
                self.slider.value = 0

    def prev_audio(self):
        if self.is_load:
            if self.cur_audio - 1 >= 0:
                self.cur_audio -= 1
                if self.audio_file.sound.on_play:
                    self.audio_file.sound.stop()
                self.audio_file = self.Music(self.play_list[self.cur_audio])
                self.time.text = self.get_audio_len()

    def volume_slider_open(self):
        self.vol_popup.open()

    def change_volume(self, instance, value):
        self.cur_volume = value
        if value == 0:
            self.volume_btn.icon = 'volume-mute'
        if 0 < value < 33:
            self.volume_btn.icon = 'volume-low'
        if 33 <= value < 66:
            self.volume_btn.icon = 'volume-medium'
        if 66 <= value <= 100:
            self.volume_btn.icon = 'volume-high'
        if self.is_load:
            self.audio_file.sound.volume = value / 100

    def ref_press(self, instance, ref):
        print(ref)
        self.cur_ref = int(ref)
        ind = self.find_page(self.cur_ref)
        if not self.clean_word(ind):
            self.go_to_audio_popup.open()

    def go_to_book(self):
        if self.is_load:
            self.audio_file.sound.stop()
            word_num = self.atb_model.get_word_num([self.cur_audio, self.audio_file.sound.get_pos])
            ind = self.find_page(word_num)
            self.mark_word(ind, word_num)
            if ind % 2 == 0:
                self.left_page.text = self.pages[ind]
                self.right_page.text = self.pages[ind + 1]
                self.cur_page = ind
            else:
                self.left_page.text = self.pages[ind - 1]
                self.right_page.text = self.pages[ind]
                self.cur_page = ind - 1

    def go_to_pos_audio(self):
        self.go_to_audio_popup.dismiss()
        pos = self.atb_model.get_sec(self.cur_ref)
        self.audio_file = self.Music(self.play_list[pos[0]])
        self.audio_file.sound.seek(pos[1])
        self.time.text = self.get_audio_len()

    def import_book(self):
        self.file_popup = Popup(title="Select .fb2 file", content=self.ChooseFile(select=self.select_fb2_mp3,
                                                                                  cancel=self.dismiss_popup, ),
                                size_hint=(0.5, 0.6), background='../images/back.jpg', title_color=[0, 0, 0, 1],
                                title_align='center')
        self.file_popup.content.select_button.text = 'Select .fb2 file'
        self.file_popup.open()
        self.menu.dismiss()

    def open_atb_file(self):
        self.file_popup = Popup(title="Select .atb file", content=self.ChooseFile(select=self.select_atb,
                                                                                  cancel=self.dismiss_popup, ),
                                size_hint=(0.5, 0.6), background='../images/back.jpg', title_color=[0, 0, 0, 1],
                                title_align='center')
        self.file_popup.content.select_button.text = 'Select .atb file'
        self.file_popup.open()
        self.menu.dismiss()

    def select_atb(self, path, selection):
        if selection and selection[0].endswith('.atb'):
            self.dismiss_popup()
            self.import_atb(selection[0])
        else:
            self.show_msg('This is not .atb file')

    def select_fb2_mp3(self, path, selection):
        if not self.file_popup.content.fb2_is_load:
            if selection and selection[0].endswith('.fb2'):
                self.file_popup.content.fb2_path = selection[0]
                self.file_popup.title = 'Select folder with mp3 files'
                self.file_popup.content.select_button.text = 'Select folder'
                self.file_popup.content.fb2_is_load = True
                self.file_popup.content.filechooser.selection = []
            else:
                self.show_msg('This is not .fb2 file')

        else:
            if not selection:
                mp3s = []
                for fil in listdir(path):
                    if fil.endswith('.mp3'):
                        mp3s.append(fil)
                if not mp3s:
                    self.show_msg('No mp3 files')
                else:
                    mp3s.sort()
                    for i in range(len(mp3s)):
                        mp3s[i] = path + '/' + mp3s[i]
                    self.dismiss_popup()
                    self.loading_popup.open()
                    self.make_atb(self.file_popup.content.fb2_path, mp3s)
            else:
                self.show_msg('This is not a folder')

    def update_bar(self, dt):
        if self.i <= 100:
            self.loading_popup.content.pb.value = self.i
            self.i += 1
            self.update_bar_trigger()
        else:
            self.loading_popup.dismiss()

    def make_atb(self, fb2_path, mp3_list):
        self.i = 0
        self.update_bar_trigger()

    def import_atb(self, path):
        self.is_load = True
        self.atb_model = Model()
        self.atb_model.load(path)
        self.last_words = []
        self.pages = self.slice_pages(self.atb_model.get_text(), 100, 46)
        self.cur_page = 0
        if len(self.pages) > 0:
            self.left_page.text = self.pages[0]
        if len(self.pages) > 1:
            self.right_page.text = self.pages[1]
        self.play_list = self.atb_model.get_audio_list()
        self.audio_file = self.Music(self.play_list[0])
        self.audio_file.sound.volume = self.cur_volume / 100
        self.cur_audio = 0
        self.audio_len = ""
        self.time.text = self.get_audio_len()
        self.cur_ref = 0

    def night_mode(self):
        if not self.night_mode_on:
            self.left_page.background_color = self.get_color('Gray', '800')
            self.left_page.color = [1, 1, 1, 1]
            self.right_page.background_color = self.get_color('Gray', '800')
            self.right_page.color = [1, 1, 1, 1]
            self.night_mode_on = True
        else:
            self.left_page.background_color = [1, 1, 1, 1]
            self.left_page.color = [0, 0, 0, 1]
            self.right_page.background_color = [1, 1, 1, 1]
            self.right_page.color = [0, 0, 0, 1]
            self.night_mode_on = False



    def clean_word(self, ind):
        if self.pages[ind].find('[/color]') != -1:
            self.pages[ind] = self.pages[ind].replace('[/color][/b]', '')
            self.pages[ind] = self.pages[ind].replace('[b][color=ff0000]', '')
            if ind % 2 == 0:
                self.left_page.text = self.pages[ind]
            else:
                self.right_page.text = self.pages[ind]
            return True
        return False

    def get_audio_len(self):
        length = int(self.audio_file.sound.length)
        self.audio_len = self.make_time_str(length)
        return "00:00/" + self.audio_len

    def find_page(self, word_num):
        ind = 0
        while self.last_words[ind] < word_num:
            ind += 1
        return ind

    def mark_word(self, ind, word_num):
        pos = self.pages[ind].find('[ref={}]'.format(word_num))
        tmp_str = self.pages[ind][pos:].replace('[/ref]', '[/color][/b][/ref]', 1)
        page = self.pages[ind][0:pos] + tmp_str
        self.pages[ind] = page.replace('[ref={}]'.format(word_num), '[ref={}][b][color=ff0000]'.format(word_num))

    def timer_callback(self, dt):
        if self.is_load:
            self.slider.value = (self.audio_file.sound.get_pos() / self.audio_file.sound.length) * 100
            time = int(self.audio_file.sound.get_pos())
            self.time.text = self.make_time_str(time) + '/' + self.audio_len

    def move_slider(self):
        Clock.schedule_interval(self.timer_callback, 1)
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
                    slicer.page += "[ref={}]{}[/ref]".format(str(cnt), word)
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

    def dismiss_popup(self):
        self.file_popup.dismiss()

    def show_msg(self, msg):
        self.dialog = MDDialog(
            title=msg,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=self.close_dialog
                ),
            ],
        )
        self.dialog.open()

    def close_dialog(self, instance):
        self.dialog.dismiss()

    def close_loading_bar(self):
        self.loading_popup.dismiss()

    @staticmethod
    def get_color(name, num):
        return get_color_from_hex(colors[name][num])



