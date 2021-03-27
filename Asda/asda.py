# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import requests

def get_product_ids():
    sitemap_url = 'https://groceries.asda.com/sitemap-products.xml'
    sitemap = bs(requests.get(sitemap_url).text, 'html.parser')

    product_ids = []
    product_urls = sitemap.find_all('loc')

    for product_url in product_urls:
        product_ids.append(product_url.text.split('/')[-1])

    pd.DataFrame({'Product ID': pd.Series(product_ids)}).to_excel('Product IDs.xlsx')

    return product_ids


def get_products(output, ids):
    json = {
        'item_ids': ids,
        'consumer_contract': 'webapp_pdp',
        'store_id': '4565',
        'request_origin': 'gi'
    }

    api_url = 'https://groceries.asda.com/api/items/catalog'
    data = requests.post(api_url, json=json).json()['data']['uber_item']['items']

    for item in data:
        promotions = item['promotion_info'][0]['linksave'] or item['promotion_info'][0]['rollback']
        if promotions:
            if item['promotion_info'][0]['rollback']:
                promo_type = 'Save'
                promo_text = 'Rollback'
                was_price = item['promotion_info'][0]['rollback']['was_price']
                promo_price =  item['price']['price_info']['price']
            else:
                promo_type = 'Multibuy'
                promo_text = item['promotion_info'][0]['linksave']['promo_detail']
                was_price =  item['price']['price_info']['price']
                promo_price = item['promotion_info'][0]['linksave']['promo_value']

        row = {
            'Product ID': item['item_id'],
            'Name': item['item']['name'],
            'Brand': item['item']['brand'],
            'Item Description': item['item']['picker_desc'],
            'Manufacturer': item['item_enrichment']['enrichment_info']['manufacturer_path'],
            'Category Level 1': item['item']['taxonomy_info']['category_name'],
            'Category Level 2': item['item']['taxonomy_info']['dept_name'],
            'Category Level 3': item['item']['taxonomy_info']['aisle_name'],
            'Category Level 4': item['item']['taxonomy_info']['shelf_name'],
            'Review Rating': item['item']['rating_review']['avg_star_rating'],
            'Review Count': item['item']['rating_review']['total_review_count'],
            'Availability': 'Y' if item['inventory']['availability_info']['availability'] == 'A' else 'N',
            'Price': item['price']['price_info']['price'],
            'Price Per Unit': item['price']['price_info']['price_per_uom'],
            'Promo': 'Y' if promotions else 'N',
            'Promo Type':  promo_type if promotions else '',
            'Promo Text': promo_text if promotions else '',
            'Was Price': was_price if promotions else '',
            'Promo Price': promo_price if promotions else '',
            'URL': 'https://groceries.asda.com/product/' + item['item_id'],
            'Date': str(datetime.now())
        }

        x = len(output)
        output.loc[x] = row
        print(output.loc[x])

    return output


def main():
    output = pd.DataFrame(columns=[
        'Category Level 1',
        'Category Level 2',
        'Category Level 3',
        'Category Level 4',
        'Brand',
        'Item Description',
        'Name',
        'Product ID',
        'Price',
        'Price Per Unit',
        'Promo',
        'Promo Type',
        'Promo Text',
        'Was Price',
        'Promo Price',
        'URL',
        'Date',
        'Manufacturer',
        'Availability',
        'Review Rating',
        'Review Count'
    ])

    products = get_product_ids()

    for product in range(0, 50, 10):
        if product + 10 <= len(products):
            output = get_products(output, products[product:product+10])
        else:
            output = get_products(output, products[product:])

    output.to_excel('Sample.xlsx', index=None)

    return


if __name__ == '__main__':
    main()
