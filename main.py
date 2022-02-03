import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy import distance


URL = "https://autos.mercadolibre.com.ar/hasta-150000-km/desde-2013/suv-usada_PriceRange_0ARS-3500000ARS_ITEM*CONDITION_2230581_NoIndex_True_VEHICLE*BODY*TYPE_452759#applied_filter_id%3DVEHICLE_YEAR%26applied_filter_name%3DA%C3%B1o%26applied_filter_order%3D7%26applied_value_id%3D2013-*%26applied_value_name%3D2013-*%26applied_value_order%3D34%26applied_value_results%3DUNKNOWN_RESULTS%26is_custom%3Dtrue"

DOLAR_BLUE_HOY = float(216.50)
items_dict = []
geolocator = Nominatim(user_agent="ml_scraper")

def get_latitude_longitude(location: str) -> tuple:
    try:
        lat_long = geolocator.geocode('Argentina, ' + location.replace('-', ','))
        return (lat_long.latitude, lat_long.longitude)
    except:
        return None

def dict_to_csv_file(listate:list, csv_file: str) -> None:
    try:
        with open(csv_file, 'w') as csvfile:
            csvfile.write(",".join(listate[0].keys()) + "\n")
            for li in listate:
                csvfile.write(",".join(li.values())+"\n")
    except IOError:
        print("I/O error")

BRANDSEN_LAT_LONG = get_latitude_longitude("Coronel brandsen")


def main():
    page = 1
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    total_paginas = int(soup.find(class_="andes-pagination__page-count").text.split(" ")[-1])


    while next_url_html := soup.findAll(class_="andes-pagination__button--next"):
        for item in soup.findAll('li', class_='ui-search-layout__item'):
            moneda = item.find(class_='price-tag-symbol').text
            price = item.find(class_='price-tag-fraction').text.replace('.','')
            location = item.find(class_='ui-search-item__location').text
            distance_km = str(int(distance.distance(BRANDSEN_LAT_LONG, get_latitude_longitude(location)).kilometers))
            price_if_blue = str(int(float(price) * DOLAR_BLUE_HOY))

            items_dict.append(
                {
                    'title': item.find(class_='ui-search-item__title').text.replace(',', ' '),
                    'moneda': moneda,
                    'price': price,
                    'price_if_blue': price if not moneda == 'U$S' else price_if_blue,
                    'year': item.findAll(class_='ui-search-card-attributes__attribute')[0].text,
                    'km': item.findAll(class_='ui-search-card-attributes__attribute')[1].text.replace('Km', ''),
                    'location': location,
                    'distance': distance_km,
                    'link': item.find('a', class_='ui-search-link')['href'],
                    'page': page
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

# consulta el tiempo actual

