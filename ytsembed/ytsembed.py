from bs4 import BeautifulSoup as bs
import pandas as pd
import requests

def parse(page):
    movies = page.find_all('div', {'class': 'browse-movie-bottom'})

    for movie in movies:
        movie_id = movie.find('a', {'class': 'browse-movie-title'}).get('onclick').rstrip('.submit()').lstrip('movs')
        data = {
            'id': movie_id
        }
        url = 'https://ytsembed.xyz/embed-page/'
        iframe = bs(requests.post(url, data=data).text, 'html.parser').find('div', {'id': 'movie-content'}).find('input').get('value')

        yield{
            'iframe src': iframe,
            'Name': movie.find('a', {'class': 'browse-movie-title'}).text.strip(),
            'Year': movie.find('div', {'class': 'browse-movie-year'}).text.strip(),
            'Language': movie.find('img').get('title').rstrip('Language').strip(),
        }


def get_pages(output):
    data = {
        'q': ':Latest:',
        'page': 1
    }

    url = 'https://ytsembed.xyz/search/:Latest:/page/'

    page_no = 1

    while True:
        data['page'] = page_no
        page = bs(requests.post(url+str(page_no), data=data).text, 'html.parser')
        movies = parse(page) 
        for movie in movies:
            x = len(output)
            output.loc[x] = movie
            print(x, movie)

        page_no += 1
        output.to_excel('Movies.xlsx', index=None)

    return output


def main():
    output = pd.DataFrame(columns=[
        'Name',
        'Year',
        'Language',
        'iframe src'
    ])

    output = get_pages(output)

    return


if __name__ == '__main__':
    main()
