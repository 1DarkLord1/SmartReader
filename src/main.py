from interface.interface import Container
from atb_model.atb_model import Model
import sys
from kivy.lang.builder import Builder
from kivymd.app import MDApp




Builder.load_file('interface/smartreader.kv')
path_atb = ''
test = False


class SmartReaderApp(MDApp):
    def build(self):
        obj = Container()
        if path_atb:
            obj.import_atb(path_atb)
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
