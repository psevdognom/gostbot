import requests
from lxml import html
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tgbot.models import Gost

Base = declarative_base()

engine = create_engine('sqlite:///gosts.db')
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

link = 'https://www.gost.ru'
page = requests.get(link+"/opendata/7706406291-nationalstandards")
tree = html.fromstring(page.content)
link += tree.xpath('//*[@id="242b6628-20e0-459f-b512-2fe12015e7eb"]/div/div[1]/div[5]/div[1]/a/@href')[0]
file = requests.get(link).content.decode('cp1251').splitlines()
for i in range(1, len(file)):
    data = file[i].split(";")
    gost = Gost(name=data[0], description=data[1])
    session.add(gost)
session.commit()