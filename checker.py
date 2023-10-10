import csv
import datetime
import os
from dataclasses import dataclass
from email.message import EmailMessage
from smtplib import SMTP

import requests
from bs4 import BeautifulSoup


@dataclass
class AgdItem:
    name: str
    url: str
    price: int = 0


agd_items = [
    AgdItem('odkurzacz', 'https://www.euro.com.pl/odkurzacze-pionowe/samsung-jet-90-premium-vs20r9048t3-ge.bhtml'),
    AgdItem('rafalek_white', 'https://www.euro.com.pl/odkurzacze-automatyczne/beko-vrr81214vw.bhtml'),
    AgdItem('rafalek_black', 'https://www.euro.com.pl/odkurzacze-automatyczne/beko-vrr80214vb.bhtml')
]

product_prices = {}


def log_agd_info(product_name, price, availability):
    timestamp = datetime.datetime.now()
    with open('agd_prices.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, product_name, price, availability])


def notify(subject, body, receiver):
    user = os.environ['EMAIL']
    password = os.environ['PASSWORD']

    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = receiver
    msg['from'] = user

    server = SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)

    try:
        server.sendmail(user, receiver, msg.as_string())
    finally:
        print(f'Message was send to {receiver}')
        server.quit()


def fetch_agd_prices():
    price_sum = 0
    for agd in agd_items:
        req = requests.get(agd.url)
        soup = BeautifulSoup(req.text, 'html.parser')
        prices = soup.find_all('span', 'price-template__large--total')
        actual_price = int(prices[0].text.replace(" ", ""))
        if agd.name == 'rafalek':
            actual_price = actual_price * 2
        price_sum = price_sum + actual_price
        print(f'{agd.name} have actual price of {actual_price}')
        available = is_available(soup)
        if available:
            notify(f'{agd.name} agd item is available now',
                   f'Item is available with {actual_price} price, under {agd.url} url',
                   os.environ['RECIPIENT'])
        log_agd_info(agd.name, actual_price, available)
    print(f'Sum of all agd items: {price_sum}')


def search_min_max_prices():
    with open('agd_prices.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            timestamp, agd_name, price, available = row
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


def is_available(soup: BeautifulSoup) -> bool:
    add_cart_button = soup.find('button', attrs={'data-test', 'add-product-to-the-cart'})
    return add_cart_button is not None


if __name__ == '__main__':
    fetch_agd_prices()
    search_min_max_prices()
    show_min_max_prices()
