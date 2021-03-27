# -*- coding: utf-8 -*-

import time
import re
from selenium import webdriver
import requests
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from selenium.webdriver.chrome.options import Options
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_data(driver, df, url):
    link = url + ';overall'
    driver.get(link)

    WebDriverWait(driver, 120).until(lambda x: x.find_element_by_css_selector('table[class="head_to_head h2h_home"]'))
    time.sleep(10)

    page = bs(driver.page_source, 'html.parser')
    home = page.find('table', {'class': 'head_to_head h2h_home'}).find('tbody')
    away = page.find('table', {'class': 'head_to_head h2h_away'}).find('tbody')
    mutual = page.find('table', {'class': 'head_to_head h2h_mutual'})

    home_name = page.find('div', {'class': 'team-text tname-home'}).text.strip()
    away_name = page.find('div', {'class': 'team-text tname-away'}).text.strip()
    date = page.find('div', {'id': 'utime'}).text
    league = page.find('span', {'class': 'description__country'}).text

    count_home = 0
    count_away = 0
    count_mutual = 0
    
    scores_home = []
    scores_away = []
    scores_mutual = []

    sum_home = 0
    sum_away = 0
    sum_mut = 0

    for row in home.find_all('tr'):
        if len(row.find_all('td')) == 1:
            continue
        if count_home < 5:
            if row.find_all('td')[2].text.strip() == home_name:
                count_home += 1
                if row.find_all('td')[4].text.strip() == '-':
                    continue
                if row.find_all('td')[4].text.split(':')[0].strip() != '0':
                    scores_home.append(row.find_all('td')[4].text.split(':')[0].strip())
        else:
            break

    for row in away.find_all('tr'):
        if len(row.find_all('td')) == 1:
            continue
        if count_away < 5:
            if row.find_all('td')[3].text.strip() == away_name:
                count_away += 1
                if row.find_all('td')[4].text.strip() == '-':
                    continue
                if row.find_all('td')[4].text.split(':')[1].strip()[0] != '0':
                    scores_away.append(row.find_all('td')[4].text.split(':')[1].strip()[0])
        else:
            break

    for row in mutual.find('tbody').find_all('tr'):
        if len(row.find_all('td')) == 1:
            continue
        if count_mutual < 5:
            if row.find_all('td')[2].text.strip() == home_name:
                count_mutual += 1
                if row.find_all('td')[4].text.split(':')[0].strip() == '0' or row.find_all('td')[4].text.split(':')[1].strip()[0] == '0':
                    continue
                scores_mutual.append(row.find_all('td')[4].text.split(':'))
        else:
            break

    print(scores_home, scores_away, scores_mutual, link)

    for score in range(len(scores_home)):
        sum_home += int(scores_home[score])
         
    for score in range(len(scores_away)):
        sum_away += int(scores_away[score][0])

    if sum_home + sum_away < 15:
        return driver, df
        
    for score in range(len(scores_mutual)):
        sum_mut += int(scores_mutual[score][0]) + int(scores_mutual[score][1].strip()[0])

    if sum_mut < 15:
        return driver, df

    x = len(df)
    df.loc[x] = [home_name + ' v ' + away_name, home_name, away_name, league, scores_home, scores_away, sum_mut, date]
    print(df.loc[x])

    return driver, df

def to_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('puntingform.json', scope)
    client = gspread.authorize(creds)
    client.import_csv(client.open('Flashscore').id, open('Match Data.csv', 'r').read())

    return

def main():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    url = 'https://www.flashscore.com/'

    while True:
        df = pd.DataFrame(columns=['Match', 'Home', 'Away', 'League', 'Goals Home', 'Goals Away', 'H2H Goals', 'Date/Time'])
        driver = webdriver.Chrome('chromedriver.exe', options=options)
        driver.get(url)
        WebDriverWait(driver, 120).until(lambda x: x.find_element_by_css_selector('div[class="calendar__direction calendar__direction--tomorrow"]')).click()
        WebDriverWait(driver, 120).until(lambda x: x.find_element_by_css_selector('div[class="sportName soccer"]'))
        time.sleep(30)
        page = bs(driver.page_source, 'html.parser')
        links = page.find_all('div', {'id': re.compile('g_1_.*')})
        for x in range(0,len(links)):
            links[x] = 'https://www.flashscore.com/match/' + links[x].get('id').lstrip('g_1_') + '/#h2h'
            driver, df = get_data(driver, df, links[x])

        driver.quit()
        df.to_csv('Match Data.csv', index=None)
        to_sheets()
        print('Sleeping')
        time.sleep(21600)
    
    return

if __name__ == '__main__':
    main()