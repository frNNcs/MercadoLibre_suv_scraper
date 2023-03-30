import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


URL = "https://listado.mercadolibre.com.ar/klipsch"

DOLAR_BLUE_HOY = "https://dolarhoy.com/cotizaciondolarblue"
items_dict = []


def dict_to_csv_file(listate: list, csv_file: str) -> None:
    try:
        with open(csv_file, 'w') as csvfile:
            csvfile.write(",".join(listate[0].keys()) + "\n")
            for li in listate:
                csvfile.write(",".join(li.values())+"\n")
    except IOError:
        print("I/O error")

def dolar_blue() -> float:
    response = requests.get(DOLAR_BLUE_HOY)
    soup = BeautifulSoup(response.text, "html.parser")
    soup.find(class_="tile is-parent is-8").find(class_="tile is-child").text
    last_price_usd = None  # Initialize to None in case no price is found
    for item in soup.findAll(class_='tile is-child'):
        try:
            price_usd = item.find(class_='value').text
            price_usd = str(price_usd).replace('$', '')
            last_price_usd = price_usd  # Update last_price_usd with the latest value

        except AttributeError:
            pass

    if last_price_usd is not None:  # Check if a price was found
        print("Sale price " + last_price_usd)
        return float(last_price_usd)
    else:
        print("No price found")
        return 0.0  # Return a default value if no price was found

def main():
    sale = str(dolar_blue())
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
            result_price = round(float(price) / float(sale), 2)

            items_dict.append(
                {
                    'title': title.text.replace(',', ''),
                    'price_usd': str(result_price),
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
