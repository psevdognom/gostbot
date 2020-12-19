#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
import requests

from PIL import Image
import pytesseract

from tgbot.settings import SEARCH_URL
from tgbot.models import Gost, session

def get_gost_from_photo(photo):
    print(pytesseract.image_to_string(Image.open('test.png')))

def get_search_list(search_text):
    params = {
        "searchString": search_text,
        "searchcatalogbtn": "Искать"
    }
    r = requests.get(SEARCH_URL, params=params)
    search_list = []
    soup = BeautifulSoup(r.content, 'html.parser')
    results = soup.findAll('div', class_='textBlue')
    return [['хуй', 'залупа'], ['хер', 'блядина'], ['гост1488', 'мы харбас в ваш дом приносим']]
    # TODO по аналогии с видео с парсингом сайтов достать из страницы ответ r.content или r.text все найденнные госты
    # пока что только на первой странице и записать в search_list
    # формат [['название', 'текст_описание'], ]

def get_search_list_db(search_text):
    res = session.query(Gost).filter(Gost.name.like('%' + search_text + '%')).all()
    res.extend(session.query(Gost).filter(Gost.description.like('%' + search_text + '%')).all())
    return res
