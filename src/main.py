from interface.interface import Container
from atb.atb_model import Model
import sys
from kivy.lang.builder import Builder
from kivymd.app import MDApp
import argparse


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('path_atb', nargs='?')
    return parser


Builder.load_file('interface/smartreader.kv')
path_atb = ''


class SmartReaderApp(MDApp):
    def build(self):
        obj = Container()
        if path_atb:
            obj.import_atb(path_atb)
        return obj


if __name__ == '__main__':
    Parser = create_parser()
    namespace = Parser.parse_args()
    if namespace.path_atb:
        path_atb = namespace.path_atb
    SmartReaderApp().run()
