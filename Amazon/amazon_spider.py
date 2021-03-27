import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'}

def spider_product(df, product):
    print('\n----------------------------------------------------------\n',requests.get(product, headers=headers))
    product_source = bs(requests.get(product, headers=headers).text, 'html.parser')

    specs = product_source.select('.techD:nth-child(1)')
    print(specs)
    if specs:
        print(specs)
        specs = specs[0].find_all('tr')
    else:
        specs = product_source.select('#prodDetails')
        print(specs)
        specs = specs[0].find_all('tr')

    count = len(df)
    df.at[count ,'Name'] = product.split('/')[3].replace('-', ' ')
    df.at[count, 'Link'] = product
    for spec in specs:
        if spec.select('.label'):
            if spec.select('.label')[0].text not in df.columns:
                print(spec.select('.label')[0].text)
                df.insert(len(df.columns), spec.select('.label')[0].text, value=[None for x in range(len(df))])
            df.at[count, spec.select('.label')[0].text] = spec.select('.value')[0].text

    print(df.loc[len(df)-1])
    df.to_excel('Amazon_data.xlsx')

    return df

    

def spider_search(df, product):
    search_url = 'https://www.amazon.in/s?k='
    url = search_url + ' '.join(product).replace(' ', '+')
    print(url)
    print(requests.get(url, headers=headers))
    search = bs(requests.get(url, headers=headers).text, 'html.parser')

    products = search.select('.a-section .rush-component .a-link-normal')[:-1]

    links = ['https://www.amazon.in' + link.get('href') for link in products]
    print(products[8:])

    for product_link in links:
        df = spider_product(df, product_link)

    return df

def main():
    df = pd.read_csv('Book1.csv')

    products = []
    print(len(df))
    for i in range(len(df)):
        products.append([df.loc[i]['Brand Name'], df.loc[i]['Product Name Line2']])


    df = pd.DataFrame(columns=['Name', 'Link'])
    #print(products)
    for product in products:
        df = spider_search(df, product)

if __name__ == '__main__':
    main()