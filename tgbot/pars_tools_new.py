#!/usr/bin/python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
import requests


url = 'http://libgost.ru/gost/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
    'accept': '*/*'}

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='news')

    gosts = []
    for item in items:
        gosts.append({
            'title': item.find('div', class_='news').get_text()
        })
    print(gosts)

def parse():
    html = get_html(url)
    if html.status_code == 200:
        get_content(html.text)
    else:
        print('Error')


parse()
