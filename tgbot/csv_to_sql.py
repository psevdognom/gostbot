import requests
from lxml import html
import sqlite3

conn = sqlite3.connect('gost.db')
c = conn.cursor()
c.execute('''
          CREATE TABLE gosts
          (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	      name varchar(50) NOT NULL,
	      title varchar(250) NOT NULL,
	      status varchar(15) NOT NULL,
	      key varchar(30) NOT NULL)
         ''' )

link = 'https://www.gost.ru'
page = requests.get(link+"/opendata/7706406291-nationalstandards")
tree = html.fromstring(page.content)
link += tree.xpath('//*[@id="242b6628-20e0-459f-b512-2fe12015e7eb"]/div/div[1]/div[5]/div[1]/a/@href')[0]
file = requests.get(link).content.decode('cp1251').splitlines()
for line in file:
    data = line.split(";")
    c.execute(f"INSERT INTO gosts VALUES({data[0]}, {data[1]}, {data[2]}, {data[3]})")
conn.commit()
conn.close()