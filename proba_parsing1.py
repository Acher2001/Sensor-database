import requests
from bs4 import BeautifulSoup

# Функция для парсинга данных с заданной ссылки
def parse_data(url):
    # Отправляем GET-запрос к указанной ссылке
    response = requests.get(url)

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Используем BeautifulSoup для парсинга HTML-кода страницы
        soup = BeautifulSoup(response.content, 'html.parser')

        # Находим блок с товарами на странице
        products_container = soup.find('div', class_='container')

        # Проверяем, найден ли блок с товарами
        if products_container:
            # Просматриваем информацию о каждом товаре
            for product in products_container.find_all('div', class_='col-6 col-md-4 col-lg-3 col-xl-2 mb-4'):
                # Получаем информацию о товаре (например, название и цену)
                name = product.find('a', class_='text-dark').text.strip()
                price = product.find('span', class_='price').text.strip()

                # Выводим информацию о товаре
                print("Название:", name)
                print("Цена:", price)
                print()
        else:
            print("Блок с товарами не найден на странице:", url)
    else:
        print("Ошибка при получении страницы:", response.status_code)

# Ссылки для парсинга данных
urls = [
    "https://www.xn--80ai9an.xn--p1ai/shop/550",
    "https://www.xn--80ai9an.xn--p1ai/shop/549",
    "https://www.xn--80ai9an.xn--p1ai/shop/467",
    "https://www.xn--80ai9an.xn--p1ai/shop/552"
]

# Парсим данные с каждой ссылки
for url in urls:
    print("Парсинг данных с", url)
    parse_data(url)
    print()
