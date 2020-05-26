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
from kivymd import app
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
    def __init__(self, change_theme, **kwargs):
        super().__init__(**kwargs)
        self.flag = True

        self.atb_model = None
        self.text_view = None
        self.audio_view = None

        self.change_theme = change_theme
        self.theme = 'Green'
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

        file_menu_items = [{"icon": "git", "text": f"Import book"}, {"icon": "git", "text": f"Open atb file"}]
        self.file_menu = MDDropdownMenu(
            caller=self.file_btn,
            items=file_menu_items,
            callback=self.set_item,
            width_mult=4,
        )
        nav_menu_items = [{"icon": "git", "text": f"Go to begin"}, {"icon": "git", "text": f"Go to end"},
                          {"icon": "git", "text": f"Go to Page"}]
        self.nav_menu = MDDropdownMenu(
            caller=self.nav_btn,
            items=nav_menu_items,
            callback=self.nav_item,
            width_mult=4,
        )
        font_menu_items = [{"icon": "git", "text": f"Font"}, {"icon": "git", "text": f"Font size"}]
        self.font_menu = MDDropdownMenu(
            caller=self.font_btn,
            items=font_menu_items,
            callback=self.font_item,
            width_mult=4,
        )
        font_size_menu_items = [{"icon": "git", "text": f"Small"}, {"icon": "git", "text": f"Medium"},
                                {"icon": "git", "text": f"High"}]
        self.font_size_menu = MDDropdownMenu(
            caller=self.font_btn,
            items=font_size_menu_items,
            callback=self.font_size_item,
            width_mult=4,
        )

        font_change_menu_items = [{"icon": "git", "text": f"Roboto"}, {"icon": "git", "text": f"DejaVuSans"}]
        self.font_change_menu = MDDropdownMenu(
            caller=self.font_btn,
            items=font_change_menu_items,
            callback=self.font_change_item,
            width_mult=4,
        )

        view_menu_items = [{"icon": "git", "text": f"Theme color"}]
        self.view_menu = MDDropdownMenu(
            caller=self.view_btn,
            items=view_menu_items,
            callback=self.view_item,
            width_mult=4,
        )

        theme_menu_items = [{"icon": "git", "text": f"Green"}, {"icon": "git", "text": f"Blue"},
                            {"icon": "git", "text": f"Dark"}]
        self.theme_menu = MDDropdownMenu(
            caller=self.view_btn,
            items=theme_menu_items,
            callback=self.theme_item,
            width_mult=4,
        )

        lang_menu_items = [{"icon": "git", "text": f"English"}, {"icon": "git", "text": f"Русский"}]
        self.lang_menu = MDDropdownMenu(
            caller=self.view_btn,
            items=lang_menu_items,
            callback=self.lang_item,
            width_mult=4,
        )

        self.go_to_page_dialog = MDDialog(
            title="Enter the number of page",
            type="custom",
            content_cls=self.GoToPage(),
            size_hint=[0.3, 0.5],
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.dismiss_page_dialog
                ),
                MDRaisedButton(
                    text="OK",
                    on_release=self.go_to_page
                ),
            ],
        )

        Clock.schedule_interval(self.file_menu.set_menu_properties, 0.1)
        Clock.schedule_interval(self.nav_menu.set_menu_properties, 0.1)
        Clock.schedule_interval(self.font_menu.set_menu_properties, 0.1)
        Clock.schedule_interval(self.font_size_menu.set_menu_properties, 0.1)
        Clock.schedule_interval(self.font_change_menu.set_menu_properties, 0.1)
        Clock.schedule_interval(self.view_menu.set_menu_properties, 0.1)
        Clock.schedule_interval(self.theme_menu.set_menu_properties, 0.1)

        Window.bind(on_resize=self.on_resize_window)

        self.msg_dialog = None
        self.cur_volume = 100
        self.night_mode_on = False
        self.event = None
        self.mutex = threading.Lock()
        self.progress = 0
        self.event2 = None
        self.cs = [0.117, 0.053, 0.09, 0.042, 0.077, 0.035]
        self.font_size = 0

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
        theme = ObjectProperty(None)

        @staticmethod
        def get_path():
            return os.path.abspath(os.curdir)

        def get_color(self, flag):
            if flag:
                hue = "600"
            else:
                hue = "800"
            if self.theme == 'Blue':
                return get_color_from_hex(colors["Blue"][hue])
            if self.theme == 'Green':
                return get_color_from_hex(colors["Green"][hue])
            if self.theme == 'Dark':
                return get_color_from_hex(colors["Gray"][hue])

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
        pass

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
        print(ref, self.atb_model.word_list[self.cur_ref])

        ind = self.text_view.find_page(self.cur_ref)
        if not self.text_view.clean_word(ind):
            self.go_to_audio_popup.open()

    def go_to_book(self):
        if self.atb_model:
            # self.audio_file.sound.stop()
            word_num = self.atb_model.get_word(self.audio_view.cur_audio,
                                               self.audio_view.audio_file.sound.get_pos())
            if not word_num:
                return
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
        if not pos:
            return

        if pos[0] != self.audio_view.cur_audio:
            self.audio_view.audio_file.sound.unload()
            self.audio_view.cur_audio = pos[0]
            self.audio_view.audio_file = self.Music(self.audio_view.play_list[pos[0]])
        self.audio_view.audio_file.sound.seek(pos[1])
        self.time_label.text = self.audio_view.get_audio_len()

    def import_book(self):
        self.file_popup = Popup(title="Select .fb2 file", content=self.ChooseFile(select=self.select_fb2_mp3,
                                                                                  cancel=self.dismiss_popup,
                                                                                  theme=self.theme),
                                size_hint=(0.5, 0.6), background='../images/back.jpg', title_color=[0, 0, 0, 1],
                                title_align='center', separator_color=[1, 1, 1, 1])
        self.file_popup.content.select_button.text = 'Select .fb2 file'
        self.file_popup.open()
        self.file_menu.dismiss()

    def open_atb_file(self):
        self.file_popup = Popup(title="Select .atb file", content=self.ChooseFile(select=self.select_atb,
                                                                                  cancel=self.dismiss_popup,
                                                                                  theme=self.theme),
                                size_hint=(0.5, 0.6), background='../images/back.jpg', title_color=[0, 0, 0, 1],
                                title_align='center', separator_color=[1, 1, 1, 1])
        self.file_popup.content.select_button.text = 'Select .atb file'
        self.file_popup.open()
        self.file_menu.dismiss()

    def select_atb(self, path, selection):
        if selection and selection[0].endswith('.atb'):
            self.dismiss_popup()
            self.loading_label.size_hint = [0.07, 1]
            self.spinner.color = [0, 0, 0, 1]
            self.spinner.active = True
            x = threading.Thread(target=self.import_atb, args=(selection[0], True))
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

                    book_path = self.file_popup.content.fb2_path
                    obj = Model()
                    obj.import_book(book_path, mp3s)
                    book_name = book_path.split('/')[-1].replace('.fb2', '')

                    x = threading.Thread(target=self.load_book,
                                         args=('../books/' + book_name + '/' + book_name + '_data' + '.atb',))
                    x.start()

            else:
                self.show_msg('This is not a folder')

    def load_book(self, path):
        self.import_atb(path, False)
        self.make_mapping()

    def update_bar(self, dt):
        self.mutex.acquire()
        self.loading_label.text = 'Sync: ' + str(self.atb_model.get_len_word_sec()) + '%'
        self.mutex.release()

    def make_mapping(self):
        self.event2 = Clock.schedule_interval(self.update_bar, 0.1)

        self.atb_model.make_mapping()

        self.event2.cancel()
        self.loading_label.size_hint = [0.1, 1]
        self.spinner.active = False
        self.loading_label.text = 'Done!'

    def on_resize_window(self, window, width, height):
        if self.text_view:
            if self.event:
                self.event.cancel()
            self.event = Clock.schedule_once(self.text_view.change_text, 0.3)

    def import_atb(self, path, flag):
        self.loading_label.text = "Loading..."
        self.loading_label.size_hint = [0.07, 1]
        self.spinner.color = [0, 0, 0, 1]
        self.spinner.active = True

        self.atb_model = Model()
        self.atb_model.load(path)
        if flag:
            self.atb_model.load_map()

        self.text_view = TextView(self.atb_model.get_text(), self.left_page, self.right_page)
        self.audio_view = AudioView(self.atb_model.get_audio_list(), self.music_button, self.time_label,
                                    self.cur_volume, self.slider)

        self.move_slider()
        self.cur_ref = 0
        

        if flag:
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
        if instance.text == 'Open atb file':
            self.open_atb_file()
        else:
            self.import_book()

    def nav_item(self, instance):
        if self.text_view:
            if instance.text == 'Go to begin':
                self.text_view.cur_page = 0
                if len(self.text_view.pages) > 0:
                    self.left_page.text = self.text_view.pages[0]
                if len(self.text_view.pages) > 1:
                    self.right_page.text = self.text_view.pages[1]
            if instance.text == 'Go to end':
                if len(self.text_view.pages) % 2 == 0:
                    self.text_view.cur_page = len(self.text_view.pages) - 2
                    self.left_page.text = self.text_view.pages[len(self.text_view.pages) - 2]
                    self.right_page.text = self.text_view.pages[len(self.text_view.pages) - 1]
                else:
                    self.text_view.cur_page = len(self.text_view.pages) - 1
                    self.left_page.text = self.text_view.pages[len(self.text_view.pages) - 1]
                    self.right_page.text = ''
            if instance.text == 'Go to Page':
                self.nav_menu.dismiss()
                self.go_to_page_dialog.content_cls.field.text = str(self.text_view.cur_page + 1)
                self.go_to_page_dialog.content_cls.label.text = 'of ' + str(len(self.text_view.pages))
                self.go_to_page_dialog.open()

    def font_item(self, instance):
        if instance.text == 'Font':
            self.font_menu.dismiss()
            self.font_change_menu.open()
        else:
            self.font_menu.dismiss()
            self.font_size_menu.open()

    def font_size_item(self, instance):
        if instance.text == 'Small':
            self.left_page.font_size = '16sp'
            self.right_page.font_size = '16sp'
            self.change_text(self.cs[0], self.cs[1])
            self.font_size = 0
        if instance.text == 'Medium':
            self.left_page.font_size = '20sp'
            self.right_page.font_size = '20sp'
            self.change_text(self.cs[2], self.cs[3])
            self.font_size = 1
        if instance.text == 'High':
            self.left_page.font_size = '24sp'
            self.right_page.font_size = '24sp'
            self.change_text(self.cs[4], self.cs[5])
            self.font_size = 2

    def font_change_item(self, instance):
        if instance.text == 'Roboto':
            self.left_page.font_name = 'fonts/Roboto-Regular'
            self.right_page.font_name = 'fonts/Roboto-Regular'
            self.cs = [0.117, 0.053, 0.09, 0.042, 0.077, 0.035]
            self.change_text(self.cs[self.font_size * 2], self.cs[self.font_size * 2 + 1])
        else:
            self.left_page.font_name = 'fonts/DejaVuSans'
            self.right_page.font_name = 'fonts/DejaVuSans'
            self.cs = [0.105, 0.053, 0.085, 0.041, 0.07, 0.035]
            self.change_text(self.cs[self.font_size * 2], self.cs[self.font_size * 2 + 1])

    def change_text(self, c1, c2):
        if self.text_view:
            self.text_view.const1 = c1
            self.text_view.const2 = c2
            self.text_view.change_text(0)

    def view_item(self, instance):
        if instance.text == 'Theme color':
            self.view_menu.dismiss()
            self.theme_menu.open()
        else:
            self.view_menu.dismiss()
            self.lang_menu.open()

    def theme_item(self, instance):
        if instance.text == 'Green':
            self.change_theme('LightGreen', '300')
            self.theme = 'Green'
            self.up_bar.md_bg_color = self.get_color('LightGreen', '300')
            self.play_layout.md_bg_color = self.get_color('LightGreen', '300')
            self.slider.thumb_color_down = [0, 0, 0, 1]
            self.vol_popup.slider_id.thumb_color_down = [0, 0, 0, 1]
        if instance.text == 'Blue':
            self.change_theme('LightBlue', '300')
            self.theme = 'Blue'
            self.up_bar.md_bg_color = self.get_color('LightBlue', '300')
            self.play_layout.md_bg_color = self.get_color('LightBlue', '300')
            self.slider.thumb_color_down = [0, 0, 0, 1]
            self.vol_popup.slider_id.thumb_color_down = [0, 0, 0, 1]
        if instance.text == 'Dark':
            self.change_theme('Gray', '500')
            self.theme = 'Dark'
            self.up_bar.md_bg_color = self.get_color('Gray', '500')
            self.play_layout.md_bg_color = self.get_color('Gray', '500')
            self.slider.thumb_color_down = [0, 0, 0, 1]
            self.vol_popup.slider_id.thumb_color_down = [0, 0, 0, 1]

    def lang_item(self, instance):
        pass

    def go_to_page(self, instance):
        page = int(self.go_to_page_dialog.content_cls.field.text) - 1
        if page >= len(self.text_view.pages):
            return

        self.text_view.cur_page = page - (page % 2)
        self.left_page.text = self.text_view.pages[self.text_view.cur_page]
        if self.text_view.cur_page + 1 < len(self.text_view.pages):
            self.right_page.text = self.text_view.pages[self.text_view.cur_page + 1]
        else:
            self.right_page.text = ''

    def dismiss_page_dialog(self, instance):
        self.go_to_page_dialog.dismiss()

    def close_go_to_page_popup(self):
        self.go_to_page_popup.dismiss()
