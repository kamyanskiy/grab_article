from re import sub
import textwrap
import unicodedata


class ParseHelper(object):
    @staticmethod
    def normalize_string(string):
        return unicodedata.normalize('NFKD', string)

    @staticmethod
    def format_text_for_a_element(aitem):
        return "[{0}] {1}".format(aitem["href"], aitem.get_text())

    @staticmethod
    def replace_tabular_codes(text):
        return sub('[ \t\r\n]+', ' ', text)

    @staticmethod
    def format_text_line(item):
        result = []
        if item.find_all("a"):
            for line in item.children:
                text = line
                if line.name == "a":
                    text = ParseHelper.format_text_for_a_element(line)
                result.append(text)
        else:
            return item.get_text()
        return "".join(result)

    @staticmethod
    def format_text(article_list):
        text = ''
        for line in article_list:
            if len(line) <= 80:
                text += line
            else:
                text += textwrap.fill(line, 80)
            text += "\n\n"
        return text
