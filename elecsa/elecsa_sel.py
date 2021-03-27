from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd
from time import sleep

def request(driver, count):
    url = 'http://www.elecsa.co.uk/Find-a-Contractor.aspx'

    driver.get(url)
    driver.get(driver.find_elements_by_tag_name('area')[count].get_attribute('href'))
    if driver.current_url != url:
        return driver, True
    else:
        return driver, False

def spider(df, driver):
    driver.find_element_by_css_selector('#ctl00_plcMain_searchResult_ucListView_lvCompanies_ddlResultsPerPage > option:nth-child(4)').click()

    sleep(8)

    page_source = bs(driver.page_source, 'html.parser')

    items = page_source.find_all('div', {'class': 'searchresultsitemtoprow'})

    for item in items:
        title = item.find('span').text.strip()
        print(title)
        data = item.find('div')
    
        website = data.find_all('a')[0].get('href').strip()
        print(website)
        if website == 'http://':
            website = ''

        email = data.find_all('a')[1].get('href').strip().lstrip('mailto:')
        print(email)
    
        contact = data.text.split('Mobile:')[1].split('Website')[0].strip()
        print(contact)

        df.loc[len(df)] = [title, contact, website, email]
        print(df.loc[len(df)-1])
    driver.quit()
    df.to_excel('elecsa.xlsx', index=None)

    return df

def main():
    df = pd.DataFrame(columns=['title', 'contact', 'website', 'email'])

    for i in range(11):
        driver = webdriver.Chrome('..\\chromedriver.exe')
        
        driver, data = request(driver, i)
        if not data:
            continue

        df = spider(df, driver)

if __name__ == '__main__':
    main()