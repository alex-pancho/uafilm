import requests

res = requests.get("https://uakino.best/filmy/page/380/")
print(res.content)