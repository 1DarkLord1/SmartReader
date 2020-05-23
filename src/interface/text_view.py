from kivy.core.window import Window


class TextView:
    def __init__(self, text, l_page, r_page):
        self.left_page = l_page
        self.right_page = r_page

        self.text = text
        self.last_words = None
        self.const1 = 0.117
        self.const2 = 0.053
        self.pages = self.slice_pages(text)
        self.cur_page = 0

        if len(self.pages) > 0:
            self.left_page.text = self.pages[0]
        if len(self.pages) > 1:
            self.right_page.text = self.pages[1]

    class Slicer:
        def __init__(self, p1, p2):
            self.str_len = 0
            self.cnt_str = 0
            self.page = ""
            self.pages = []
            self.last_words = []
            self.words_in_str = p1
            self.num_of_str = p2

        def find_pos(self, space_pos, enter_pos):
            if space_pos == -1 and enter_pos == -1:
                return -1
            if space_pos == -1:
                return enter_pos
            if enter_pos == -1:
                return space_pos
            return min(space_pos, enter_pos)

        def add_str_to_list(self, text, i, cnt):
            self.str_len += 1

            if text[i] == ' ':
                space_pos = text[i + 1:i + 30].find(' ')
                enter_pos = text[i + 1:i + 30].find('\n')
                pos = self.find_pos(space_pos, enter_pos)
            else:
                pos = 0

            if (text[i] == ' ' and pos + self.str_len >= self.words_in_str) or text[i] == '\n':
                self.cnt_str += 1
                self.str_len = 0
                if text[i] != '\n':
                    self.page += '\n'
            if self.cnt_str >= self.num_of_str:
                self.cnt_str = 0
                self.pages.append(self.page)
                self.last_words.append(cnt - 1)
                self.page = ""

    def slice_pages(self, data):
        cnt = 0
        beg = 0
        end = 0
        words_in_str = int((Window.width * 0.995 * 0.5 - 20) * self.const1)
        num_str = int((Window.height * 0.88 - 20) * self.const2)
        slicer = self.Slicer(words_in_str, num_str)
        while end < len(data):
            s = data[end]
            text = data
            index = end

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
            slicer.add_str_to_list(text, index, cnt)
        slicer.pages.append(slicer.page)
        self.last_words = slicer.last_words
        return slicer.pages

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

    def change_text_r(self):
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
        if self.cur_page - 2 >= 0:
            self.left_page.text = self.pages[self.cur_page - 2]
            self.right_page.text = self.pages[self.cur_page - 1]
            self.cur_page -= 2

    def change_text(self, dt):
        if self.cur_page == 0:
            num_of_first_word = 0
        else:
            num_of_first_word = self.last_words[self.cur_page - 1] + 1
        self.pages = self.slice_pages(self.text)
        self.cur_page = self.find_page(num_of_first_word)
        self.cur_page -= self.cur_page % 2
        self.left_page.text = self.pages[self.cur_page]
        self.right_page.text = self.pages[self.cur_page + 1]

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
