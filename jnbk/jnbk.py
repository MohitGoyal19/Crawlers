from bs4 import BeautifulSoup as bs
import pandas as pd
import requests

def get_data(url, output):
    page = bs(requests.get(url).text, 'html.parser')
    specifications = ' ^ '.join([title.text.strip().replace('\n', ' ') + '|' + field.text.strip().replace('\n', ' ') for title, field in zip(page.find('div', {'class': 'detail__specification'}).find_all('div', {'class': 'param-title'}), page.find('div', {'class': 'detail__specification'}).find_all('div', {'class': 'param-field'}))])
    alternatives = ' ^ '.join([alt.text.strip().replace('\n', ' ') for alt in page.find('div', {'class': 'detail__plate'}).find_all('a')])
    cross_refs = ' ^ '.join([ref.text.strip().replace('\n', ' ') for ref in page.find_all('div', {'class': 'detail__body'})[1].find_all('div', {'class': 'str'})])

    for model in range(len(page.find_all('div', {'class': 'model-title'}))):
        (make, car_model) = page.find_all('div', {'class': 'model-title'})[model].find('h3').text.strip().split('»')
        rows = page.find_all('div', {'class': 'model-body'})[model].find_all('tr')

        for row in rows:
            front_rotor = ' ^ '.join([rotor.text.strip() for rotor in row.find_all('td')[4].find_all('a')]) + ' | ' + ' | '.join([rotor.text.strip() for rotor in row.find_all('td')[4].find_all('span')])
            front_brake = ' ^ '.join([rotor.text.strip() for rotor in row.find_all('td')[5].find_all('a')]) + ' | ' + ' | '.join([rotor.text.strip() for rotor in row.find_all('td')[5].find_all('span')])
            rear_rotor = ' ^ '.join([rotor.text.strip() for rotor in row.find_all('td')[6].find_all('a')]) + ' | ' + ' | '.join([rotor.text.strip() for rotor in row.find_all('td')[6].find_all('span')])
            rear_brake = ' ^ '.join([rotor.text.strip() for rotor in row.find_all('td')[7].find_all('a')]) + ' | ' + ' | '.join([rotor.text.strip() for rotor in row.find_all('td')[7].find_all('span')])
            
            year_start, year_end = (2000+int(row.find_all('td')[0].text.strip().split('~')[0].split('.')[1]), 2000+int(row.find_all('td')[0].text.strip().split('~')[1].split('.')[1])) if len(row.find_all('td')[0].text.strip().split('~')) > 1 else (2000+int(row.find_all('td')[0].text.strip().split('~')[0].split('.')[1]), 2020)
            for year in range(year_start, year_end+1):
                x = len(output)
                output.loc[x] = {
                    'Break Id': url.split('/')[-1],
                    'Maker': make.strip(),
                    'Model': car_model.strip(),
                    'Year': year,
                    'Engine Vol': row.find_all('td')[1].text.strip(),
                    'Engine No': row.find_all('td')[2].text.strip(),
                    'Body': row.find_all('td')[3].text.strip(),
                    'Front Rotor': front_rotor.strip().strip('|') if len(front_rotor) > 3 else row.find_all('td')[4].text.strip(),
                    'Front Brake': front_brake.strip().strip('|') if len(front_brake) > 3 else row.find_all('td')[5].text.strip(),
                    'Rear Rotor': rear_rotor.strip().strip('|') if len(rear_rotor) > 3 else row.find_all('td')[6].text.strip(),
                    'Rear Brake': rear_brake.strip().strip('|') if len(rear_brake) > 3 else row.find_all('td')[7].text.strip(),
                    'Parking Shoe': row.find_all('td')[8].text.strip(),
                    'Specifications': specifications,
                    'Alternatives': alternatives,
                    'Cross References': cross_refs,
                    'Product Url': url,
                    'Image Url': page.find('img', {'alt': url.split('/')[-1]}).get('src')
                }
                print(output.loc[x])


    return output


def get_brakes(output, model):
    url = f'http://www.jnbk-brakes.com/application/get_applications/{model}/1'
    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }

    page = bs(requests.get(url, headers=headers).text, 'html.parser')

    links = [link.get('href') for link in page.find('table').find_all('a')]

    for link in links:
        output = get_data(link, output)

    return output


def get_models(output, make):
    url = f'http://www.jnbk-brakes.com/application/get_application_models/{make}/1/0'
    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }

    page = bs(requests.get(url, headers=headers).text, 'html.parser')
    models = [option.get('value').strip('\\').strip('"').strip('\\') for option in page.find_all('option')]

    for model in models:
        output = get_brakes(output, model)

    return output


def get_makes(output):
    url = 'http://www.jnbk-brakes.com/catalogue/cars'

    page = bs(requests.get(url).text, 'html.parser')

    makes = [option.get('value') for option in page.find('select', {'id', 'selBrand'}).find_all('option')]
    
    for make in makes:
        output = get_models(output, make)
        output.to_excel('JNBK.xlsx', index=None)
    
    return output
    

def main():
    output = pd.DataFrame(columns=[
        'Break Id',
        'Maker',
        'Model',
        'Year',
        'Engine Vol',
        'Engine No',
        'Body',
        'Front Rotor',
        'Front Brake',
        'Rear Rotor',
        'Rear Brake',
        'Parking Shoe',
        'Specifications',
        'Alternatives',
        'Cross References',
        'Product Url',
        'Image Url'
    ])

    #output = pd.read_excel('JNBK.xlsx')

    output = get_makes(output)

    return


if __name__ == '__main__':
    main()
