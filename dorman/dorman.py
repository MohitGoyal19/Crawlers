# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
import pandas as pd
import random
import requests
from time import sleep

def request(url):
    headers = {
        'host': 'www.dormanproducts.com'
    }
    proxies = get_proxies()

    try:
        proxy_link = random.choice(proxies)
        proxy = {
            'http': proxy_link,
            'https': proxy_link
        }

        response = requests.get(url, headers=headers, proxies=proxy)

    except:
        response = request(url)
        sleep(2)

    return response


def get_proxies():
    print('Finding Proxies, please wait')
    page = bs(requests.get('https://free-proxy-list.net/').text, 'html.parser')
    proxies = page.find('table', {'id': 'proxylisttable'}).find('tbody').find_all('tr')
    working = []

    for x in range(len(proxies)):
        proxies[x] = proxies[x].find_all('td')[0].text + ':' + proxies[x].find_all('td')[1].text

    return proxies


def text_format(tag):
    text = '^'.join([row.text for row in tag.find_all('tr')]).replace(':', '|')

    return text


def get_app_details(prod_id, category):
    link = 'https://www.dormanproducts.com/itemdetailapp.aspx?ProductID={}&PartType={}'.format(prod_id, category)
    page = bs(requests.get(link).text, 'html.parser')

    det_text = []
    rows = page.find_all('tr', {'class': 'detail-app-row'})

    for row in rows:
        det_text.append('|'.join([td.text.replace('\r\n                        ', '').replace('\r\n                    ', '').replace('\n', ' ') for td in row.find_all('td')]))

    det_text = '^'.join(det_text)

    return det_text


def get_data(df, link):
    response = requests.get(link)
    page = bs(response.text, 'html.parser')

    make = page.find('input', {'id': 'make'}).get('value')
    model = page.find('input', {'id': 'model'}).get('value')
    year = page.find('input', {'id': 'year'}).get('value')
    engine = ''
    category = page.find('input', {'id': 'parttype'}).get('value')
    prod_no = page.find('span', {'id': 'lblProductName'}).text
    name = page.find('span', {'id': 'lblProductDesc'}).text
    app_sum = page.find('div', {'id': 'divAppSummary'}).text.strip().lstrip('Application Summary:').strip()
    app_notes = page.find('div', {'id': 'divNote'}).text.strip()
    desc = page.find('section', {'id': 'productDesc'}).find('div').text.strip()
    
    spec = text_format(page.find('section', {'id': 'productSpec'}).find('table')).replace('\r\n          ', '')
    oe = '^'.join([row.text.strip().replace('\n', '|') for row in page.find('section', {'id': 'productOE'}).find('tbody').find_all('tr')])
    image1 = page.find('a', {'id': 'ProductPic'}).get('href')
    image2 = page.find('a', {'data-zoom-id': 'ProductPic'}).get('href')

    main_url = 'https://www.dormanproducts.com/gsearch.aspx?' + link.split('?')[1]

    prod_id = page.find('input', {'id': 'productid'}).get('value')
    app_details = get_app_details(prod_id, category)

    x = len(df)
    df.loc[x] = [make, model, year, engine, category, prod_no, name, app_sum, app_notes, desc, app_details, spec, oe, main_url, link, image1, image2]
    print(df.loc[x])

    return df


def get_products(df, year):
    url = f'https://www.dormanproducts.com/gsearch.aspx?year={year}&origin=YMM'

    products = bs(request(url).text, 'html.parser').find('span', {'id': 'lblResultCount'}).text
    print(products, year)
    if not products:
        print('khali hai')

    return df



def main():
    df = pd.DataFrame(columns=['Make', 'Model', 'Year', 'Engine', 'Brand/Category', 'Product Number', 'Product Name', 'Application Summary', 'Application Notes', 'Product Description', 'Detailed Applications', 'Product Specifications', 'OE Numbers', 'Main Url', 'Product Url', 'Image Url1', 'Image Url2'])
    
    for year in range(2021, 1914, -1):
        if not year in [1927, 1926, 1924, 1921, 1920, 1919, 1918, 1917, 1916]:
            df = get_products(df, year)


    #df.to_excel('Sample.xlsx', index=None)

    return

if __name__ == '__main__':
    main()
