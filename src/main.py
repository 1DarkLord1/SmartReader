from interface.interface import Container
from atb_model.atb_model import Model
import sys

from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivymd.app import MDApp




Builder.load_file('interface/smartreader.kv')
path_atb = ''
test = False


class SmartReaderApp(MDApp):
    def change_theme(self, palette, hue):
        self.theme_cls.primary_palette = palette
        self.theme_cls.primary_hue = hue

    def build(self):
        self.theme_cls.primary_palette = "LightGreen"  # "Purple", "Red"
        self.theme_cls.primary_hue = "300"
        obj = Container(self.change_theme)
        if path_atb:
            obj.import_atb(path_atb, True)
        if test:
            obj.run_test_go_to_book()
        return obj


if __name__ == '__main__':
    if len(sys.argv) <= 3:
        if 2 <= len(sys.argv) <= 3:
            path_atb = sys.argv[1]
            if len(sys.argv) == 3:
                test = True
        SmartReaderApp().run()
    else:
        print("Wrong number of args")
