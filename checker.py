import csv
import datetime
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class AgdItem:
    name: str
    url: str
    price: int = 0


agd_class_items = [
    AgdItem('lodowka', 'https://www.euro.com.pl/lodowki/samsung-rb38t705cb.bhtml'),
    AgdItem('suszarka', 'https://www.euro.com.pl/suszarki/bosch-serie-6-wtw8760epl.bhtml'),
    AgdItem('ekspres', 'https://www.euro.com.pl/ekspresy-cisnieniowe/delonghi-dinamica-plus-ecam-370-70-b.bhtml'),
    AgdItem('indukcja', 'https://www.euro.com.pl/plyty-do-zabudowy/electrolux-eiv835.bhtml'),
    AgdItem('pralka', 'https://www.euro.com.pl/pralki/samsung-addwash-ww80t554dae.bhtml'),
    AgdItem('piekarnik', 'https://www.euro.com.pl/piekarniki-do-zabudowy/electrolux-coc8h31z.bhtml'),
    # AgdItem('odkurzacz', 'https://www.euro.com.pl/odkurzacze-pionowe/samsung-jet-90-premium-vs20r9048t3-ge.bhtml'),
    AgdItem('zmywarka', 'https://www.euro.com.pl/zmywarki-do-zabudowy/electrolux-zmywarka-eem48321l-electrolux.bhtml'),
    # AgdItem('rafalek', 'https://www.euro.com.pl/odkurzacze-automatyczne/beko-vrr81214vw.bhtml'),
    AgdItem('okap', 'https://www.euro.com.pl/okapy/electrolux-cfg516r.bhtml')
]

product_prices = {}


def log_price(product_name, price):
    timestamp = datetime.datetime.now()
    with open('agd_prices.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, product_name, price])


def fetch_agd_prices():
    price_sum = 0
    for agd in agd_class_items:
        req = requests.get(agd.url)
        soup = BeautifulSoup(req.text, 'html.parser')
        prices = soup.find_all('span', 'price-template__large--total')
        actual_price = int(prices[0].text.replace(" ", ""))
        if agd.name == 'rafalek':
            actual_price = actual_price * 2
        price_sum = price_sum + actual_price
        print(f'{agd.name} have actual price of {actual_price}')
        log_price(agd.name, actual_price)
    print(f'Sum of all agd items: {price_sum}')


def search_min_max_prices():
    with open('agd_prices.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            timestamp, agd_name, price = row
            price = int(price)

            if agd_name not in product_prices:
                product_prices[agd_name] = {'min_price': price, 'max_price': price}
            else:
                if price < product_prices[agd_name]['min_price']:
                    product_prices[agd_name]['min_price'] = price
                if price > product_prices[agd_name]['max_price']:
                    product_prices[agd_name]['max_price'] = price


def show_min_max_prices():
    for product_name, prices in product_prices.items():
        min_price = prices['min_price']
        max_price = prices['max_price']
        print(f"Product: {product_name}, Min Price: {min_price}, Max Price: {max_price}")


if __name__ == '__main__':
    fetch_agd_prices()
    search_min_max_prices()
    show_min_max_prices()
