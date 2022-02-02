import scrapy
import re
from xml.etree.ElementTree import fromstring
from xml.etree.ElementTree import ParseError



class CoreSpider(scrapy.Spider):

    @staticmethod
    def tag_cleaner(out):
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
        start = text.find(keyword)
        if start == -1:
            return None
        start = start + len(keyword)
        end = text.find(end, start)
        if end == -1:
            end = len(text)
        return text[start:end]

    @classmethod
    def get_detailed_values(cls, description):
        description = cls.tag_cleaner(description)
        categories = cls.get_text_key(description, "Категорія:")
        director = cls.get_text_key(description, "Режисер:")
        year = cls.get_text_key(description, "Рік:")
        actors = cls.get_text_key(description, "Актори:")
        return {"categories": categories, "actors": actors, "director": director, "year": year}
