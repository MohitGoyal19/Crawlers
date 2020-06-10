from bs4 import BeautifulSoup as bs
import json
from math import ceil
import pandas as pd
import re
import requests
from time import sleep

def request(link):
    try:
        response = requests.get(link)
    except:
        sleep(8)
        response = request(link)

    return response


def get_data(link, cat):
    response = request(link)
    print(link)
    if response.status_code == 404:
        item = get_data(link, cat)
        return item

    page = bs(response.text, 'html5lib')

    data = json.loads(page.find('script', {'type': 'application/ld+json'}).text) if page.find('script', {'type': 'application/ld+json'}).text else ''
    if not data:
        return [None]*25

    working_hours = dict()
    for day in data["openingHoursSpecification"]:
        working_hours[day['dayOfWeek']] = dict()
        if day['opens'] == day['closes']:
            working_hours[day['dayOfWeek']]['opens'] = 'CLOSED'
            working_hours[day['dayOfWeek']]['closes'] = 'CLOSED'
        else:
            working_hours[day['dayOfWeek']]['opens'] = day['opens']
            working_hours[day['dayOfWeek']]['closes'] = day['closes']

    item = [
        cat,
        page.find('h2' , {'class': 'yext-name'}).text if page.find('h2' , {'class': 'yext-name'}) else '',
        page.find('a', {'class': 'yext-url-website'}).text.strip() if page.find('a', {'class': 'yext-url-website'}) else '',
        page.find('span', {'class': 'yext-categories'}).text.replace('✔', '').strip() + ', ' + ', '.join([prod.text.replace('✔', '').strip() for prod in page.find_all('span', {'class': 'yext-keywords'})]),
        page.find('a', {'class': 'yext-phone'}).text.strip() if page.find('a', {'class': 'yext-phone'}) else '',
        page.find('a', {'class': 'yext-emails'}).text.strip() if page.find('a', {'class': 'yext-emails'}) else '',
        page.find('span', {'id': 'location'}).text.strip().lstrip(',').strip() if page.find('span', {'id': 'location'}) else '',
        working_hours['Monday']['opens'],
        working_hours['Monday']['closes'],
        working_hours['Tuesday']['opens'],
        working_hours['Tuesday']['closes'],
        working_hours['Wednesday']['opens'],
        working_hours['Wednesday']['closes'],
        working_hours['Thursday']['opens'],
        working_hours['Thursday']['closes'],
        working_hours['Friday']['opens'],
        working_hours['Friday']['closes'],
        working_hours['Saturday']['opens'],
        working_hours['Saturday']['closes'],
        working_hours['Sunday']['opens'],
        working_hours['Sunday']['closes'],
        page.find('p', {'class': 'yext-city'}).text if page.find('p', {'class': 'yext-city'}) else '',
        page.find('img', {'class': 'yext-image-logo'}).get('data-src') if 'http' in page.find('img', {'class': 'yext-image-logo'}).get('data-src') else 'https://www.yellowpages.co.za' + page.find('img', {'class': 'yext-image-logo'}).get('data-src').lstrip('..'),
        page.find('meta', {'name': 'description'}).get('content'),
        page.find('span', {'class': 'yext-description'}).text if page.find('span', {'class': 'yext-description'}) else ''
    ]

    return item


def get_listings(link):
    response = request(link)
    if response.status_code == 404:
        return get_listings(link)

    page = bs(response.text, 'html.parser')
    links = page.find_all('a', {'href': re.compile('/business/\d+.*')})

    return links    


def get_pages(link):
    response = request(link)
    #print(response.status_code, type(response.status_code))
    if response.status_code == 404:
        return 0

    page = bs(response.text, 'html.parser')
    listings = int(page.find('div', {'id': 'YellowResultsDiv'}).find('div', {'class': 'container-fluid'}).find('p').text.strip().split()[-1])

    return listings


def main():
    cats = [
        'Animal Training Centre',
        'Beauty Parlor',
        'Cab Service',
        'Cafe',
        'Car Care & Servicing',
        'Car Dealer',
        'Car Driving',
        'Cardiologist',
        'Carpenter',
        'Carpet Cleaning',
        'Child Care Center',
        'Commercial Cleaning',
        'Computer & Laptop Repair',
        'Construction Companies',
        'Denter and Painter',
        'Dentist',
        'Education Institute',
        'Electrician',
        'Event Organizer',
        'Fast Food',
        'Finance & Legal',
        'Gym Center',
        'Home Cleaning',
        'Insurance',
        'IT/Web Development',
        'Laundry',
        'Marketing',
        'Massage Center',
        'Mobile Repair',
        'Neurosurgeon',
        'Packer & Movers',
        'Painter',
        'Pediatrician',
        'Pet Care Center',
        'Pet Dealer',
        'Physician',
        'Plumber',
        'Pubs & Bars',
        'Renovation Companies',
        'Rent A Car',
        'Resturant',
        'Self Motivation Center',
        'Spa Center',
        'Special Kids Training',
        'Tour & Travel Service',
        'Wild Animal Care',
        'Yoga Center'
    ]

    output = pd.DataFrame(columns=[
         'Sub Category',
         'Company / Business Name',
         'Direct Link to Company Website',
         'Products / Services',
        'Phone Number',
        'Email Address',
        'Physical Address',
        'Working Hours (Monday - Start)',
        'Working Hours (Monday - End)',
        'Working Hours (Tuesday - Start)',
        'Working Hours (Tuesday - End)',
        'Working Hours (Wednesday - Start)',
        'Working Hours (Wednesday - End)',
        'Working Hours (Thursday - Start)',
        'Working Hours (Thursday - End)',
        'Working Hours (Friday - Start)',
        'Working Hours (Friday - End)',
        'Working Hours (Saturday - Start)',
        'Working Hours (Saturday - End)',
        'Working Hours (Sunday - Start)',
        'Working Hours (Sunday - End)',
        'City',
        'Image / Logo',
        'Amenities and Features',
        'Company Description / About'
    ])

    url = 'https://www.yellowpages.co.za/search?what='

    for cat in cats:
        cat_link = url + cat.replace(' ', '+').replace('&', '%26')
        pages = ceil(get_pages(cat_link)/20)

        for page in range(1, pages+1):
            listing_link = cat_link + f'&p={page}'
            links = get_listings(listing_link)

            for link in links:
                link = 'https://www.yellowpages.co.za' + link.get('href')
                x = len(output)
                output.loc[x] = get_data(link, cat)
                print(output.loc[x])

        output.to_excel('Data 2.xlsx', index=None)

    return


if __name__ == '__main__':
    main()
