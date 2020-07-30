#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
import requests
from settings import SEARCH_URL

def get_search_list(search_text):
    params = {
        "searchString": search_text,
        "searchcatalogbtn": "Искать"
    }
    r = requests.get(SEARCH_URL, params=params)
    search_list = []
    soup = BeautifulSoup(r.content, 'html.parser')
    return [['хуй', 'залупа'], ['хер', 'блядина'], ['гост1488', 'мы харбас в ваш дом приносим']]
    # TODO по аналогии с видео с парсингом сайтов достать из страницы ответ r.content или r.text все найденнные госты
    # пока что только на первой странице и записать в search_list
    # формат [['название', 'текст_описание'], ]

