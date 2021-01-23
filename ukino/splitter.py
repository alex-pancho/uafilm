from lxml import html as ET
from lxml.html.clean import clean_html

it={'all_local': 'directly', 'background-image': 'http://cdn.nserv.host/img/bg/treeview.jpg', 
        'channels': [
        {'title': 'Описание', 'description': 
        """<div id="cover_div" style="float: left; margin: 0px 1.8% 0px 0px;">
        <img id="cover_img" style="width: 185px;" src="https://kinoukr.com/uploads/posts/2020-06/1591608137_poster.jpg" />
        </div>
        <span id="title" style="color: #699bbb;">
        <strong style="font-size: 1.9vw">Правдива історія банди Келлі / True History of the Kelly Gang</strong></span><br /><br />
        <div id="description" style="font-size: 1.7vw">
        <strong><span style="color: #3974d0;">Вихід:</span></strong> Велика Британія, 2019<br />
        <strong><span style="color: #3974d0;">Жанр:</span></strong> Біографія, Вестерн, Драма, Кримінал<br /><strong>
        <span style="color: #339966;">Переклад:</span></strong> Дубляж<br /><strong>
        <span style="color: #339966;">Тривалість:</span></strong> 02:05:08<br /><strong>
        <span style="color: #f29420;">IMDb:</span></strong> 6.10<br /><br /><strong>
        <span style="color: #03b9cc;">Режиссер:</span></strong> Джастін Курзель<br />
        <div style="clear: both; font-size: ; "><br />
        <strong><span style="color: #00a0b0;">Актори:</span></strong> Джордж МакКей, Расселл Кроу, Ніколас Голт, Ессі Девіс, Чарлі Ганнем, 
        Томасін МакКензі<br /><br />
        <strong><span style="color: #3974d0;">Опис:</span></strong> 
        Захоплююча кримінально-біографічна драма про одного з найбільш суперечливих персонажів світової кримінальної історії - Неда Келлі. 
        Ким він був, безжальним вбивцею або борцем за справедливість - обирати вам.<br><br>Події розгортаються в середині ХІХ століття в одній з 
        Британських колоній - Австралії. За сюжетом, хлопчик на ім\'я Нед Келлі ріс сильним, сміливим та непокірним. Щодня він бачив навколо себе 
        жорстокість, а також несправедливість і свавілля влади й поліції. Не бажаючи миритися з цим, він очолив спротив, почавши грабувати банки. 
        Поліція тремтіла від одного згадування його імені, а ба прості люди вважали його за героя та народного месника, такого собі сучасного Робіна 
        Гуда.<br><br>Фільм «Правдива історія банди Келлі» (2019) варто дивитися онлайн українською мовою усім, хто цікавиться історії кримінального 
        світу.<br /></div></div>""",
        'logo_30x30': 'http://cdn.nserv.host/img/info.png', 'details': False}, 
        {'title': 'Трейлер', 'description': '''<div style="text-align: center">
        <img width="40%" src="https://kinoukr.com/uploads/posts/2020-04/1587922061_1.jpg" />
        <img width="40%" src="https://kinoukr.com/uploads/posts/2020-04/1587922046_2.jpg" />
        <img width="40%" src="https://kinoukr.com/uploads/posts/2020-04/1587922106_3.jpg" />
        <img width="40%" src="https://kinoukr.com/uploads/posts/2020-04/1587922125_4.jpg" />
        <img width="40%" src="https://kinoukr.com/uploads/posts/2020-04/1587922056_5.jpg" />
        <img width="40%" src="https://kinoukr.com/uploads/posts/2020-04/1587922122_6.jpg" /></div>''',
         'logo_30x30': 'http://cdn.nserv.host/img/youtube.png', 
         'stream_url': 'https://sparrow.tortuga.wtf/content/stream/trailers/true_history_of_the_kelly_gang_2019_17187/hls/index.m3u8', 'details': False}, 
         {'title': '1080p', 'logo_30x30': 'http://cdn.nserv.host/img/mediafile.png', 
         'stream_url': 'https://blackpearl.tortuga.wtf/content/stream/films/true.history.of.the.kelly.gang.2o19.d.webdl.1080p_34031/hls/1080/index.m3u8', 
         'details': False}, 
         {'title': '720p', 'logo_30x30': 'http://cdn.nserv.host/img/mediafile.png', 
         'stream_url': 'https://blackpearl.tortuga.wtf/content/stream/films/true.history.of.the.kelly.gang.2o19.d.webdl.1080p_34031/hls/720/index.m3u8', 
         'details': False}, 
         {'title': '480p', 'logo_30x30': 'http://cdn.nserv.host/img/mediafile.png', 
         'stream_url': 'https://blackpearl.tortuga.wtf/content/stream/films/true.history.of.the.kelly.gang.2o19.d.webdl.1080p_34031/hls/480/index.m3u8', 
         'details': False}], 
         'is_iptv': False}
itis = it['channels'][0]['description']
itis = clean_html(itis)
print(itis)
input()

def _printResponse(res, name=''):
    print('D-res : ', name)
    for child in res.iter('*'):
        print('\t', child.tag, child.attrib, child.text)
    print('\n')

tree=ET.fromstring(itis) 
poster = tree.xpath('//img[@src]')[0].attrib["src"]
print(poster)
con=0
my_list=[]
for i in itis.replace("</strong>", "<strong>").split("<strong>"):
   #print(con)
   x=i.replace("<br>","").replace("<div>","").replace("</div>","").replace("\n","").strip()
   #print(x)
   if con in [1,14,18]:
        my_list.append(x)
   if con == 4:
        x=x.split(",")
        my_list.append(x[-1])
   con=con+1
print(my_list)