# Ukrainian online films parser
###### based on Python framework Scrapy

### parser_name: site
* ukino: uakino.club
* eneyida: eneyida.tv

### Prepared
1. Download and extract
1. Create virtual environment 
   `python -m venv`   
1. Install requirements 
   `pip install -r requirements.txt`
   
### Run

`cd uakino`

`scrapy crawl parser_name`

### Database 
By default, the data is stored in the local MySQL database. 

The USED_DB parameter can be changed in settings.py. 

Also supported MySQL database

You can add, change DB in db.py

Work with databases is based by [Pony ORM] (https://docs.ponyorm.org/database.html)
