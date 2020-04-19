from lxml import etree
import re

class model:
    def __init__(self):
        self.tree = None
        self.root = None
        self.text = None
        self.word_list = None


    def __get_fb2_root(self, fb2_path):
        fb2_tree = etree.parse(fb2_path)
        fb2_root = tree.getroot()
        for elem in fb2_root.getiterator():
            elem.tag = etree.QName(elem).localname
        etree.cleanup_namespaces(root)
        return fb_root


    def __fb2_text_parse(self, fb2_path):
        fb2_root = self.__get_fb2_root()
        text = etree.tounicode(fb2_root.find('body'))
        repl_cltag = '#~?$'
        text = re.sub('<.*?>', '', re.sub('</.*?>', repl_cltag, text)).replace(repl_cltag, '\n')
        return text


    def __load_text(self):
        book_path = self.root.find('fb2')
        self.text =  __fb2_text_parse(self, book_path)

    def __make_word_list(self):
        self.word_list = [filter(lambda ch: ch.isalpha() or ch == '-', word) for word in re.split(' |\.|,|:|\n', self.text)]
        self.word_list = filter(lambda word: word != "", self.word_list)


    def load(self, path):
        parser = etree.XMLParser(remove_blank_text=True)
        self.tree = etree.parse(path, parser)
        self.root = tree.getroot()
        self.__load_text()
        self.__make_word_list()


    def save(self, path):
        self.tree.write(path, pretty_print=True)


    def get_audio_list(self):
        audio = root.find('audio')
        return [file.text for file in root.findall('file')]

    def get_text(self):
        return self.text
