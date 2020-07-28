from bs4 import BeautifulSoup
import requests
from .settings import SEARCH_URL

def get_search_list(search_text):
    params = {
        "searchString": search_text,
        "searchcatalogbtn": "Искать"
    }
    r = requests.get(SEARCH_URL, params=params)
    search_list = []
    return search_list
    # TODO по аналогии с видео с парсингом сайтов достать из страницы ответ r.content или r.text все найденнные госты
    # пока что только на первой странице и записать в search_list
    # формат [['название', 'текст_описание'], ]

