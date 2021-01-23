import scrapy
import json
from lxml import html as ET
from lxml.html.clean import clean_html
from ukino.items import UkinoItem


class KinoSpider(scrapy.Spider):
    name = "uakino"

    def res_return(self, response):
        try:
            res = json.loads(response.text)
            return res
        except json.decoder.JSONDecodeError:
            self.failures += 1
            self.logger.error('JSON parse error retrying')
            return []

    def start_requests(self):
        urls = [
            'http://nserv.host:5300/eneyida/list?cat=films',
            'http://nserv.host:5300/uakino/list?cat=filmi',
            'http://nserv.host:5300/kinoukr/list?cat=films',
            "http://nserv.host:5300/eneyida/list?cat=cartoon",
            "http://nserv.host:5300/uakino/list?cat=cartoon",
            "http://nserv.host:5300/kinoukr/list?cat=cartoon",

        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.pre_parse)

    def pre_parse(self, response):
        
        cont = self.res_return(response)
        if isinstance(cont, dict):
            items = cont.get("channels")
            for i in items[:-1]:
                item_url = i.get("playlist_url", "")
                yield scrapy.Request(url=item_url, callback=self.parse)
                
            next_page_url=cont.get("next_page_url", response.url)
            old_url = response.url
            print(old_url,next_page_url)
            if old_url != next_page_url:
                print("go to new")
                yield scrapy.Request(url=next_page_url, callback=self.pre_parse)
                #yield response.follow(next_page_url, self.pre_parse)
            else:
                print(old_url,next_page_url)
        else:
            print("Look, its all!")
            return

    def parse(self, response):
        item = self.res_return(response)        
        
        ch=item.get("channels",[])
        my_list=[]
        def get_type():
            type_src="other"  
            if response.url.find("cat=cartoon")!=-1: 
                type_src="cartoon"
            elif response.url.find("cat=film")!=-1:
                type_src="uakino"
            return type_src

        title_ua=""    
        type_src=get_type()
        title_or=""
        poster=""
        desc=""
        year=""
        director=""
        all_links={}

        def get_list(itis):
            itis = clean_html(itis)
            con=0
            for i in itis.replace("</strong>", "<strong>").split("<strong>"):
               #print(con)
               x=i.replace("<br>","").replace("<div>","").replace("</div>","").replace("\n","").strip()
               #print(x)
               if con in [1,14,18]:
                    my_list.append(x)
               if con == 4:
                    x=x.replace("- Знімається", "").replace("- Закінчений", "")
                    x=x.split(",")
                    my_list.append(x[-1].strip())
               con=con+1
            return my_list
        
        
        if len(ch)>0:
            for i in ch:
                if i.get("title") == "Описание":
                    desc =str(i.get("description","[]")).replace("'", '"')#+"'''""'''"+
                    tree = ET.fromstring(desc)
                    poster = tree.xpath('//img[@src]')[0].attrib["src"]
                    my_list=get_list(desc)
                    if len(my_list) >0:
                        names = my_list[0].split("/")
                        title_ua = names[0].replace("'", '"').strip()
                        if len(names)>1:
                            title_or = ":".join(names[1:]).replace("'", '"').strip()
                        else:
                            title_or=""
                        try:
                            year=my_list[1]
                        except (IndexError,ValueError):
                            year=""
                        try:
                            director=my_list[2].replace("'", '"')
                        except (IndexError,ValueError):
                            director=""
                        try:
                            desc=my_list[3]
                        except (IndexError,ValueError):
                            desc=desc


                elif i.get("title") != "Описание" and i.get("title") != "Трейлер" and i.get("title") != "Cледующая страница":
                    qa = i.get("title", "?")
                    link=i.get("stream_url")
                    all_links.update({qa:link})

        item_dict= dict(title_ua=title_ua, type_src=type_src, title_or=title_or, poster=poster, desc=desc, year=year, 
                director=director, all_links=all_links)
        itm = UkinoItem(**item_dict)
        yield itm




        