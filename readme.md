# Ukrainian online films parser
###### based on Python framework Scrapy

### parser_name: site
* **ukino**: uakino.club
* **eneyida**: eneyida.tv

### Prepared
1. Download and extract
1. Create virtual environment: <br> 
   `python -m venv`   
1. Install requirements: <br> 
   `pip install -r requirements.txt`
   
### Run

`cd uakino` <br>
`scrapy crawl {parser_name}`

### Databases 
By default, the data is stored in the local MySQL database.<br>
Work with databases is based by [Pony ORM](https://docs.ponyorm.org/database.html). <br>
You can add, change and config DB connecton setting in `db.py`<br>
Also supported SQLite databases.<br>
The type of database used changes the `USE_DB` parameter in the `settings.py`.<br>



