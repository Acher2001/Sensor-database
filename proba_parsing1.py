from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Функция для обработки товаров на странице
def process_products(page_source, file):
    soup = BeautifulSoup(page_source, 'html.parser')

    # Пытаемся найти все элементы с товаром
    product_divs = soup.find_all('div', {'field': 'link'})

    if not product_divs:
        file.write("На этой странице нет товаров\n")
        return

    for product_div in product_divs:
        product_name = product_div.text.strip()
        exists_tag = product_div.find_next_sibling('span', {'field': 'exists'})
        if exists_tag and "Товар в наличии" in exists_tag.text:
            price_span = product_div.find_next_sibling('div', {'class': 'price'})
            if price_span:
                price = price_span.text.strip()
            else:
                price = "Цена не указана"

            file.write("Название товара: {}\n".format(product_name))
            file.write("Наличие: {}\n".format(exists_tag.text.strip()))
            file.write("Цена: {}\n".format(price))
            file.write("-" * 50 + "\n")

# Настройка веб-драйвера Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

urls = [
    "https://www.xn--80ai9an.xn--p1ai/shop/550",
    "https://www.xn--80ai9an.xn--p1ai/shop/549",
    "https://www.xn--80ai9an.xn--p1ai/shop/467",
    "https://www.xn--80ai9an.xn--p1ai/shop/552"
]

# Создаем файл для записи результатов
with open("output.txt", "w", encoding="utf-8") as file:
    for url in urls:
        driver.get(url)
        file.write("Страница: {}\n".format(url))
        file.write("=" * 50 + "\n")

        # Даем время на загрузку динамического контента
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[field="link"]')))

        process_products(driver.page_source, file)
        file.write("\n")

# Завершаем сеанс браузера
driver.quit()
