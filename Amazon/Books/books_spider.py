from bs4 import BeautifulSoup as bs
import json
import logging
import os
import pandas as pd
import re
import requests

def init_vars():
    global headers, session, logger, df
    
    headers = {
        'Host': 'www.amazon.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }

    session = requests.Session()

    df = pd.DataFrame(columns=[
        'Category',
        'Title',
        'Listing URL',
        '#Stars',
        '#Ratings',
        '#Questions Answered',
        'Price',
        'Product Overview',
        'Front Image URL',
        'Back Image URL',
        'Ships From',
        'Sold By',
        'New#' ,
        'Old#' ,
        '# of Pages',
        'Product Description',
        'Product Dimesions & Weights',
        'Date First Available',
        'ASIN',
        'Rank',
        '# of Review Videos',
        'Embedded'
    ], dtype=str)

    # Create and configure logger
    logging.basicConfig(
        filename="Amazon_Scraper.log",
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'
    )
    
    # Creating an object
    logger = logging.getLogger()
    
    # Setting the threshold of logger to DEBUG
    logger.setLevel(logging.DEBUG)


def save_image(type_of_book: str, book_category: str, data: dict) -> None:
    if not os.path.exists(os.path.join(os.getcwd(), type_of_book)):
        os.mkdir(os.path.join(os.getcwd(), type_of_book))
    
    path_of_image = os.path.join(os.getcwd(), os.path.join(type_of_book, book_category))
    if not os.path.exists(path_of_image):
        os.mkdir(path_of_image)
    
    if data['Front Image URL']:
        title = data['Title'].replace(':', '').replace('\'', '').replace('*', '').replace('’', '').replace('|', '').replace(',', '').replace('/', '').strip()
        with open(os.path.join(path_of_image, f"{title} (Front Cover).jpg"), 'wb') as f:
            f.write(session.get(data['Front Image URL'], headers=headers).content)

    if data['Back Image URL']:
        title = data['Title'].replace(':', '').replace('\'', '').replace('*', '').replace('’', '').replace('|', '').replace(',', '').replace('/', '').strip()
        with open(os.path.join(path_of_image, f"{title} (Back Cover).jpg"), 'wb') as f:
            f.write(session.get(data['Back Image URL'], headers=headers).content)


def get_listings(url: str, rank: str) -> dict:
    url = 'https://www.amazon.com' + url
    page = bs(session.get(url, headers=headers).text, 'lxml')

    if page.find('a', {'href': re.compile('tmm_hrd_swatch_0')}):
        url = 'https://www.amazon.com' + page.find('a', {'href': re.compile('tmm_hrd_swatch_0')}).get('href')
        page = bs(session.get(url, headers=headers).text, 'lxml')


    elif page.find('a', {'href': re.compile('tmm_pap_swatch_0')}):
        url = 'https://www.amazon.com' + page.find('a', {'href': re.compile('tmm_pap_swatch_0')}).get('href')
        page = bs(session.get(url, headers=headers).text, 'lxml')

    return {
        'Title': page.find('span', {'id': 'productTitle'}).text.strip(),
        'Listing URL': url.split('?')[0],
        '#Stars': page.find('span', {'id': 'acrPopover'}).get('title').split()[0] if page.find('span', {'id': 'acrPopover'}) and page.find('span', {'id': 'acrPopover'}).get('title') else '',
        '#Ratings': page.find('span', {'id': 'acrCustomerReviewText'}).text if page.find('span', {'id': 'acrCustomerReviewText'}) else '',
        '#Questions Answered': '',
        'Price': page.find('span', {'class': 'a-size-base a-color-price a-color-price'}).text if page.find('span', {'class': 'a-size-base a-color-price a-color-price'}) else '',
        'Product Overview': page.find('div', {'class': 'a-expander-content a-expander-partial-collapse-content'}).text.strip() if page.find('div', {'class': 'a-expander-content a-expander-partial-collapse-content'}) else '',
        'Front Image URL': page.find_all('div', {'class': 'a-column a-span3 a-spacing-micro imageThumb thumb'})[0].find('img').get('src').split('._AC')[0] + '.jpg' if len(page.find_all('div', {'class': 'a-column a-span3 a-spacing-micro imageThumb thumb'})) > 0 else '',
        'Back Image URL': page.find_all('div', {'class': 'a-column a-span3 a-spacing-micro imageThumb thumb'})[1].find('img').get('src').split('._AC')[0] + '.jpg' if len(page.find_all('div', {'class': 'a-column a-span3 a-spacing-micro imageThumb thumb'})) > 1 else '',
        'Ships From': page.find('div', {'tabular-attribute-name': 'Ships from', 'class':'tabular-buybox-text'}).text.strip() if page.find('div', {'tabular-attribute-name': 'Ships from', 'class':'tabular-buybox-text'}) else '',
        'Sold By': page.find('div', {'tabular-attribute-name': 'Sold by', 'class':'tabular-buybox-text'}).text.strip() if page.find('div', {'tabular-attribute-name': 'Sold by', 'class':'tabular-buybox-text'}) else '',
        'New#': '',
        'Old#': '',
        '# of Pages': page.find('div', {'id': 'rpi-attribute-book_details-fiona_pages'}).find('span', string=re.compile('pages')).text if page.find('div', {'id': 'rpi-attribute-book_details-fiona_pages'}) else '', #to be taken from product attributes
        'Product Description': page.find('div', {'class': 'a-cardui _about-the-author-card_carouselItemStyles_expander__3Fm-M'}).text if page.find('div', {'class': 'a-cardui _about-the-author-card_carouselItemStyles_expander__3Fm-M'}) else '',
        'Product Dimesions & Weights': page.find('div', {'id': 'rpi-attribute-book_details-dimensions'}).find('span', string=re.compile('inches')).text if page.find('div', {'id': 'rpi-attribute-book_details-dimensions'}) else '', #to be taken from product attributes
        'Date First Available': page.find('div', {'id': 'rpi-attribute-book_details-publication_date'}).find('span', string=re.compile('[A-z]* \d{1,2}\, \d{4}')).text if page.find('div', {'id': 'rpi-attribute-book_details-publication_date'}) else '', #to be taken from product attributes
        'ASIN': url.split('/')[5], #to be taken from URL
        'Rank': rank,
        '# of Review Videos': '',
        'Embedded': ''
    }



def get_pages(url: str) -> dict:
    '''
        Get initial 30 listings from page, then take the 8 ids at a time to scrape up to 50, i.e. 30 from page, 8-8-4 from API

        Sample link: https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/<page_number> , here page number can be either 1 or 2, since best sellers take only top 100

        returns a dictionary with position in best-selling list as index and product's url as value 
    '''
    post_headers = headers.copy()

    page = bs(session.get(url, headers=post_headers).text, 'lxml')

    listings = {listing.find('span', {'class': 'zg-bdg-text'}).text.strip().lstrip('#'): listing.find('a').get('href') for listing in page.find_all('div', {'id': re.compile('p13n-asin-index-')}) if listing.find('span', {'class': 'a-size-small a-color-secondary a-text-normal'}) and listing.find('span', {'class': 'a-size-small a-color-secondary a-text-normal'}).text.strip().lower() != 'kindle edition'}

    acp_url = 'https://www.amazon.com' + page.find('div', {'data-acp-path': re.compile('.*')}).get('data-acp-path') + 'nextPage?page-type=undefined&stamp=' + page.find('div', {'data-acp-stamp': re.compile('.*')}).get('data-acp-stamp')
    post_headers['Accept'] = '*/*'
    post_headers['Accept-Encoding'] = 'gzip, deflate, br'
    post_headers['Content-Type'] = 'application/json'
    post_headers['X-Requested-With'] = 'XMLHttpRequest' 
    post_headers['X-AMZ-ACP-Params'] = page.find('div', {'data-acp-params': re.compile('.*')}).get('data-acp-params')

    rec_lists = page.find('div', {'data-acp-params': re.compile('.*')}).find('div', {'data-client-recs-list': re.compile('.*')}).attrs
    payload = {
        'faceoutkataname': rec_lists.pop('data-faceoutkataname'),
        'ids': [json.dumps(rec) for rec in json.loads(rec_lists['data-client-recs-list'])][30:38],
        'indexes': [x for x in range(30, 38)],
        'linkparameters': '',
        'offset': '1',
        'reftagprefix': rec_lists.pop('data-reftag'),
    }

    post_headers['Content-Length'] = str(len(json.dumps(payload)))

    listings.update({listing.find('span', {'class': 'zg-bdg-text'}).text.strip().lstrip('#'): listing.find('a').get('href') for listing in bs(session.post(acp_url, json=payload, headers=post_headers).text, 'lxml').find_all('div', {'id': 'gridItemRoot'})  if listing.find('span', {'class': 'a-size-small a-color-secondary a-text-normal'}) and listing.find('span', {'class': 'a-size-small a-color-secondary a-text-normal'}).text.strip().lower() != 'kindle edition'})

    payload['ids'] = [json.dumps(rec) for rec in json.loads(rec_lists['data-client-recs-list'])][38:46]
    payload['indexes'] = [_ for _ in range(38, 46)]

    post_headers['Content-Length'] = str(len(json.dumps(payload)))

    listings.update({listing.find('span', {'class': 'zg-bdg-text'}).text.strip().lstrip('#'): listing.find('a').get('href') for listing in bs(session.post(acp_url, json=payload, headers=post_headers).text, 'lxml').find_all('div', {'id': 'gridItemRoot'})  if listing.find('span', {'class': 'a-size-small a-color-secondary a-text-normal'}) and listing.find('span', {'class': 'a-size-small a-color-secondary a-text-normal'}).text.strip().lower() != 'kindle edition'})

    payload['ids'] = [json.dumps(rec) for rec in json.loads(rec_lists['data-client-recs-list'])][46:50]
    payload['indexes'] = [_ for _ in range(46, 50)]

    post_headers['Content-Length'] = str(len(json.dumps(payload)))

    listings.update({listing.find('span', {'class': 'zg-bdg-text'}).text.strip().lstrip('#'): listing.find('a').get('href') for listing in bs(session.post(acp_url, json=payload, headers=post_headers).text, 'lxml').find_all('div', {'id': 'gridItemRoot'})  if listing.find('span', {'class': 'a-size-small a-color-secondary a-text-normal'}) and listing.find('span', {'class': 'a-size-small a-color-secondary a-text-normal'}).text.strip().lower() != 'kindle edition'})
    
    return listings


def main():
    init_vars()
    global df

    urls = {
        'Best Sellers': 'https://www.amazon.com/best-sellers/zgbs/books',
        'New Releases': 'https://www.amazon.com/gp/new-releases/books'
    }

    categories = pd.read_csv('Categories.csv')

    for type_of_book, book_url in urls.items():
        for category_name, category_id in zip(categories['Category Name'].tolist(), categories['Category Id'].tolist()):       
            url = f"{book_url}/{category_id}"
            listings = get_pages(url)

            for rank, url in listings.items():
                data = {
                    'Category': category_name,
                    **get_listings(url, rank)
                }

                df.loc[len(df)] = data
                save_image(type_of_book, category_name, data)

                logger.debug(df.loc[len(df)-1])

                df = df.fillna('')
                df.to_csv(f'{type_of_book}.csv', index=None)
        


if __name__ == '__main__':
    main()