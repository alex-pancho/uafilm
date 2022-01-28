from scrapy import cmdline
#cmdline.execute("cd uakino".split())
spy_name = "ukino"
cmdline.execute(f"scrapy crawl {spy_name}".split())
