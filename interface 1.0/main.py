import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.slider import Slider
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.scrollview import ScrollView


# Window.size = (1920, 1080)

class ScrollableLabel(ScrollView):
    text = StringProperty('')


def slice_pages(len_of_str, num_of_str):
    handle = open("test.txt", "r")
    data = handle.read()
    handle.close()
    pages = []
    beg = 0
    end = 0
    while end < len(data):
        num = 0
        while num < num_of_str:
            ln = 0
            while ln < len_of_str and end < len(data):
                if data[end] == '\n':
                    end += 1
                    break
                else:
                    ln += 1
                    end += 1
            num += 1
        pages.append(data[beg:end])
        beg = end
    return pages


class Container(BoxLayout):
    list = ObjectProperty(slice_pages(100, 50))
    cnt = ObjectProperty(0)

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


class SmartReaderApp(App):
    def build(self):
        return Container()


if __name__ == '__main__':
    SmartReaderApp().run()
