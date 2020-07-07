# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
import math
import pandas as pd
import random
import re
import requests
from time import sleep

def request(url):
    sleep(120)
    headers = {
        'host': 'www.dormanproducts.com',
        'user-agent': 'Googlebot'
    }
    #proxies = get_proxies()

    
    #proxy_link = random.choice(proxies)
    proxy_host = "proxy.crawlera.com"
    proxy_port = "8010"
    proxy_auth = "512343bd229f4d8e9e356710b11003dc:"

    proxy = {
        "https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
        "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)
    }

    response = requests.get(url, headers=headers, proxies=proxy, allow_redirects=False, verify=False)

    '''except:
        response = request(url)
        sleep(2)
'''
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
    if not page.find('a', {'id': 'pagingBottom_nextButton'}):
        rows = page.find_all('tr', {'class': 'detail-app-row'})
    else:
        rows = []
        link = 'https://www.dormanproducts.com/itemdetailapp.aspx?ProductID={}&PartType={}&start={}&num=50'
        page_no = 0
        while True:
            page = bs(requests.get(link.format(prod_id, category, page_no*50)).text, 'html.parser')
            rows.append(page.find_all('tr', {'class': 'detail-app-row'}))
            page_no += 1
            if not page.find('a', {'id': 'pagingBottom_nextButton'}):
                break

    for row in rows:
        det_text.append('|'.join([td.text.replace('\r\n                        ', '').replace('\r\n                    ', '').replace('\n', ' ') for td in row.find_all('td')]))

    det_text = '^'.join(det_text)
    for row in rows:
        yield{
            'Make': row.find_all('td')[1].text,
            'Model': row.find_all('td')[2].text,
            'Year': row.find_all('td')[0].text,
            'Applications': det_text
        }


def get_data(df, link):
    print('Getting Product......')
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
    app_notes = page.find('div', {'id': 'divNote'}).text.strip() if page.find('div', {'id': 'divNote'}) else ''
    desc = page.find('section', {'id': 'productDesc'}).find('div').text.strip()
    
    spec = text_format(page.find('section', {'id': 'productSpec'}).find('table')).replace('\r\n          ', '')
    oe = '^'.join([row.text.strip().replace('\n', '|') for row in page.find('section', {'id': 'productOE'}).find('tbody').find_all('tr')])
    image1 = page.find('a', {'id': 'ProductPic'}).get('href')
    image2 = page.find('a', {'data-zoom-id': 'ProductPic'}).get('href')

    main_url = 'https://www.dormanproducts.com/gsearch.aspx?' + link.split('?')[1]

    prod_id = page.find('input', {'id': 'productid'}).get('value')
    app_details = get_app_details(prod_id, category)

    for app in app_details:
        x = len(df)
        df.loc[x] = [app['make'], app['model'], app['year'], engine, category, prod_no, name, app_sum, app_notes, desc, app['Applications'], spec, oe, main_url, link, image1, image2]
        print(df.loc[x])
    df.to_excel('Dorman_Data.xlsx', index=None)

    return df


def get_products(df, year):
    url = f'https://www.dormanproducts.com/gsearch.aspx?year={year}&origin=YMM'

    product_count = int(bs(request(url).text, 'html.parser').find('span', {'id': 'lblResultCount'}).text)
    pages = math.ceil(product_count/100)

    print(year, ': ', product_count)

    for start in range(pages):
        url = f'https://www.dormanproducts.com/gsearch.aspx?year={year}&origin=YMM&start={start*100}&num=100'
        products = ['https://www.dormanproducts.com/' + link.get('href') for link in bs(request(url).text, 'html.parser').find_all('a', {'id': re.compile('rptDetails\_ctl\d+\_alinkProductName')})]

        print(len(products), products)

        for product in products:
            df = get_data(df, product) 

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
