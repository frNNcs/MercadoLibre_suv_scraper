import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


URL = "https://listado.mercadolibre.com.ar/klipsch"

DOLAR_BLUE_HOY = float(245.0)
items_dict = []


def dict_to_csv_file(listate: list, csv_file: str) -> None:
    try:
        with open(csv_file, 'w') as csvfile:
            csvfile.write(",".join(listate[0].keys()) + "\n")
            for li in listate:
                csvfile.write(",".join(li.values())+"\n")
    except IOError:
        print("I/O error")


def main():
    page = 1
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    total_paginas = int(
        soup.find(class_="andes-pagination__page-count").text.split(" ")[-1])

    while next_url_html := soup.findAll(class_="andes-pagination__button--next"):
        for item in soup.findAll('li', class_='ui-search-layout__item'):
            price = item.find(class_='price-tag-fraction').text.replace('.', '')
            title = item.find(class_='ui-search-item__title shops__item-title')
            link = item.find(class_='ui-search-link').get('href')
            items_dict.append(
                {
                    'title': title.text,
                    'price': str(price),
                    'link': link,
                }
            )

        response = requests.get(
            BeautifulSoup(
                str(next_url_html), "html.parser"
            ).find('a', href=True)['href']
        )
        soup = BeautifulSoup(response.text, "html.parser")
        page += 1
        print(f"Pagina {page} de {total_paginas}")

    dict_to_csv_file(items_dict, "items.csv")


if __name__ == '__main__':
    main()
