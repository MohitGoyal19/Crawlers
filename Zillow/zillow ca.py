# -*- coding: utf-8 -*-

import json
import pandas as pd
import requests

def get_data():
    url = 'https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22london%22%2C%22mapBounds%22%3A%7B%22west%22%3A-81.72232040039061%2C%22east%22%3A-80.77474959960936%2C%22south%22%3A42.56331873328158%2C%22north%22%3A43.33229186074362%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A792613%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%7D%2C%22isListVisible%22%3Atrue%7D&includeMap=true&includeList=false'
    homes = dict()

    with open('london_data.json', 'r') as f:
        homes = json.load(f)['searchResults']['mapResults']
    
    df = pd.DataFrame(columns=
                            ['ZPID',
                             'Street Address', 
                             'Zipcode', 
                             'City', 
                             'State', 
                             'Country', 
                             'Latitude', 
                             'Longitude', 
                             'Price', 
                             'Currency', 
                             'Bathrooms', 
                             'Bedrooms', 
                             'Living Area', 
                             'Type', 
                             'Status', 
                             'Featured', 
                             'Zillow Owned', 
                             'Image', 
                             'URL'
                        ])

    for home in homes:
        if not 'hdpData' in home.keys():
            continue

        obj = {
            'ZPID': home['hdpData']['homeInfo']['zpid'],
            'Street Address': home['hdpData']['homeInfo']['streetAddress'],
            'Zipcode': home['hdpData']['homeInfo']['zipcode'],
            'City': home['hdpData']['homeInfo']['city'],
            'State': home['hdpData']['homeInfo']['state'],
            'Country': home['hdpData']['homeInfo']['country'],
            'Latitude': home['hdpData']['homeInfo']['latitude'],
            'Longitude': home['hdpData']['homeInfo']['longitude'],
            'Price': home['hdpData']['homeInfo']['price'],
            'Currency': home['hdpData']['homeInfo']['currency'],
            'Bathrooms': home['hdpData']['homeInfo']['bathrooms'] if 'bathrooms' in home['hdpData']['homeInfo'].keys() else '',
            'Bedrooms': home['hdpData']['homeInfo']['bedrooms'] if 'bedrooms' in home['hdpData']['homeInfo'].keys() else '',
            'Living Area': str(home['hdpData']['homeInfo']['livingArea']) + ' sqft.' if 'livingArea' in home['hdpData']['homeInfo'].keys() else 'Not Available',
            'Type': home['hdpData']['homeInfo']['homeType'],
            'Status': home['hdpData']['homeInfo']['homeStatus'],
            'Featured': 'Yes' if home['hdpData']['homeInfo']['isFeatured'] == True else 'No',
            'Zillow Owned': 'Yes' if home['hdpData']['homeInfo']['isZillowOwned'] == True else 'No',
            'Image': home['hdpData']['homeInfo']['hiResImageLink'],
            'URL': 'https://www.zillow.com' + home['detailUrl']            
        }

        x = len(df)
        df.loc[x] = obj
        print(df.loc[x])
    
    df.to_excel('London_Data.xlsx', index=None)

    return

if __name__ == '__main__':
    get_data()