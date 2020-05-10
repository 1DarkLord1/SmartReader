from interface.interface import Container
from atb_model.atb_model import Model
import sys
from kivy.lang.builder import Builder
from kivymd.app import MDApp
import argparse


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('path_atb')
    parser.add_argument('test')
    return parser


Builder.load_file('interface/smartreader.kv')
path_atb = ''
test=''


class SmartReaderApp(MDApp):
    def build(self):
        obj = Container()
        if path_atb:
            obj.import_atb(path_atb)
        if test == 'test':
            obj.run_test_go_to_book()
        return obj


if __name__ == '__main__':
    Parser = create_parser()
    namespace = Parser.parse_args()
    path_atb = namespace.path_atb
    test = namespace.test
    SmartReaderApp().run()
