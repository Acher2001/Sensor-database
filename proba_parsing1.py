# Импорт необходимых модулей и библиотек
import os
import requests
import hashlib
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pony.orm import *
import schedule
import time

# Определение базы данных с помощью PonyORM
db = Database()


# Определение сущности City (город) с помощью PonyORM
class City(db.Entity):
    name = Required(str)
    number = Required(int)
    shops = Set("Shop")


# Определение сущности Shop (магазин) с помощью PonyORM
class Shop(db.Entity):
    name = Required(str)
    number = Required(int)
    city = Required("City")
    website = Optional(str)
    address = Optional(str)
    products = Set("Product")


# Определение сущности Product (продукт) с помощью PonyORM
class Product(db.Entity):
    name = Required(str)
    number = Required(int)
    shop = Required("Shop")
    price = Required(float)
    image = Optional(str)
    product_page_link = Optional(str)
    application_example_link = Optional(str)


# Привязка базы данных к SQLite и создание таблиц при необходимости
db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


# Функция для парсинга данных и их сохранения в базу данных
@db_session
def parse_and_save_data(url, page_source):
    # Задание названия города, номера города, названия и номера магазина
    city_name = "Пермь"  # Укажите название города
    city_number = 1  # Укажите номер города
    shop_name = "Арду.рф"  # Укажите название магазина
    shop_number = 1  # Укажите номер магазина

    # Получение объекта города из базы данных или создание нового
    city = City.get(name=city_name, number=city_number)
    if not city:
        city = City(name=city_name, number=city_number)

    # Получение объекта магазина из базы данных или создание нового
    shop = Shop.get(name=shop_name, number=shop_number)
    if not shop:
        shop = Shop(name=shop_name, number=shop_number, city=city)

    # Инициализация парсера HTML страницы
    soup = BeautifulSoup(page_source, 'html.parser')

    # Получение списка div'ов с информацией о продуктах
    product_divs = soup.find_all('div', {'class': 'row product-row'})

    # Парсинг информации о продуктах и сохранение в базу данных
    for product_div in product_divs:
        img_div = product_div.find('div', {'field': 'picture'})
        product_name = product_div.find('div', {'field': 'link'}).find('a').text.strip()
        exists_tag = product_div.find('span', {'field': 'exists'})
        price = float(product_div.find('span', {'field': 'price'}).text.strip())

        # Добавление ссылки на товар
        product_link = urljoin(url, product_div.find('div', {'field': 'link'}).find('a')['href'])

        # Скачивание изображения товара, если оно есть
        if img_div and img_div.find('img'):
            img_url = urljoin(url, img_div.find('img')['src'])
            img_extension = os.path.splitext(img_url)[-1]
            img_filename = hashlib.md5(img_url.encode()).hexdigest() + img_extension
            img_path = os.path.join('images', img_filename)
            with open(img_path, 'wb') as img_file:
                img_file.write(requests.get(img_url).content)
        else:
            img_path = None

        # Создание объекта Product и сохранение в базу данных
        Product(name=product_name, number=1, shop=shop, price=price, image=img_path,
                product_page_link=product_link)


# Функция для обновления данных
def update_data():
    # Создание директории для сохранения изображений
    os.makedirs('images', exist_ok=True)
    for url in urls:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.row.product-row')))
        parse_and_save_data(url, driver.page_source)


# Настройка веб-драйвера Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Список URL-адресов для парсинга данных
urls = [
    "https://www.xn--80ai9an.xn--p1ai/shop/550",
    "https://www.xn--80ai9an.xn--p1ai/shop/549",
    "https://www.xn--80ai9an.xn--p1ai/shop/467",
    "https://www.xn--80ai9an.xn--p1ai/shop/552"
]

# Вызываем функцию обновления данных сразу, чтобы в начале скрипта данные были обновлены
update_data()

# Планирование выполнения функции обновления данных каждый час
schedule.every().hour.do(update_data)

# Бесконечный цикл для выполнения планированных задач
while True:
    schedule.run_pending()
    time.sleep(1)

# Завершаем сеанс браузера
driver.quit()
