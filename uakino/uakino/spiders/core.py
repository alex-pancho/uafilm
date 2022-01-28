import scrapy
import re
from xml.etree.ElementTree import fromstring
from xml.etree.ElementTree import ParseError

class CoreSpider(scrapy.Spider):

    @classmethod
    def tag_cleaner(cls, out):
        if out is None:
            return out
        out = out.replace("]", "").replace("[", " ").replace("\t", " ").replace("  ", " ")
        out = out.replace("&gt;", " ").replace('a{', "").replace('color:inherit;', "").replace("}", "")
        out = re.sub(re.compile('<.*?>'), '', out)
        try:
            out = fromstring(out).text
        except ParseError as e:
            if 'syntax error' in e.msg and "line" in e.msg and "column" in e.msg:
                pass
            else:
                print(e, " ".join(out.split("\n"))[:100])
        return out.strip()

    @staticmethod
    def get_text_key(text, keyword, end: str = "\n"):
        start = text.find(keyword) + len(keyword)
        end = text.find(end, start)
        return text[start:end]