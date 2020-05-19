import os
import threading
import time
from os import listdir
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.core.audio import SoundLoader, Sound
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
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
from kivymd.uix.textfield import MDTextField
from kivymd.uix.spinner import MDSpinner

from atb_model.atb_model import Model
from interface.text_view import TextView
from interface.audio_view import AudioView


class Container(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.atb_model = None
        self.text_view = None
        self.audio_view = None

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

        self.go_to_page_popup = Popup(title="Enter number of page",
                                      content=self.GoToPage(func=self.go_to_page, close=self.close_go_to_page_popup),
                                      size_hint=(0.2, 0.2), separator_color=[0, 0, 0, 1], title_size='0')

        file_menu_items = [{"icon": "git", "text": f"Import book"}, {"icon": "git", "text": f"Open atb"}]
        self.file_menu = MDDropdownMenu(
            caller=self.file_btn,
            items=file_menu_items,
            callback=self.set_item,
            width_mult=4,
        )
        nav_menu_items = [{"icon": "git", "text": f"Go to Page"}, {"icon": "git", "text": f"Go to title"}]
        self.nav_menu = MDDropdownMenu(
            caller=self.nav_btn,
            items=nav_menu_items,
            callback=self.nav_item,
            width_mult=4,
        )

        Clock.schedule_interval(self.file_menu.set_menu_properties, 0.1)
        Clock.schedule_interval(self.nav_menu.set_menu_properties, 0.1)
        Window.bind(on_resize=self.on_resize_window)

        self.msg_dialog = None
        self.cur_volume = 100
        self.night_mode_on = False
        self.event = None
        self.mutex = threading.Lock()
        self.progress = 0
        self.event2 = None

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

        @staticmethod
        def get_color(name, num):
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

    class GoToPage(BoxLayout):
        close = ObjectProperty(None)
        func = ObjectProperty(None)

    def change_text_r(self):
        if self.text_view:
            self.text_view.change_text_r()

    def change_text_l(self):
        if self.text_view:
            self.text_view.change_text_l()

    def play_or_stop(self):
        if self.audio_view:
            self.audio_view.play_or_stop()

    def move_pos_audio(self, value):
        if self.audio_view:
            self.audio_view.move_pos_audio(value)

    def next_audio(self):
        if self.audio_view:
            self.audio_view.next_audio()

    def prev_audio(self):
        if self.audio_view:
            self.audio_view.prev_audio()

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
        if self.audio_view:
            self.audio_view.audio_file.sound.volume = value / 100

    def ref_press(self, instance, ref):
        self.cur_ref = int(ref)
        ind = self.text_view.find_page(self.cur_ref)
        if not self.text_view.clean_word(ind):
            self.go_to_audio_popup.open()

    def go_to_book(self):
        if self.atb_model:
            # self.audio_file.sound.stop()
            word_num = self.atb_model.get_word(self.audio_view.cur_audio, self.audio_view.audio_file.sound.get_pos())
            ind = self.text_view.find_page(word_num)
            self.text_view.clean_word(ind)
            self.text_view.mark_word(ind, word_num)
            if ind % 2 == 0:
                self.left_page.text = self.text_view.pages[ind]
                self.right_page.text = self.text_view.pages[ind + 1]
                self.text_view.cur_page = ind
            else:
                self.left_page.text = self.text_view.pages[ind - 1]
                self.right_page.text = self.text_view.pages[ind]
                self.text_view.cur_page = ind - 1

    def test_go_to_book(self, dt):
        self.go_to_book()

    def go_to_pos_audio(self):
        self.go_to_audio_popup.dismiss()
        pos = self.atb_model.get_sec(self.cur_ref)
        self.audio_view.audio_file = self.audio_view.Music(self.audio_view.play_list[pos[0]])
        self.audio_view.audio_file.sound.seek(pos[1])
        self.time_label.text = self.audio_view.get_audio_len()

    def import_book(self):
        self.file_popup = Popup(title="Select .fb2 file", content=self.ChooseFile(select=self.select_fb2_mp3,
                                                                                  cancel=self.dismiss_popup, ),
                                size_hint=(0.5, 0.6), background='../images/back.jpg', title_color=[0, 0, 0, 1],
                                title_align='center', separator_color=[1, 1, 1, 1])
        self.file_popup.content.select_button.text = 'Select .fb2 file'
        self.file_popup.open()
        self.file_menu.dismiss()

    def open_atb_file(self):
        self.file_popup = Popup(title="Select .atb file", content=self.ChooseFile(select=self.select_atb,
                                                                                  cancel=self.dismiss_popup, ),
                                size_hint=(0.5, 0.6), background='../images/back.jpg', title_color=[0, 0, 0, 1],
                                title_align='center', separator_color=[1, 1, 1, 1])
        self.file_popup.content.select_button.text = 'Select .atb file'
        self.file_popup.open()
        self.file_menu.dismiss()

    def select_atb(self, path, selection):
        if selection and selection[0].endswith('.atb'):
            self.dismiss_popup()
            self.loading_label.size_hint = [0.07, 1]
            self.loading_label.text = "Loading..."
            self.spinner.color = [0, 0, 0, 1]
            self.spinner.active = True
            x = threading.Thread(target=self.import_atb, args=(selection[0],))
            x.start()
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
                    x = threading.Thread(target=self.make_atb, args=(self.file_popup.content.fb2_path, mp3s))
                    x.start()
                    self.loading_label.size_hint = [0.07, 1]
                    self.spinner.color = [0, 0, 0, 1]
                    self.spinner.active = True
                    self.event2 = Clock.schedule_interval(self.update_bar, 0.1)

            else:
                self.show_msg('This is not a folder')

    def update_bar(self, dt):
        self.mutex.acquire()
        self.loading_label.text = 'Sync: ' + str(self.progress) + '%'
        self.mutex.release()

    def make_atb(self, fb2_path, mp3_list):
        for i in range(100):
            self.progress += 1
            time.sleep(0.2)
        self.event2.cancel()
        self.loading_label.size_hint = [0.1, 1]
        self.spinner.active = False
        self.loading_label.text = 'Done!'

    def on_resize_window(self, window, width, height):
        if self.text_view:
            if self.event:
                self.event.cancel()
            self.event = Clock.schedule_once(self.text_view.change_text, 0.3)

    def import_atb(self, path):
        self.atb_model = Model()
        self.atb_model.load(path)
        self.atb_model.load_map()

        self.text_view = TextView(self.atb_model.get_text(), self.left_page, self.right_page)
        self.audio_view = AudioView(self.atb_model.get_audio_list(), self.music_button, self.time_label,
                                    self.cur_volume, self.slider)

        self.move_slider()
        self.cur_ref = 0
        self.loading_label.size_hint = [0.1, 1]
        self.loading_label.text = "Done!"
        self.spinner.active = False

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

    def move_slider(self):
        Clock.schedule_interval(self.audio_view.timer_callback, 1)
        return 0

    def dismiss_popup(self):
        self.file_popup.dismiss()

    def show_msg(self, msg):
        self.msg_dialog = MDDialog(
            title=msg,
            size_hint=[0.3, 0.5],
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=self.close_dialog
                ),
            ],
        )
        self.msg_dialog.open()

    def close_dialog(self, instance):
        self.msg_dialog.dismiss()

    def close_loading_bar(self):
        self.loading_popup.dismiss()

    def run_test_go_to_book(self):
        Clock.schedule_interval(self.test_go_to_book, 0.5)

    @staticmethod
    def get_color(name, num):
        return get_color_from_hex(colors[name][num])

    def set_item(self, instance):
        if instance.text == 'Open atb':
            self.open_atb_file()
        else:
            self.import_book()

    def nav_item(self, instance):
        if instance.text == 'Go to str':
            self.go_to_page_popup.open()
        else:
            print('bbb')

    def go_to_page(self, page):
        cur = page - (page % 2)
        self.text_view.cur_page = cur
        self.left_page.text = self.text_view.pages[self.text_view.cur_page]
        self.right_page.text = self.text_view.pages[self.text_view.cur_page + 1]

    def close_go_to_page_popup(self):
        self.go_to_page_popup.dismiss()
